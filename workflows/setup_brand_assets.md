# Setup Brand Assets

## Objective
Collect and persist brand assets (logo, colors, fonts) for report generation.

## Required Inputs
- Logo file (PNG or JPEG) — copy to `assets/logo.jpeg` (or `.png`)
- Brand colors as hex codes: primary, secondary, accent, background, text
- Font names for headings and body text
- Font files (TTF) if using custom fonts — place in `assets/fonts/`

## Process
1. Ask the user for logo file path → copy to `assets/`
2. Ask for hex color codes → validate they're proper hex format
3. Ask for font preferences → check if TTF files exist in `assets/fonts/`
4. Save config:
```
python tools/save_json.py --data '{
  "company_name": "...",
  "logo_path": "assets/logo.jpeg",
  "colors": {"primary": "#...", "secondary": "#...", "accent": "#...", "background": "#...", "text": "#..."},
  "fonts": {
    "heading": {"name": "FontName", "file": "assets/fonts/Font.ttf"},
    "body": {"name": "FontName", "file": "assets/fonts/Font.ttf"}
  }
}' --output .tmp/brand_config.json
```

## Font Fallback
If custom font TTF files are not available, the PDF generator falls back to Helvetica. Note this to the user so they know the report won't have custom typography.

## Current Config
If `.tmp/brand_config.json` already exists, read it first and ask what to update.
