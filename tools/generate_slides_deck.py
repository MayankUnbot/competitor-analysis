"""Generate a branded Google Slides competitor analysis deck."""

import argparse
import json
import os
import sys

from dotenv import load_dotenv


def hex_to_rgb_float(hex_color):
    """Convert hex to float RGB dict for Slides API (0.0-1.0 range)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return {"red": r, "green": g, "blue": b}


def get_slides_service():
    """Authenticate and return Google Slides + Drive services."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = [
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/drive.file",
    ]

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print(json.dumps({"error": "credentials.json not found. Set up Google OAuth first."}))
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return slides_service, drive_service


def create_text_box(page_id, text, x_emu, y_emu, w_emu, h_emu,
                    font_size=14, color=None, bold=False, font_family="Arial"):
    """Generate requests to create a text box on a slide."""
    element_id = f"elem_{page_id}_{x_emu}_{y_emu}"
    requests = []

    # Create shape
    requests.append({
        "createShape": {
            "objectId": element_id,
            "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": page_id,
                "size": {
                    "width": {"magnitude": w_emu, "unit": "EMU"},
                    "height": {"magnitude": h_emu, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": x_emu, "translateY": y_emu,
                    "unit": "EMU",
                },
            },
        }
    })

    # Insert text
    requests.append({
        "insertText": {
            "objectId": element_id,
            "text": text,
            "insertionIndex": 0,
        }
    })

    # Style text
    style = {
        "fontSize": {"magnitude": font_size, "unit": "PT"},
        "fontFamily": font_family,
    }
    if bold:
        style["bold"] = True
    if color:
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}

    requests.append({
        "updateTextStyle": {
            "objectId": element_id,
            "style": style,
            "textRange": {"type": "ALL"},
            "fields": "fontSize,fontFamily" + (",bold" if bold else "") + (",foregroundColor" if color else ""),
        }
    })

    return requests


