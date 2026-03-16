"""
Browser script to automate prompt submission against the Streamlit app.
Submits each prompt twice: once without guardrails, once with guardrails.

Prerequisites:
    pip install playwright
    playwright install chromium                     # macOS 
    playwright install --with-deps                  # Linux (recommended)

Usage Examples:
    python run_prompts.py                           # headless, 1 loop, 30s delay
    python run_prompts.py --url http://host:8501/   # required: app URL
    python run_prompts.py --withbrowser             # visible browser window
    python run_prompts.py --loops 5                 # run 5 loops
    python run_prompts.py --loops 0                 # run endlessly (Ctrl+C to stop)
    python run_prompts.py --delay 10                # 10 second delay between requests

All output is logged to both the console and run_prompts.log (overwritten each run).
"""

import argparse
import asyncio
import logging
import sys
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Logging – output to both console and run_prompts.log
# ---------------------------------------------------------------------------
LOG_FILE = "run_prompts.log"

logger = logging.getLogger("run_prompts")
logger.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

_file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
_file_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
logger.addHandler(_console_handler)


def log(msg: str = ""):
    """Log a message to both console and log file."""
    logger.info(msg)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROMPTS = [
    "What is the weather in New York?",
    "Tell me about NVIDIA GPUs",
    "How does Dynatrace monitor AI workloads?",
]

OPTION_WITHOUT_GUARDRAILS = "Without NeMo Guardrails"
OPTION_WITH_GUARDRAILS = "With NeMo Guardrails"

# Timeout (ms) to wait for the app to finish processing a query
PROCESSING_TIMEOUT = 120_000  # 2 minutes

# Default delay (seconds) between requests
DEFAULT_DELAY = 30


async def wait_for_processing_complete(page, timeout=PROCESSING_TIMEOUT):
    """Wait until Streamlit is no longer in a 'running' state."""
    # Streamlit shows a status indicator while running; wait for it to disappear.
    try:
        # Wait for the running indicator to appear (short timeout – it may already be gone)
        await page.wait_for_selector(
            '[data-testid="stStatusWidget"]', timeout=5000
        )
    except Exception:
        pass  # It may have already finished

    # Now wait for it to disappear, meaning processing is done
    try:
        await page.wait_for_selector(
            '[data-testid="stStatusWidget"]', state="hidden", timeout=timeout
        )
    except Exception:
        print("  ⚠  Timed out waiting for processing to complete")


async def submit_prompt(page, prompt: str, guardrail_option: str):
    """Fill in the prompt, select the guardrail option, and click Submit."""
    log(f"  → Option: {guardrail_option}")
    log(f"    Prompt: {prompt[:80]}{'…' if len(prompt) > 80 else ''}")

    # --- Clear and fill the text area ---
    textarea = page.locator("textarea").first
    await textarea.click()
    await textarea.fill("")
    await textarea.fill(prompt)
    # Small pause so Streamlit registers the change
    await asyncio.sleep(0.5)

    # --- Select the guardrail dropdown option ---
    # Streamlit selectbox is rendered as a div; click it then pick the option
    selectbox = page.locator('[data-testid="stSelectbox"]').first
    await selectbox.click()
    await asyncio.sleep(0.3)

    # Click the matching option in the dropdown list
    option_el = page.locator(
        f'[data-testid="stSelectboxVirtualDropdown"] [role="option"]:has-text("{guardrail_option}")'
    )
    await option_el.click()
    await asyncio.sleep(0.3)

    # --- Click Submit ---
    submit_btn = page.get_by_role("button", name="Submit Query")
    await submit_btn.click()

    # --- Wait for result ---
    await wait_for_processing_complete(page)
    log("    ✓ Done")


async def main(headless: bool = True, loops: int = 1, delay: int = DEFAULT_DELAY, url: str = ""):
    endless = loops == 0
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        log(f"Opening {url} …")
        await page.goto(url, wait_until="networkidle", timeout=60_000)
        # Give Streamlit extra time to fully hydrate
        await asyncio.sleep(3)
        log("Page loaded.")
        log(f"Loops: {'endless' if endless else loops} | Delay: {delay}s\n")

        loop_num = 0
        while True:
            loop_num += 1
            if endless:
                log(f"=== Loop {loop_num} (endless) ===")
            else:
                log(f"=== Loop {loop_num}/{loops} ===")

            for idx, prompt in enumerate(PROMPTS, start=1):
                log(f"  [{idx}/{len(PROMPTS)}] Processing prompt …")

                # First run: WITHOUT guardrails
                await submit_prompt(page, prompt, OPTION_WITHOUT_GUARDRAILS)

                # Delay between requests
                log(f"    Waiting {delay}s …")
                await asyncio.sleep(delay)

                # Second run: WITH guardrails
                await submit_prompt(page, prompt, OPTION_WITH_GUARDRAILS)

                # Delay between prompts (skip on very last prompt of last loop)
                is_last_loop = not endless and loop_num >= loops
                is_last_prompt = idx == len(PROMPTS)
                if not (is_last_loop and is_last_prompt):
                    log(f"    Waiting {delay}s …")
                    await asyncio.sleep(delay)

            if is_last_loop:
                break

        log("\nAll prompts submitted. Closing browser.")
        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate prompt submission to Streamlit app")
    parser.add_argument("--withbrowser", action="store_true", help="Run with a visible browser window")
    parser.add_argument("--loops", type=int, default=1, help="Number of loops (0 = endless, default: 1)")
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY, help=f"Delay in seconds between requests (default: {DEFAULT_DELAY})")
    parser.add_argument("--url", type=str, required=True, help="Streamlit app URL (e.g. http://host:8501/)")
    args = parser.parse_args()
    try:
        asyncio.run(main(headless=not args.withbrowser, loops=args.loops, delay=args.delay, url=args.url))
    except KeyboardInterrupt:
        log("\nInterrupted by user. Exiting.")
