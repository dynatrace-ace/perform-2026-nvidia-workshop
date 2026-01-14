"""Custom actions for NeMo Guardrails."""

import re
from typing import Optional


def check_jailbreak(context: Optional[dict] = None) -> bool:
    """Check if user input contains jailbreak attempts.
    
    Args:
        context: Context dictionary containing user_input
        
    Returns:
        True if jailbreak attempt detected, False otherwise
    """
    if not context:
        return False
    
    # NeMo Guardrails passes user_message
    user_input = context.get("user_message", "") or context.get("last_user_message", "")
    if not user_input:
        return False
    
    user_input = user_input.lower()
    
    # Define jailbreak patterns
    jailbreak_patterns = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
        r"disregard\s+(all\s+)?(previous|prior|above)",
        r"forget\s+(all\s+)?(previous|prior|above)",
        r"pretend\s+(you\s+are|to\s+be)",
        r"roleplay\s+as",
        r"act\s+as\s+(if\s+)?you",
        r"simulate\s+(being|that\s+you)",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"bypass\s+(your\s+)?(safety|guidelines|rules|restrictions)",
        r"override\s+(your\s+)?(safety|guidelines|rules|restrictions)",
    ]
    
    for pattern in jailbreak_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True
    
    return False


def check_blocked_terms(context: Optional[dict] = None) -> bool:
    """Check if text contains blocked or inappropriate terms.
    
    Args:
        context: Context dictionary containing user_input or bot_response
        
    Returns:
        True if blocked terms found, False otherwise
    """
    if not context:
        return False
    
    # Check both user input and bot response
    user_text = context.get("user_message", "") or context.get("last_user_message", "") or ""
    bot_text = context.get("bot_message", "") or context.get("last_bot_message", "") or ""
    text = (user_text + " " + bot_text).lower()
    
    # Define blocked term categories - harmful/dangerous content
    blocked_terms = [
        # Cybersecurity threats
        "hack",
        "exploit",
        "bypass",
        "malware",
        "virus",
        # Weapons and violence
        "bomb",
        "explosive",
        "weapon",
        "gun",
        "ammunition",
        "grenade",
        "missile",
        # Violence and harm
        "kill",
        "murder",
        "assassinate",
        "torture",
        "poison",
        "suicide",
        # Illegal activities
        "illegal",
        "smuggle",
        "counterfeit",
        "fraud",
        "scam",
        # Drugs
        "cocaine",
        "heroin",
        "methamphetamine",
        "fentanyl",
    ]
    
    for term in blocked_terms:
        if term in text:
            return True
    
    return False


def check_input_length(context: Optional[dict] = None) -> bool:
    """Check if user input exceeds maximum length.
    
    Args:
        context: Context dictionary containing user_input
        
    Returns:
        True if input too long, False otherwise
    """
    if not context:
        return False
    
    user_input = context.get("user_message", "") or context.get("last_user_message", "")
    if not user_input:
        return False
    max_length = 2000  # Maximum characters
    
    return len(user_input) > max_length


def check_politics(context: Optional[dict] = None) -> bool:
    """Check if user input contains political content.
    
    Args:
        context: Context dictionary containing user_input
        
    Returns:
        True if political content detected, False otherwise
    """
    if not context:
        return False
    
    user_input = context.get("user_message", "") or context.get("last_user_message", "")
    if not user_input:
        return False
    
    user_input = user_input.lower()
    
    # Political terms and figures to block
    political_terms = [
        # US Political figures
        "trump",
        "donald trump",
        "biden",
        "joe biden",
        "obama",
        "clinton",
        "hillary",
        # Political parties
        "republican",
        "democrat",
        "gop",
        "maga",
        # Political topics
        "politics",
        "political",
        "election",
        "vote",
        "voting",
        "congress",
        "senate",
        "president",
        "presidential",
        "white house",
        "capitol",
        "impeach",
    ]
    
    # Check for blocked political terms
    for term in political_terms:
        if term in user_input:
            return True
    
    return False


def check_input_topic(context: Optional[dict] = None) -> bool:
    """Check if user input is on topic.
    
    Args:
        context: Context dictionary containing user_input
        
    Returns:
        True if input is off-topic, False if on-topic
    """
    if not context:
        return False
    
    user_input = context.get("user_message", "") or context.get("last_user_message", "")
    if not user_input:
        return False
    
    user_input = user_input.lower()
    
    # Keywords that indicate the question is on topic
    topic_keywords = [
        "dynatrace",
        "observability",
        "monitoring",
        "apm",
        "application performance",
        "tracing",
        "logs",
        "metrics",
        "oneagent",
        "activegate",
        "davis",
        "rum",
        "synthetic",
        "infrastructure",
        "kubernetes",
        "opentelemetry",
        "grail",
    ]
    
    # If any topic keyword is in the input, it's on-topic
    if any(keyword in user_input for keyword in topic_keywords):
        return False  # Not off-topic
    
    # Check for clearly off-topic patterns
    off_topic_patterns = [
        r"\b(weather|temperature|forecast)\b",
        r"\b(cook|recipe|food|restaurant)\b",
        r"\b(sports|game|match|score)\b",
        r"\b(movie|film|actor|actress)\b",
        r"\b(music|song|album|artist)\b",
        r"\b(news|politics|election)\b",
        r"\b(car|vehicle|drive|engine)\b",
        r"\b(health|medical|doctor|medicine)\b",
    ]
    
    for pattern in off_topic_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True  # Off-topic detected
    
    # Default to allowing if not clearly off-topic
    return False


def check_output_relevance(context: Optional[dict] = None) -> bool:
    """Check if bot response is relevant on topic.
    
    Args:
        context: Context dictionary containing user_input and bot_response
        
    Returns:
        True if response is off-topic, False otherwise
    """
    if not context:
        return False
    
    # NeMo Guardrails passes bot_message or last_bot_message
    bot_response = context.get("bot_message", "") or context.get("last_bot_message", "")
    if not bot_response:
        return False
        
    bot_response = bot_response.lower()
    
    # Keywords that indicate relevance on topic
    relevant_keywords = [
        "dynatrace",
        "observability",
        "monitoring",
        "apm",
        "tracing",
        "logs",
        "metrics",
        "oneagent",
        "activegate",
        "davis",
        "kubernetes",
        "opentelemetry",
        "observability",
        "debugging",
        "evaluation",
        "llm",
        "agent",
    ]
    
    # Check if any relevant keyword is in the response
    has_relevant_content = any(keyword in bot_response for keyword in relevant_keywords)
    
    # If no relevant content found, it's likely off-topic
    return not has_relevant_content

