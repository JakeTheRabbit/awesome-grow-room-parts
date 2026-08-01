#!/usr/bin/env python3
"""Build the static site into docs/ for GitHub Pages.

Everything is generated from parts/*.yaml and recipes/*.yaml. The page is a
single self-contained HTML file with the data embedded, so it works from
file:// as well as from Pages - no build step, no CDN, no fetch().

Run:  python scripts/build_site.py
"""
import json
import os
import shutil
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
TEMPLATE = os.path.join(ROOT, "scripts", "site_template.html")

# Only these fields reach the browser. Anything not listed here stays out of the
# published bundle by construction - a cheap guard against leaking a field that
# gets added to the schema later.
FIELDS = [
    "id", "name", "manufacturer", "part_numbers", "category", "subcategory", "bus",
    "i2c", "protocol_settings", "voltage", "price", "vendors", "ip_rating",
    "calibration_required", "calibration_notes", "quality_tier", "deployment_count",
    "deployment_evidence", "evidence", "failure_modes", "notes", "drivers",
    "platforms", "works_with", "alternatives", "image", "image_source", "image_source_url",
    "use_cases", "accuracy", "datasheet_url", "example", "tags",
]


def load_dir(path):
    out = []
    if not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        if name.endswith((".yaml", ".yml")):
            out.append(yaml.safe_load(open(os.path.join(path, name), encoding="utf-8")))
    return out


def main():
    parts = [{k: p[k] for k in FIELDS if k in p} for p in load_dir(os.path.join(ROOT, "parts"))]

    # A part with a real photo also has a 480px sibling for the hover preview.
    # Derived here rather than stored, so the two can never disagree.
    for p in parts:
        img = p.get("image", "")
        if img.endswith(".png"):
            big = img[:-4] + "-lg.png"
            if os.path.isfile(os.path.join(ROOT, big)):
                p["image_large"] = big
    recipes = load_dir(os.path.join(ROOT, "recipes"))
    if not parts:
        print("no parts found", file=sys.stderr)
        return 1

    os.makedirs(DOCS, exist_ok=True)

    # Self-host every thumbnail under docs/ so Pages serves them from one origin.
    src_assets = os.path.join(ROOT, "assets", "parts")
    dst_assets = os.path.join(DOCS, "assets", "parts")
    if os.path.isdir(src_assets):
        shutil.rmtree(dst_assets, ignore_errors=True)
        shutil.copytree(src_assets, dst_assets)

    # Secondary-currency prices are DERIVED in the browser from each part's one
    # canonical observed price, using this single rate table. Nothing is stored
    # twice, so a stale conversion cannot hide in a part file.
    fx_path = os.path.join(ROOT, "data", "fx.yaml")
    fx = yaml.safe_load(open(fx_path, encoding="utf-8")) if os.path.isfile(fx_path) else {}

    payload = {"parts": parts, "recipes": recipes, "fx": fx}
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # </script> inside any string would terminate the embedding script tag early.
    blob = blob.replace("</", "<\\/")

    html = open(TEMPLATE, encoding="utf-8").read().replace("__DATA__", blob)
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    # Also emit the raw data for anyone who wants to consume the catalogue.
    with open(os.path.join(DOCS, "data.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    # Pages would otherwise run the output through Jekyll and drop _-prefixed files.
    open(os.path.join(DOCS, ".nojekyll"), "w").close()

    i2c = sum(1 for p in parts if (p.get("i2c") or {}).get("address"))
    size = os.path.getsize(os.path.join(DOCS, "index.html")) / 1024
    rates = ", ".join(f"1 {fx.get('base')} = {v} {k}" for k, v in (fx.get("rates") or {}).items())
    print(f"docs/index.html  {size:.0f} KB  ({len(parts)} parts, {i2c} on I2C, {len(recipes)} recipes)")
    print(f"fx: {rates or 'none'}  (rate date {fx.get('rate_date', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
