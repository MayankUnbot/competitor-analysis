"""Save structured data to a JSON file. Creates directories as needed."""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Save JSON data to a file")
    parser.add_argument("--data", required=True, help="JSON string to save")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    try:
        parsed = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(json.dumps({"status": "saved", "path": os.path.abspath(args.output)}))


if __name__ == "__main__":
    main()
