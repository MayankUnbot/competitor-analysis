"""Normalize and structure raw competitor data into a comparison JSON.

This tool organizes raw data collected by web_search.py, scrape_website.py,
and scrape_reviews.py. The actual analysis/narrative is written by Claude
after reading this tool's structured output.
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone


def load_json_safe(path):
    """Load a JSON file, returning None on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError, UnicodeDecodeError):
        return None


def find_previous_analysis(output_dir):
    """Find the most recent previous analysis file for trend comparison."""
    pattern = os.path.join(output_dir, "analysis_output_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if files:
        return load_json_safe(files[0])
    return None


def structure_competitor(name, data_dir):
    """Structure all raw data for a single competitor."""
    competitor = {
        "name": name,
        "data_sources": [],
    }

    # Load search results
    search_path = os.path.join(data_dir, "search_results.json")
    search_data = load_json_safe(search_path)
    if search_data:
        competitor["search_results"] = search_data
        competitor["data_sources"].append("web_search")

    # Load website data
    website_path = os.path.join(data_dir, "website_data.json")
    website_data = load_json_safe(website_path)
    if website_data:
        competitor["website"] = {
            "title": website_data.get("title", ""),
            "description": website_data.get("meta_description", ""),
            "headings": website_data.get("headings", []),
            "content_preview": website_data.get("text_content", "")[:2000],
            "key_links": website_data.get("links", [])[:10],
        }
        competitor["data_sources"].append("website_scrape")

    # Load review data
    reviews_path = os.path.join(data_dir, "reviews.json")
    reviews_data = load_json_safe(reviews_path)
    if reviews_data:
        competitor["reviews"] = reviews_data
        competitor["data_sources"].append("reviews")

    # Load any additional data files
    for filepath in glob.glob(os.path.join(data_dir, "*.json")):
        basename = os.path.basename(filepath)
        if basename not in ("search_results.json", "website_data.json", "reviews.json"):
            extra = load_json_safe(filepath)
            if extra:
                key = os.path.splitext(basename)[0]
                competitor[key] = extra
                competitor["data_sources"].append(key)

    return competitor


def main():
    parser = argparse.ArgumentParser(description="Structure competitor data for analysis")
    parser.add_argument("--input_dir", required=True,
                        help="Path to .tmp/competitor_data/ directory")
    parser.add_argument("--business_profile", required=True,
                        help="Path to business_profile.json")
    parser.add_argument("--output", required=True,
                        help="Output path for analysis JSON")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(json.dumps({"error": f"Input directory not found: {args.input_dir}"}))
        sys.exit(1)

    business = load_json_safe(args.business_profile)
    if not business:
        print(json.dumps({"error": f"Could not load business profile: {args.business_profile}"}))
        sys.exit(1)

    # Find all competitor directories
    competitors = []
    for entry in sorted(os.listdir(args.input_dir)):
        entry_path = os.path.join(args.input_dir, entry)
        if os.path.isdir(entry_path):
            competitor = structure_competitor(entry, entry_path)
            if competitor["data_sources"]:  # Only include if we have data
                competitors.append(competitor)

    if not competitors:
        print(json.dumps({"error": "No competitor data found in input directory"}))
        sys.exit(1)

    # Check for previous analysis (trend tracking)
    output_dir = os.path.dirname(os.path.abspath(args.output))
    previous = find_previous_analysis(output_dir)

    # Build analysis output
    analysis = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "business_context": {
            "company": business.get("company_name", ""),
            "industry": business.get("industry", ""),
            "niche": business.get("niche", ""),
            "differentiators": business.get("differentiators", []),
        },
        "competitors": competitors,
        "competitor_count": len(competitors),
        "data_completeness": {
            c["name"]: len(c["data_sources"]) for c in competitors
        },
    }

    if previous:
        prev_names = {c["name"] for c in previous.get("competitors", [])}
        curr_names = {c["name"] for c in competitors}
        analysis["changes_since_last_run"] = {
            "previous_run": previous.get("generated_at", "unknown"),
            "new_competitors": list(curr_names - prev_names),
            "removed_competitors": list(prev_names - curr_names),
            "recurring_competitors": list(curr_names & prev_names),
        }

    # Save with timestamp for history
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    timestamped_path = os.path.join(output_dir, f"analysis_output_{timestamp}.json")

    # Write both the requested output and a timestamped copy
    for path in [args.output, timestamped_path]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": "success",
        "competitors_analyzed": len(competitors),
        "output_path": os.path.abspath(args.output),
        "timestamped_copy": os.path.abspath(timestamped_path),
        "has_trend_data": previous is not None,
    }, indent=2))


if __name__ == "__main__":
    main()
