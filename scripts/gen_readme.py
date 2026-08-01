#!/usr/bin/env python3
"""Regenerate the catalogue tables inside README.md from parts/*.yaml, so the
repo still reads as a proper awesome list without anyone hand-maintaining a
table that drifts.

Only the region between the AUTOGEN markers is rewritten; everything else in
README.md is hand-written and left alone.

Run:  python scripts/gen_readme.py
"""
import os
import sys
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- AUTOGEN:PARTS START -->"
END = "<!-- AUTOGEN:PARTS END -->"

TIER_LABEL = {
    "field-proven": "**field-proven**",
    "works": "works",
    "experimental": "experimental",
    "avoid": "**avoid**",
}
TIER_ORDER = {"field-proven": 0, "works": 1, "experimental": 2, "avoid": 3}


def esc(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def main():
    parts = []
    for name in sorted(os.listdir(os.path.join(ROOT, "parts"))):
        if name.endswith((".yaml", ".yml")):
            parts.append(yaml.safe_load(open(os.path.join(ROOT, "parts", name), encoding="utf-8")))

    by_cat = defaultdict(list)
    for p in parts:
        by_cat[p["category"]].append(p)

    out = [
        f"_{len(parts)} parts. Generated from `parts/*.yaml` by "
        f"`scripts/gen_readme.py` — edit the YAML, not this table._\n",
    ]

    # Lead with the evidence, since that is the point of the list.
    proven = sorted([p for p in parts if p.get("quality_tier") == "field-proven"],
                    key=lambda p: -(p.get("deployment_count") or 0))
    out.append("### Field-proven core\n")
    out.append("Parts named in the stated number of live production ESPHome device configs.\n")
    out.append("| Part | Live configs | Bus | I²C | Price | Notes |")
    out.append("|---|---:|---|---|---|---|")
    for p in proven:
        price = p.get("price") or {}
        pr = f"{price.get('currency','')} {price.get('observed')}" if price.get("observed") else price.get("band", "")
        out.append(
            f"| [{esc(p['name'])}](parts/{p['id']}.yaml) | {p.get('deployment_count','')} | "
            f"{esc('/'.join(p.get('bus', [])))} | {esc((p.get('i2c') or {}).get('address',''))} | "
            f"{esc(pr)} | {esc(p.get('subcategory',''))} |")
    out.append("")

    avoid = [p for p in parts if p.get("quality_tier") == "avoid"]
    if avoid:
        out.append("### Hall of shame\n")
        out.append("Documented dead ends. Listed so nobody repeats the work.\n")
        out.append("| Part | Why it is here |")
        out.append("|---|---|")
        for p in sorted(avoid, key=lambda p: p["name"]):
            reason = (p.get("failure_modes") or [""])[0]
            out.append(f"| [{esc(p['name'])}](parts/{p['id']}.yaml) | {esc(reason)} |")
        out.append("")

    out.append("### Everything, by category\n")
    for cat in sorted(by_cat):
        out.append(f"#### {cat}\n")
        out.append("| Part | Tier | Live | Bus | I²C | Price |")
        out.append("|---|---|---:|---|---|---|")
        for p in sorted(by_cat[cat], key=lambda p: (TIER_ORDER.get(p.get("quality_tier"), 9),
                                                    -(p.get("deployment_count") or 0), p["name"])):
            price = p.get("price") or {}
            pr = f"{price.get('currency','')} {price.get('observed')}" if price.get("observed") else price.get("band", "")
            dep = p.get("deployment_count")
            out.append(
                f"| [{esc(p['name'])}](parts/{p['id']}.yaml) | "
                f"{TIER_LABEL.get(p.get('quality_tier'), '')} | {dep if dep else ''} | "
                f"{esc('/'.join(p.get('bus', [])))} | {esc((p.get('i2c') or {}).get('address',''))} | {esc(pr)} |")
        out.append("")

    table = "\n".join(out)
    readme_path = os.path.join(ROOT, "README.md")
    src = open(readme_path, encoding="utf-8").read()
    if START not in src or END not in src:
        print(f"markers {START} / {END} not found in README.md", file=sys.stderr)
        return 1
    head, rest = src.split(START, 1)
    _, tail = rest.split(END, 1)
    with open(readme_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"{head}{START}\n\n{table}\n{END}{tail}")
    print(f"README.md regenerated: {len(parts)} parts, {len(proven)} field-proven, {len(avoid)} avoid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
