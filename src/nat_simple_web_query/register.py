import logging
import os

from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.component_ref import EmbedderRef
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


# Tavily Web Search Tool Configuration
class TavilySearchToolConfig(FunctionBaseConfig, name="tavily_search"):
    description: str = "Search the web for current information"
    max_results: int = 5


@register_function(config_type=TavilySearchToolConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def tavily_search_tool(config: TavilySearchToolConfig, builder: Builder):
    from langchain_tavily import TavilySearch

    logger.info("Initializing Tavily web search tool")
    
    # Tavily API key should be set via TAVILY_API_KEY environment variable
    tavily_tool = TavilySearch(
        max_results=config.max_results,
        topic="general",
    )

    async def _search(query: str) -> str:
        """Search the web for information."""
        result = await tavily_tool.ainvoke({"query": query})
        return str(result)

    yield FunctionInfo.from_fn(_search, description=config.description)


# Original Webpage Query Tool Configuration
class WebQueryToolConfig(FunctionBaseConfig, name="webpage_query"):
    webpage_url: str
    description: str
    chunk_size: int = 1024
    embedder_name: EmbedderRef = "nvidia/nv-embedqa-e5-v5"


@register_function(config_type=WebQueryToolConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def webquery_tool(config: WebQueryToolConfig, builder: Builder):
    from langchain.tools.retriever import create_retriever_tool
    from langchain_community.document_loaders import WebBaseLoader
    from langchain_community.vectorstores import USearch
    from langchain_core.embeddings import Embeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    logger.info("Generating docs for the webpage: %s", config.webpage_url)

    embeddings: Embeddings = await builder.get_embedder(config.embedder_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)

    loader = WebBaseLoader(config.webpage_url)

    # Cant use `aload` because its implemented incorrectly and is not async
    docs = [document async for document in loader.alazy_load()]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=config.chunk_size)
    documents = text_splitter.split_documents(docs)
    vector = await USearch.afrom_documents(documents, embeddings)

    retriever = vector.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "webpage_search",
        config.description,
    )

    async def _inner(query: str) -> str:
        return await retriever_tool.arun(query)

    yield FunctionInfo.from_fn(_inner, description=config.description)