#!/usr/bin/env python3
"""Validate every part and recipe against the JSON Schema, then check the things
a schema cannot: cross-references, image files, duplicate ids, tier honesty, and
credentials that should never have been committed.

Run:  python scripts/validate.py
Exit: 0 clean, 1 if anything failed.
"""
import json
import os
import re
import sys

import yaml
from jsonschema import Draft7Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "parts")
RECIPES = os.path.join(ROOT, "recipes")

errors = []
warnings = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def load_yaml_dir(path):
    out = {}
    if not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        if not name.endswith((".yaml", ".yml")):
            continue
        full = os.path.join(path, name)
        try:
            out[name] = yaml.safe_load(open(full, encoding="utf-8"))
        except yaml.YAMLError as exc:
            err(name, f"unparseable YAML: {exc}")
    return out


# --------------------------------------------------------------------------
# Credential patterns. These exist because the source configs this catalogue
# was distilled from contain LIVE keys - see SECURITY.md. Nothing lifted from a
# real config may carry a credential into this repo.
# --------------------------------------------------------------------------
SECRET_PATTERNS = [
    (re.compile(r"\bkey:\s*[\"']?[A-Za-z0-9+/]{40,}={0,2}[\"']?"), "API encryption key"),
    (re.compile(r"\bpassword:\s*[\"']?[0-9a-f]{32}[\"']?"), "OTA password (32-hex)"),
    (re.compile(r"\bpassword:\s*[\"'](?!YOUR_|CHANGE|placeholder)[^\"'\n]{8,}[\"']"), "hard-coded password"),
    (re.compile(r"\bssid:\s*[\"'](?!YOUR_|Fallback)[^\"'\n]+[\"']"), "hard-coded SSID"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "IP address"),
    (re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"), "MAC address"),
    (re.compile(r"uid:\s*[\"'](?!00-00-00-00)[0-9A-F]{2}(?:-[0-9A-F]{2}){3,}[\"']"), "RFID card UID"),
    (re.compile(r"\bnetwork_key\b", re.I), "Zigbee network key"),
    (re.compile(r"rtsp://[^\s\"']*:[^\s\"']*@"), "RTSP credentials"),
]

# Documented, deliberately-safe strings that must not trip the scanner.
SECRET_ALLOW = re.compile(
    r"!secret\s|YOUR_|CHANGE_ME|placeholder|0\.0\.0\.0|127\.0\.0\.1|"
    r"192\.168\.1\.\d+|255\.255\.255\.0|00-00-00-00|"
    r"1\.302e-2|6\.771e-10|5\.105e-6",  # calibration polynomial coefficients
    re.I,
)


def scan_secrets(text, where):
    for line_no, line in enumerate(text.splitlines(), 1):
        if SECRET_ALLOW.search(line):
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(line):
                err(where, f"line {line_no}: possible {label} - scrub before committing")


def main():
    schema_path = os.path.join(ROOT, "schema", "part.schema.json")
    validator = Draft7Validator(json.load(open(schema_path, encoding="utf-8")))

    parts = load_yaml_dir(PARTS)
    if not parts:
        err("parts/", "no part files found")

    ids = {}
    for name, data in parts.items():
        if not isinstance(data, dict):
            err(name, "top level must be a mapping")
            continue

        for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            err(name, f"{'.'.join(str(p) for p in e.path) or '(root)'}: {e.message}")

        pid = data.get("id")
        if pid:
            if pid in ids:
                err(name, f"duplicate id '{pid}' (also in {ids[pid]})")
            ids[pid] = name
            expected = pid + ".yaml"
            if name != expected:
                err(name, f"filename must match id -> expected {expected}")

        # Image must be self-hosted AND actually present. A blank thumbnail is a
        # visible hole on the site, so this is an error not a warning.
        img = data.get("image")
        if img and not os.path.isfile(os.path.join(ROOT, img)):
            err(name, f"image file missing: {img}")

        # Tier honesty: field-proven is a claim about evidence, so check it.
        if data.get("quality_tier") == "field-proven":
            listed = data.get("deployment_evidence") or []
            count = data.get("deployment_count") or 0
            if count < len(listed):
                err(name, f"deployment_count ({count}) < listed evidence files ({len(listed)})")
            if not listed:
                err(name, "field-proven requires deployment_evidence filenames")

        # An 'avoid' entry has to say why, or it is just a grudge.
        if data.get("quality_tier") == "avoid" and not data.get("failure_modes"):
            err(name, "quality_tier 'avoid' requires failure_modes")

        scan_secrets(open(os.path.join(PARTS, name), encoding="utf-8").read(), name)

    # Referential integrity - a dangling id silently breaks the site's links.
    for name, data in parts.items():
        if not isinstance(data, dict):
            continue
        for field in ("works_with", "alternatives"):
            for ref in data.get(field) or []:
                if ref not in ids:
                    err(name, f"{field} -> unknown part id '{ref}'")
                if ref == data.get("id"):
                    err(name, f"{field} -> references itself")

    # Recipes reference parts by id and must total correctly.
    for name, data in load_yaml_dir(RECIPES).items():
        if not isinstance(data, dict):
            err(name, "top level must be a mapping")
            continue
        for item in data.get("items") or []:
            ref = item.get("part") if isinstance(item, dict) else None
            if ref and ref not in ids:
                err(name, f"items -> unknown part id '{ref}'")

    # I2C collision awareness. Not an error - a bus can legitimately host parts
    # that are never used together - but the site surfaces it, so flag it here.
    by_addr = {}
    for name, data in parts.items():
        if not isinstance(data, dict):
            continue
        i2c = data.get("i2c") or {}
        addr = i2c.get("address")
        if addr:
            by_addr.setdefault(addr.lower(), []).append(data["id"])
        # Composite modules occupy several addresses; each can collide.
        for extra in i2c.get("also_occupies") or []:
            by_addr.setdefault(extra.lower(), []).append(data["id"] + " (secondary)")
        overlap = {a.lower() for a in i2c.get("alternates") or []} & \
                  {a.lower() for a in i2c.get("also_occupies") or []}
        if overlap:
            err(name, f"i2c: {sorted(overlap)} listed as both an escape route and occupied")
    for addr, members in sorted(by_addr.items()):
        if len(members) > 1:
            warn("i2c", f"{addr} shared by {len(members)} parts: {', '.join(sorted(members))}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print(f"\n{len(parts)} parts, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