def set_slide_background(page_id, color):
    """Set slide background color."""
    return {
        "updatePageProperties": {
            "objectId": page_id,
            "pageProperties": {
                "pageBackgroundFill": {
                    "solidFill": {"color": {"rgbColor": color}}
                }
            },
            "fields": "pageBackgroundFill.solidFill.color",
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate branded Google Slides deck")
    parser.add_argument("--analysis", required=True, help="Path to analysis JSON")
    parser.add_argument("--brand_config", required=True, help="Path to brand_config.json")
    parser.add_argument("--business_profile", required=True, help="Path to business_profile.json")
    parser.add_argument("--narrative_sections", required=True, help="Path to narrative JSON")
    parser.add_argument("--title", default="Competitor Analysis", help="Presentation title")
    args = parser.parse_args()

    load_dotenv()

    # Load inputs
    with open(args.analysis, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    with open(args.brand_config, "r", encoding="utf-8") as f:
        brand = json.load(f)
    with open(args.business_profile, "r", encoding="utf-8") as f:
        business = json.load(f)
    with open(args.narrative_sections, "r", encoding="utf-8") as f:
        narrative = json.load(f)

    colors = {k: hex_to_rgb_float(v) for k, v in brand["colors"].items()}
    company = brand.get("company_name", business.get("company_name", ""))
    heading_font = brand["fonts"]["heading"]["name"]
    body_font = brand["fonts"]["body"]["name"]

    try:
        slides_service, drive_service = get_slides_service()

        # Create presentation
        presentation = slides_service.presentations().create(
            body={"title": f"{args.title} - {company}"}
        ).execute()
        presentation_id = presentation["presentationId"]

        # Get the default first slide ID
        first_slide_id = presentation["slides"][0]["objectId"]

        batch_requests = []

        # --- Slide 1: Title slide (use existing first slide) ---
        batch_requests.append(set_slide_background(first_slide_id, colors["background"]))
        batch_requests.extend(create_text_box(
            first_slide_id, args.title,
            x_emu=500000, y_emu=1500000, w_emu=8000000, h_emu=1200000,
            font_size=36, color=colors["primary"], bold=True, font_family=heading_font,
        ))
        batch_requests.extend(create_text_box(
            first_slide_id, f"Prepared for {company}",
            x_emu=500000, y_emu=3000000, w_emu=8000000, h_emu=600000,
            font_size=18, color=colors["secondary"], font_family=body_font,
        ))

        # --- Slide 2: Executive Summary ---
        exec_slide_id = "slide_exec_summary"
        batch_requests.append({"createSlide": {"objectId": exec_slide_id, "insertionIndex": 1}})
        batch_requests.append(set_slide_background(exec_slide_id, colors["background"]))
        batch_requests.extend(create_text_box(
            exec_slide_id, "Executive Summary",
            x_emu=500000, y_emu=300000, w_emu=8000000, h_emu=600000,
            font_size=28, color=colors["primary"], bold=True, font_family=heading_font,
        ))
        exec_text = narrative.get("executive_summary", "Analysis in progress...")
        # Truncate for slide readability
        if len(exec_text) > 600:
            exec_text = exec_text[:597] + "..."
        batch_requests.extend(create_text_box(
            exec_slide_id, exec_text,
            x_emu=500000, y_emu=1100000, w_emu=8000000, h_emu=3500000,
            font_size=14, color=colors["text"], font_family=body_font,
        ))

        # --- Competitor slides (1 per competitor) ---
        slide_index = 2
        competitor_profiles = narrative.get("competitor_profiles", {})
        for competitor in analysis.get("competitors", [])[:8]:  # Cap at 8 competitors
            name = competitor.get("name", "Unknown")
            slide_id = f"slide_comp_{slide_index}"

            batch_requests.append({"createSlide": {"objectId": slide_id, "insertionIndex": slide_index}})
            batch_requests.append(set_slide_background(slide_id, colors["background"]))

            # Competitor name
            batch_requests.extend(create_text_box(
                slide_id, name,
                x_emu=500000, y_emu=300000, w_emu=8000000, h_emu=600000,
                font_size=24, color=colors["primary"], bold=True, font_family=heading_font,
            ))

            # Profile text
            profile_text = competitor_profiles.get(name, "")
            if not profile_text:
                # Fallback to structured data
                website = competitor.get("website", {})
                profile_text = website.get("description", "") or f"Data sources: {', '.join(competitor.get('data_sources', []))}"

            if len(profile_text) > 500:
                profile_text = profile_text[:497] + "..."

            batch_requests.extend(create_text_box(
                slide_id, profile_text,
                x_emu=500000, y_emu=1100000, w_emu=8000000, h_emu=3500000,
                font_size=13, color=colors["text"], font_family=body_font,
            ))

            slide_index += 1

        # --- Recommendations slide ---
        rec_slide_id = "slide_recommendations"
        batch_requests.append({"createSlide": {"objectId": rec_slide_id, "insertionIndex": slide_index}})
        batch_requests.append(set_slide_background(rec_slide_id, colors["background"]))
        batch_requests.extend(create_text_box(
            rec_slide_id, "Strategic Recommendations",
            x_emu=500000, y_emu=300000, w_emu=8000000, h_emu=600000,
            font_size=28, color=colors["primary"], bold=True, font_family=heading_font,
        ))
        rec_text = narrative.get("recommendations", "Recommendations pending analysis...")
        if len(rec_text) > 600:
            rec_text = rec_text[:597] + "..."
        batch_requests.extend(create_text_box(
            rec_slide_id, rec_text,
            x_emu=500000, y_emu=1100000, w_emu=8000000, h_emu=3500000,
            font_size=14, color=colors["text"], font_family=body_font,
        ))

        # Execute all requests
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": batch_requests},
        ).execute()

        slides_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"

        print(json.dumps({
            "status": "success",
            "presentation_id": presentation_id,
            "url": slides_url,
            "slides_count": slide_index + 1,
        }, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
