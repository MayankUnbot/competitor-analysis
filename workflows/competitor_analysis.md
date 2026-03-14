# Competitor Analysis Workflow

## Objective
Research competitors in Mayank's niche (tech/coding-to-business content creators), analyze their positioning, and deliver a branded PDF report + Google Slides deck.

## Required Inputs
- List of competitor names or URLs (or ask the user, or auto-discover via search)
- Analysis scope: content strategy, audience growth, monetization, positioning, features, pricing (varies by competitor type)

## Prerequisites
Before running, confirm these exist:
1. **Business profile**: `.tmp/business_profile.json` — if missing, follow `workflows/setup_business_profile.md`
2. **Brand config**: `.tmp/brand_config.json` — if missing, follow `workflows/setup_brand_assets.md`
3. **API keys**: `.env` must contain `TAVILY_API_KEY`
4. **Dependencies**: `pip install -r requirements.txt` must have been run

## Execution Steps

### Step 1: Identify Competitors
If the user provides specific competitors, use those. Otherwise, run discovery:
```
python tools/web_search.py --query "top tech content creators coding to business" --num_results 10
python tools/web_search.py --query "developers turned entrepreneurs youtube channels" --num_results 10
```
Confirm the competitor list with the user before proceeding.

### Step 2: Gather Data (per competitor)
Follow `workflows/gather_competitor_data.md` for each competitor. This produces:
- `.tmp/competitor_data/{competitor_name}/search_results.json`
- `.tmp/competitor_data/{competitor_name}/website_data.json`
- `.tmp/competitor_data/{competitor_name}/reviews.json` (if applicable)

### Step 3: Structure & Analyze
```
python tools/analyze_competitors.py \
  --input_dir .tmp/competitor_data/ \
  --business_profile .tmp/business_profile.json \
  --output .tmp/analysis_output.json
```
This normalizes all raw data and detects changes from previous runs.

### Step 4: Write Narrative Sections
Read `.tmp/analysis_output.json` and write:
- **executive_summary**: 3-5 paragraph overview of competitive landscape
- **competitor_profiles**: per-competitor analysis (strengths, weaknesses, strategy, what Mayank can learn)
- **feature_comparison**: `{headers: [...], rows: [[...]]}` table structure
- **pricing_comparison**: `{headers: [...], rows: [[...]]}` table structure (if applicable)
- **recommendations**: actionable strategies for Code2Commerce
- **market_trends**: observations about the niche

Save to `.tmp/narrative_sections.json` using:
```
python tools/save_json.py --data '{...}' --output .tmp/narrative_sections.json
```

### Step 5: Generate Reports
Follow `workflows/generate_reports.md` to produce both PDF and Google Slides.

### Step 6: Deliver
- Share the PDF file path with the user
- Share the Google Slides URL
- Highlight 3 key takeaways from the analysis

## Repeatability
- Run monthly to track competitor changes
- Previous data is auto-archived with timestamps
- The analysis tool compares against the last run and flags changes
- When re-running, skip Steps 1-2 if data was recently gathered (within the same week)

## Error Handling
- If a competitor's website blocks scraping: use search snippet data instead, note the limitation
- If Tavily API limit is reached: use partial results, inform the user
- If Google OAuth fails: generate PDF only, ask user to re-authenticate for Slides
- If a paid API call is needed: ask the user before executing
