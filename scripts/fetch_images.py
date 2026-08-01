#!/usr/bin/env python3
"""Fetch, normalise and self-host product images.

Driven by data/image_sources.yaml, which maps a part id to the page its image
comes from. Nothing is hotlinked: images are downloaded, normalised and
committed, so the catalogue does not break when a vendor reorganises their CDN.

For each part we write two files:
  assets/parts/<id>.png      96x96   - the table thumbnail
  assets/parts/<id>-lg.png   480x480 - the hover preview and drawer image

Both are square with a white background, so rows stay on a consistent grid
regardless of the source image's aspect ratio.

Provenance is written back into the part YAML as `image_source` and
`image_source_url` so every image can be traced and a takedown honoured.

Where no usable image is found the generated placeholder is KEPT. A truthful
placeholder beats a wrong or broken picture.

Run:  python scripts/fetch_images.py [--only id1,id2] [--force]
"""
import argparse
import io
import os
import re
import sys
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "parts")
ASSETS = os.path.join(ROOT, "assets", "parts")
SOURCES = os.path.join(ROOT, "data", "image_sources.yaml")

SMALL, LARGE = 96, 480
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Junk that lives on product pages and is never the product.
BAD = re.compile(r"(sprite|logo|icon|banner|badge|placeholder|payment|visa|"
                 r"mastercard|paypal|facebook|twitter|instagram|youtube|"
                 r"loading|spinner|avatar|flag|star|arrow)", re.I)


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def candidates(page_url):
    """Image URLs from a product page, best guess first."""
    try:
        html = get(page_url).decode("utf-8", "replace")
    except Exception as exc:                                  # noqa: BLE001
        print(f"    page fetch failed: {type(exc).__name__}")
        return []

    out = []
    # og:image is what the vendor themselves nominate as representative.
    out += re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html)
    out += re.findall(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)', html)
    # JSON-LD product images.
    out += re.findall(r'"image"\s*:\s*"([^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', html)
    # Then anything that looks like a product photo.
    out += re.findall(r'https?://[^\s"\'<>()]+?\.(?:jpg|jpeg|png|webp)', html)

    seen, clean = set(), []
    for u in out:
        u = u.replace("&amp;", "&").strip()
        if u.startswith("//"):
            u = "https:" + u
        if not u.startswith("http") or u in seen or BAD.search(u):
            continue
        seen.add(u)
        clean.append(u)
    return clean


def normalise(data, size):
    """Square, white-backed, centred, no upscaling past the source."""
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im).convert("RGB")
    else:
        im = im.convert("RGB")
    im.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas


def usable(data):
    """Reject tracking pixels, sprites and anything too small to be a product."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        w, h = im.size
    except Exception:                                         # noqa: BLE001
        return False, "not an image"
    if w < 120 or h < 120:
        return False, f"too small ({w}x{h})"
    if max(w, h) / max(1, min(w, h)) > 4:
        return False, f"extreme aspect ratio ({w}x{h})"
    return True, f"{w}x{h}"


def set_field(path, key, value):
    """Insert or replace a scalar key at the top level of a part YAML."""
    src = open(path, encoding="utf-8").read()
    line = f"{key}: {value}\n"
    if re.search(rf"^{key}:.*$", src, re.M):
        src = re.sub(rf"^{key}:.*$", line.rstrip("\n"), src, count=1, flags=re.M)
    else:
        src = re.sub(r"^(image:.*\n)", r"\1" + line, src, count=1, flags=re.M)
    open(path, "w", encoding="utf-8", newline="\n").write(src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated part ids")
    ap.add_argument("--force", action="store_true", help="refetch even if a PNG exists")
    args = ap.parse_args()

    sources = yaml.safe_load(open(SOURCES, encoding="utf-8")) or {}
    entries = sources.get("parts") or {}
    if args.only:
        wanted = set(args.only.split(","))
        entries = {k: v for k, v in entries.items() if k in wanted}

    ok = skipped = failed = 0
    for pid, spec in entries.items():
        part_path = os.path.join(PARTS, pid + ".yaml")
        if not os.path.isfile(part_path):
            print(f"[{pid}] no such part"); failed += 1; continue

        small_path = os.path.join(ASSETS, pid + ".png")
        if os.path.isfile(small_path) and not args.force:
            skipped += 1; continue

        page = spec.get("page")
        direct = spec.get("direct")
        kind = spec.get("source", "manufacturer")
        print(f"[{pid}]")

        urls = [direct] if direct else candidates(page)
        if not direct and spec.get("match"):
            rx = re.compile(spec["match"], re.I)
            urls = [u for u in urls if rx.search(u)] or urls

        chosen = data = None
        for u in urls[:12]:
            try:
                blob = get(u)
            except Exception as exc:                          # noqa: BLE001
                continue
            good, why = usable(blob)
            if good:
                chosen, data = u, blob
                print(f"    using {why}  {u[:88]}")
                break

        if not data:
            print("    no usable image - keeping generated placeholder")
            failed += 1
            continue

        os.makedirs(ASSETS, exist_ok=True)
        normalise(data, SMALL).save(small_path, "PNG", optimize=True)
        normalise(data, LARGE).save(os.path.join(ASSETS, pid + "-lg.png"), "PNG", optimize=True)

        set_field(part_path, "image", f"assets/parts/{pid}.png")
        set_field(part_path, "image_source", kind)
        set_field(part_path, "image_source_url", page or chosen)
        ok += 1

    print(f"\nfetched {ok}, already had {skipped}, kept placeholder for {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
