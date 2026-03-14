"""Search the web using Tavily API and return structured results."""

import argparse
import json
import os
import sys

from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Web search via Tavily API")
    parser.add_argument("--query", required=True, help="Search query string")
    parser.add_argument("--num_results", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--search_type", choices=["general", "news"], default="general",
                        help="Type of search (default: general)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print(json.dumps({"error": "TAVILY_API_KEY not found in .env"}))
        sys.exit(1)

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=args.query,
            max_results=args.num_results,
            search_depth="advanced",
            topic=args.search_type,
            include_raw_content=False,
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
                "score": r.get("score", 0),
            })

        print(json.dumps({
            "query": args.query,
            "num_results": len(results),
            "results": results,
        }, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e), "query": args.query}))
        sys.exit(1)


if __name__ == "__main__":
    main()
