"""Generate a branded PDF competitor analysis report using fpdf2."""

import argparse
import json
import os
import sys
from datetime import datetime


def hex_to_rgb(hex_color):
    """Convert hex color string to (r, g, b) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class BrandedReport:
    def __init__(self, brand_config, business_profile):
        from fpdf import FPDF

        self.brand = brand_config
        self.business = business_profile
        self.colors = {k: hex_to_rgb(v) for k, v in brand_config["colors"].items()}

        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=20)

        # Register custom fonts
        heading_font = brand_config["fonts"]["heading"]
        body_font = brand_config["fonts"]["body"]

        if os.path.exists(heading_font["file"]):
            self.pdf.add_font(heading_font["name"], "", heading_font["file"], )
            self.heading_font = heading_font["name"]
        else:
            self.heading_font = "Helvetica"

        if os.path.exists(body_font["file"]):
            self.pdf.add_font(body_font["name"], "", body_font["file"], )
            self.body_font = body_font["name"]
        else:
            self.body_font = "Helvetica"

    def _set_bg(self):
        """Fill page with background color."""
        r, g, b = self.colors["background"]
        self.pdf.set_fill_color(r, g, b)
        self.pdf.rect(0, 0, 210, 297, "F")

    def _add_header(self):
        """Add branded header with logo to non-cover pages."""
        self._set_bg()
        # Header bar
        r, g, b = self.colors["primary"]
        self.pdf.set_fill_color(r, g, b)
        self.pdf.rect(0, 0, 210, 12, "F")

        # Company name in header
        self.pdf.set_font(self.heading_font, size=8)
        self.pdf.set_text_color(*self.colors["text"])
        self.pdf.set_xy(10, 3)
        self.pdf.cell(0, 6, self.brand.get("company_name", ""), align="L")

        # Logo in header (small)
        logo_path = self.brand.get("logo_path", "")
        if os.path.exists(logo_path):
            self.pdf.image(logo_path, x=185, y=1, h=10)

        self.pdf.set_y(20)

    def add_cover_page(self, title, date_str):
        """Create branded cover page."""
        self.pdf.add_page()
        self._set_bg()

        # Logo centered
        logo_path = self.brand.get("logo_path", "")
        if os.path.exists(logo_path):
            self.pdf.image(logo_path, x=65, y=30, w=80)
            self.pdf.set_y(120)
        else:
            self.pdf.set_y(60)

        # Title
        self.pdf.set_font(self.heading_font, size=28)
        self.pdf.set_text_color(*self.colors["primary"])
        self.pdf.multi_cell(0, 14, title, align="C")

        # Subtitle
        self.pdf.ln(8)
        self.pdf.set_font(self.body_font, size=14)
        self.pdf.set_text_color(*self.colors["secondary"])
        self.pdf.cell(0, 10, f"Prepared for {self.business.get('company_name', '')}", align="C")

        # Date
        self.pdf.ln(20)
        self.pdf.set_font(self.body_font, size=11)
        self.pdf.set_text_color(*self.colors["text"])
        self.pdf.cell(0, 10, date_str, align="C")

        # Accent line
        self.pdf.ln(15)
        r, g, b = self.colors["accent"]
        self.pdf.set_draw_color(r, g, b)
        self.pdf.set_line_width(1)
        self.pdf.line(40, self.pdf.get_y(), 170, self.pdf.get_y())

    def add_section(self, title, content):
        """Add a titled section with body text."""
        self.pdf.add_page()
        self._add_header()

        # Section title
        self.pdf.set_font(self.heading_font, size=18)
        self.pdf.set_text_color(*self.colors["primary"])
        self.pdf.cell(0, 12, title)
        self.pdf.ln(8)

        # Accent underline
        r, g, b = self.colors["secondary"]
        self.pdf.set_draw_color(r, g, b)
        self.pdf.set_line_width(0.5)
        self.pdf.line(10, self.pdf.get_y(), 100, self.pdf.get_y())
        self.pdf.ln(8)

        # Body text
        self.pdf.set_font(self.body_font, size=10)
        self.pdf.set_text_color(*self.colors["text"])
        self.pdf.multi_cell(0, 6, content)

    def add_competitor_profile(self, name, details):
        """Add a competitor profile page."""
        self.pdf.add_page()
        self._add_header()

        # Competitor name
        self.pdf.set_font(self.heading_font, size=16)
        self.pdf.set_text_color(*self.colors["primary"])
        self.pdf.cell(0, 12, name)
        self.pdf.ln(10)

        # Details as key-value pairs
        self.pdf.set_font(self.body_font, size=10)
        for key, value in details.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            elif not isinstance(value, str):
                value = str(value)

            # Key
            self.pdf.set_text_color(*self.colors["secondary"])
            self.pdf.set_font(self.body_font, size=9)
            self.pdf.cell(45, 7, str(key).replace("_", " ").title())

            # Value
            self.pdf.set_text_color(*self.colors["text"])
            self.pdf.set_font(self.body_font, size=10)
            self.pdf.multi_cell(0, 7, value[:200])
            self.pdf.ln(2)

    def add_table(self, title, headers, rows):
        """Add a comparison table."""
        self.pdf.add_page()
        self._add_header()

        # Table title
        self.pdf.set_font(self.heading_font, size=16)
        self.pdf.set_text_color(*self.colors["primary"])
        self.pdf.cell(0, 12, title)
        self.pdf.ln(10)

        col_width = (190 - 10) / len(headers)

        # Header row
        self.pdf.set_font(self.body_font, size=9)
        r, g, b = self.colors["primary"]
        self.pdf.set_fill_color(r, g, b)
        self.pdf.set_text_color(*self.colors["background"])
        for header in headers:
            self.pdf.cell(col_width, 8, str(header)[:20], border=1, fill=True, align="C")
        self.pdf.ln()

        # Data rows
        self.pdf.set_text_color(*self.colors["text"])
        fill = False
        for row in rows:
            if fill:
                self.pdf.set_fill_color(30, 30, 30)
            else:
                self.pdf.set_fill_color(*self.colors["background"])

            for cell in row:
                self.pdf.cell(col_width, 7, str(cell)[:25], border=1, fill=True, align="C")
            self.pdf.ln()
            fill = not fill

    def save(self, output_path):
        """Save the PDF to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.pdf.output(output_path)
        return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate branded PDF report")
    parser.add_argument("--analysis", required=True, help="Path to analysis JSON")
    parser.add_argument("--brand_config", required=True, help="Path to brand_config.json")
    parser.add_argument("--business_profile", required=True, help="Path to business_profile.json")
    parser.add_argument("--narrative_sections", required=True,
                        help="Path to JSON with Claude-written narrative sections")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    # Load all inputs
    with open(args.analysis, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    with open(args.brand_config, "r", encoding="utf-8") as f:
        brand = json.load(f)
    with open(args.business_profile, "r", encoding="utf-8") as f:
        business = json.load(f)
    with open(args.narrative_sections, "r", encoding="utf-8") as f:
        narrative = json.load(f)

    try:
        report = BrandedReport(brand, business)
        date_str = datetime.now().strftime("%B %d, %Y")

        # Cover page
        report.add_cover_page("Competitor Analysis Report", date_str)

        # Executive summary
        if "executive_summary" in narrative:
            report.add_section("Executive Summary", narrative["executive_summary"])

        # Individual competitor profiles
        for competitor in analysis.get("competitors", []):
            name = competitor.get("name", "Unknown")
            profile_narrative = narrative.get("competitor_profiles", {}).get(name, "")

            if profile_narrative:
                report.add_section(name, profile_narrative)
            else:
                # Fallback: use structured data
                details = {}
                if "website" in competitor:
                    details["description"] = competitor["website"].get("description", "")
                details["data_sources"] = competitor.get("data_sources", [])
                report.add_competitor_profile(name, details)

        # Feature comparison table
        if "feature_comparison" in narrative:
            table = narrative["feature_comparison"]
            if "headers" in table and "rows" in table:
                report.add_table("Feature Comparison", table["headers"], table["rows"])

        # Pricing comparison table
        if "pricing_comparison" in narrative:
            table = narrative["pricing_comparison"]
            if "headers" in table and "rows" in table:
                report.add_table("Pricing Comparison", table["headers"], table["rows"])

        # Strategic recommendations
        if "recommendations" in narrative:
            report.add_section("Strategic Recommendations", narrative["recommendations"])

        # Market trends
        if "market_trends" in narrative:
            report.add_section("Market Trends", narrative["market_trends"])

        # Save
        output_path = report.save(args.output)
        print(json.dumps({
            "status": "success",
            "output_path": output_path,
            "pages": report.pdf.page,
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
