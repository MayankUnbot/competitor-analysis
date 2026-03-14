# Gather Competitor Data

## Objective
For a single competitor, gather all available intelligence using search and scraping tools.

## Required Inputs
- Competitor name
- Competitor URL (optional — search for it if not provided)

## Process

### 1. Web Search
Run multiple targeted searches:
```
python tools/web_search.py --query "{competitor_name} content creator" --num_results 10
python tools/web_search.py --query "{competitor_name} pricing revenue monetization" --num_results 5
python tools/web_search.py --query "{competitor_name} reviews audience" --num_results 5
```
Save combined results:
```
python tools/save_json.py --data '{...}' --output .tmp/competitor_data/{competitor_name}/search_results.json
```

### 2. Website Scrape
If a website URL is available (found via search or provided):
```
python tools/scrape_website.py --url "https://..."
```
If the page returns empty/minimal content, retry with browser:
```
python tools/scrape_website.py --url "https://..." --use_browser
```
Save:
```
python tools/save_json.py --data '{...}' --output .tmp/competitor_data/{competitor_name}/website_data.json
```

### 3. Review/Social Scrape (if applicable)
If review pages are found in search results:
```
python tools/scrape_reviews.py --url "https://..." --platform g2
```
Save:
```
python tools/save_json.py --data '{...}' --output .tmp/competitor_data/{competitor_name}/reviews.json
```

## Error Handling
- If a site blocks scraping (403/429): fall back to search snippet data. Note this in the output.
- If the competitor has no website: use search results only. This is fine.
- Never hard-fail. Always save whatever data was collected.

## Output
Each competitor gets a directory: `.tmp/competitor_data/{competitor_name}/`
Files within are timestamped on subsequent runs for trend tracking.
