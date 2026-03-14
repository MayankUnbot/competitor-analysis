"""Extract structured review data from review platforms."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv


def extract_via_tavily(url, api_key):
    """Use Tavily's extract endpoint to pull review content."""
    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)
    response = client.extract(urls=[url])

    results = response.get("results", [])
    if not results:
        return None

    return results[0].get("raw_content", "")


def extract_via_browser(url):
    """Fallback: use Playwright to scrape review page."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000, wait_until="networkidle")

        content = page.evaluate("""() => {
            const elements = document.querySelectorAll(
                '[class*="review"], [class*="rating"], [class*="testimonial"], '
                + '[data-testid*="review"], .review-content, .rating-summary, '
                + 'h1, h2, h3, p'
            );
            return Array.from(elements).map(el => el.textContent.trim()).filter(t => t).join('\\n');
        }""")

        browser.close()

    return content[:10000] if content else None


def main():
    parser = argparse.ArgumentParser(description="Extract review data from review platforms")
    parser.add_argument("--url", required=True, help="Review page URL")
    parser.add_argument("--platform", choices=["g2", "capterra", "trustpilot", "google_maps", "other"],
                        default="other", help="Review platform")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")

    raw_content = None
    extraction_method = None

    # Try Tavily extract first
    if api_key:
        try:
            raw_content = extract_via_tavily(args.url, api_key)
            if raw_content:
                extraction_method = "tavily_extract"
        except Exception as e:
            print(json.dumps({"warning": f"Tavily extract failed: {e}"}), file=sys.stderr)

    # Fallback to browser scraping
    if not raw_content:
        try:
            raw_content = extract_via_browser(args.url)
            if raw_content:
                extraction_method = "playwright"
        except Exception as e:
            print(json.dumps({"warning": f"Browser scraping failed: {e}"}), file=sys.stderr)

    if not raw_content:
        print(json.dumps({
            "error": "Could not extract review content from this URL",
            "url": args.url,
            "platform": args.platform,
        }))
        sys.exit(1)

    # Output raw content for Claude to analyze and structure
    result = {
        "url": args.url,
        "platform": args.platform,
        "extraction_method": extraction_method,
        "raw_content": raw_content[:15000],  # Cap at 15k chars
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
