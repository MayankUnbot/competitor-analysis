# Generate Reports

## Objective
Transform analysis data into branded PDF report and Google Slides deck.

## Required Inputs
- `.tmp/analysis_output.json` — structured competitor data
- `.tmp/narrative_sections.json` — Claude-written narrative text
- `.tmp/brand_config.json` — brand colors, fonts, logo path
- `.tmp/business_profile.json` — business context

## Process

### 1. Generate PDF Report
```
python tools/generate_pdf_report.py \
  --analysis .tmp/analysis_output.json \
  --brand_config .tmp/brand_config.json \
  --business_profile .tmp/business_profile.json \
  --narrative_sections .tmp/narrative_sections.json \
  --output .tmp/reports/competitor_analysis_{date}.pdf
```
Replace `{date}` with today's date (YYYY-MM-DD).

### 2. Generate Google Slides Deck
Requires Google OAuth to be set up (`credentials.json` + `token.json`).
```
python tools/generate_slides_deck.py \
  --analysis .tmp/analysis_output.json \
  --brand_config .tmp/brand_config.json \
  --business_profile .tmp/business_profile.json \
  --narrative_sections .tmp/narrative_sections.json \
  --title "Competitor Analysis"
```

### 3. Deliver to User
- Share the PDF file path
- Share the Google Slides URL
- If Google auth fails: deliver PDF only, ask user to set up OAuth for Slides

## Narrative Sections JSON Format
The `narrative_sections.json` must contain:
```json
{
  "executive_summary": "string — 3-5 paragraph overview",
  "competitor_profiles": {
    "CompetitorName": "string — analysis paragraph per competitor"
  },
  "feature_comparison": {
    "headers": ["Feature", "Competitor A", "Competitor B"],
    "rows": [["Feature 1", "Yes", "No"]]
  },
  "pricing_comparison": {
    "headers": ["Tier", "Competitor A", "Competitor B"],
    "rows": [["Free", "Yes", "No"]]
  },
  "recommendations": "string — actionable strategies",
  "market_trends": "string — market observations"
}
```
