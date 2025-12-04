#!/usr/bin/env python3
"""
Run the existing Guidebook module to generate guidebooks from a JSON file.

Usage examples:
  # From repo root:
  python scripts/gen_guidebook.py --input travel_plan_output.json --formats pdf --output-dir ./guidebooks

  # All formats:
  python scripts/gen_guidebook.py -i travel_plan_output.json -f pdf html markdown -o ./guidebooks

This runner assumes your existing module exposes `GuidebookGenerator` in:
  src/travel_planner/guidebook/generator.py

and that it supports:
  GuidebookGenerator(travel_plan_data: dict, output_dir: str = "guidebooks")
  generate_all_formats(formats: list[str], options: dict) -> dict
  generate_pdf(), generate_html(), generate_markdown() (optional)
"""
import argparse
import json
import os
import sys
from typing import List


def add_src_to_path():
    """
    Ensure `src/` is on sys.path so `travel_planner.guidebook` can be imported
    even if the user hasn't installed the package editable.
    """
    repo_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def ensure_output_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def parse_args():
    parser = argparse.ArgumentParser(description="Run existing guidebook generator on a JSON file")
    parser.add_argument(
        "-i", "--input", required=True, help="Path to travel_plan_output.json (or similar TravelPlan JSON)"
    )
    parser.add_argument(
        "-f",
        "--formats",
        nargs="+",
        default=["pdf"],
        choices=["pdf", "html", "markdown"],
        help="Formats to generate",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="guidebooks",
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--language",
        "-l",
        default="vi",
        choices=["vi", "en"],
        help="Language (if the module supports it)",
    )
    parser.add_argument(
        "--include-location-images",
        action="store_true",
        help="Ask the module to fetch location images (if implemented; requires API keys)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    add_src_to_path()

    # Import the existing Guidebook module from your repo
    try:
        from travel_planner.guidebook.generator import GuidebookGenerator
    except Exception as e:
        print("ERROR: Could not import GuidebookGenerator from travel_planner.guidebook.generator.")
        print("Hint: Run from repo root, or ensure src/ is on PYTHONPATH.")
        print(f"Details: {e}")
        sys.exit(1)

    # Read the travel plan JSON
    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)
    with open(args.input, "r", encoding="utf-8") as f:
        travel_plan = json.load(f)

    out_dir = ensure_output_dir(args.output_dir)

    # Instantiate and run using the existing API
    generator = GuidebookGenerator(travel_plan, output_dir=out_dir)

    print(f"Generating formats: {args.formats} -> {out_dir}")
    results = generator.generate_all_formats(formats=args.formats)

    print("\nGenerated files:")
    for fmt, path in results.items():
        print(f" - {fmt}: {path}")

    print("\nDone.")


if __name__ == "__main__":
    main()