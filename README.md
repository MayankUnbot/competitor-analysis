# Competitor Analysis — WAT Framework

An automated competitor analysis system built on the **WAT (Workflows, Agents, Tools)** architecture. It researches competitors, analyzes their positioning, and delivers branded PDF reports + Google Slides decks.

## How It Works

The framework separates concerns into three layers:

- **Workflows** — Markdown SOPs in `workflows/` that define objectives, inputs, tools to use, and edge cases
- **Agents** — AI handles reasoning, orchestration, and decision-making
- **Tools** — Python scripts in `tools/` handle deterministic execution (API calls, scraping, report generation)

This separation keeps AI focused on what it's good at (reasoning) while reliable scripts handle execution.

## Project Structure

```
workflows/          # Step-by-step instructions (Markdown SOPs)
tools/              # Python scripts for execution
assets/             # Brand assets (logo, fonts)
.tmp/               # Temporary/intermediate files (gitignored)
.env                # API keys (gitignored)
```

## Workflows

| Workflow | Description |
|----------|-------------|
| `competitor_analysis.md` | Main entry point — orchestrates the full analysis pipeline |
| `gather_competitor_data.md` | Web search, website scraping, and review extraction per competitor |
| `generate_reports.md` | Transforms analysis data into branded PDF + Google Slides |
| `setup_business_profile.md` | Collects your business context (industry, niche, differentiators) |
| `setup_brand_assets.md` | Collects brand assets (logo, colors, fonts) for report styling |

## Tools

| Tool | Description |
|------|-------------|
| `web_search.py` | Search the web via Tavily API |
| `scrape_website.py` | Scrape websites using BeautifulSoup or Playwright |
| `scrape_reviews.py` | Extract reviews from review platforms |
| `analyze_competitors.py` | Normalize and structure raw competitor data into JSON |
| `generate_pdf_report.py` | Generate branded PDF reports using fpdf2 |
| `generate_slides_deck.py` | Create branded Google Slides decks via Google Slides API |
| `save_json.py` | Utility to save structured data to JSON |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

**Required keys:**
- `TAVILY_API_KEY` — for web search and content extraction
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — for Google Slides integration

### 3. Install Playwright (for JS-heavy sites)

```bash
playwright install
```

## Usage

This project is designed to be run with an AI agent (like Claude Code). Point the agent at `workflows/competitor_analysis.md` and provide:

1. Your business context (company name, industry, what you do)
2. Competitors to analyze (or let the agent discover them)
3. Brand assets for report styling (optional)

The agent will orchestrate the tools, gather data, analyze it, and deliver a branded PDF report + Google Slides deck.

## Architecture Principle

> When AI tries to handle every step directly, accuracy drops fast. Five steps at 90% each = 59% overall. By offloading execution to deterministic scripts, the AI stays focused on orchestration and decision-making.

The system also self-improves: when something breaks, the tool gets fixed, the fix is verified, and the workflow is updated so it doesn't happen again.
