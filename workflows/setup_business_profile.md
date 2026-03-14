# Setup Business Profile

## Objective
Collect and persist the user's business details so all workflows have context.

## Required Inputs
Ask the user for:
- Company/brand name
- Industry and niche
- Description of what they do
- Target audience
- Key differentiators
- Stage (early, growth, established)
- Similar companies/creators for reference

## Process
1. Ask the user for each field (or accept all at once)
2. Structure as JSON
3. Save using:
```
python tools/save_json.py --data '{...}' --output .tmp/business_profile.json
```

## Update Flow
The user can re-run this anytime to update their profile. The new profile overwrites the old one.

## Current Profile
If `.tmp/business_profile.json` already exists, read it first and ask the user what they'd like to update rather than collecting everything from scratch.
