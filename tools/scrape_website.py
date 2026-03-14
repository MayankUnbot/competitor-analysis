"""Scrape a single URL and extract structured text content."""

import argparse
import json
import sys
from datetime import datetime, timezone


def scrape_static(url, selectors=None):
    """Scrape using requests + BeautifulSoup (fast, no JS)."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    # Extract targeted content if selectors provided
    if selectors:
        targeted = {}
        for name, sel in selectors.items():
            elements = soup.select(sel)
            targeted[name] = [el.get_text(strip=True) for el in elements]
        return targeted

    # General extraction
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    headings = []
    for level in range(1, 4):
        for h in soup.find_all(f"h{level}"):
            text = h.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    text_content = "\n".join(paragraphs[:50])  # Limit to first 50 paragraphs

    links = []
    for a in soup.find_all("a", href=True)[:30]:
        href = a["href"]
        link_text = a.get_text(strip=True)
        if href.startswith("http") and link_text:
            links.append({"text": link_text, "url": href})

    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "text_content": text_content,
        "links": links,
    }


def scrape_browser(url):
    """Scrape using Playwright for JS-heavy sites."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000, wait_until="networkidle")

        title = page.title()
        content = page.evaluate("""() => {
            const elements = document.querySelectorAll('h1, h2, h3, p, li');
            return Array.from(elements).map(el => el.textContent.trim()).filter(t => t).join('\\n');
        }""")

        browser.close()

    return {
        "title": title,
        "text_content": content[:5000],
        "headings": [],
        "links": [],
        "meta_description": "",
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape a web page")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--selectors", help="JSON object of {name: css_selector} for targeted extraction")
    parser.add_argument("--use_browser", action="store_true", help="Use Playwright for JS-heavy sites")
    args = parser.parse_args()

    selectors = None
    if args.selectors:
        try:
            selectors = json.loads(args.selectors)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON for --selectors"}))
            sys.exit(1)

    try:
        if args.use_browser:
            data = scrape_browser(args.url)
        else:
            data = scrape_static(args.url, selectors)

        result = {
            "url": args.url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            **data,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "url": args.url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
