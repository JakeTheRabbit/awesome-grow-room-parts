#!/usr/bin/env python3
"""Link-rot checker for vendor and driver URLs.

Vendor listings rot constantly - that is exactly why every part records
canonical `part_numbers`. This flags dead links so they can be replaced, and it
deliberately does NOT fail the build on a 404: a dead vendor link is a chore,
not a broken catalogue. It exits non-zero only when a part has NO reachable
vendor link at all AND no part number to fall back on.

Run:  python scripts/check_links.py [--timeout 15]
"""
import argparse
import concurrent.futures
import os
import urllib.error
import urllib.request
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "awesome-grow-room-parts link checker (+https://github.com/)"


def check(url, timeout):
    """HEAD, falling back to a ranged GET - plenty of shops reject HEAD."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Range": "bytes=0-2047",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, ""
        except urllib.error.HTTPError as exc:
            # 403/405 usually means bot-blocked, not dead. Only GET-404 is real.
            if exc.code in (403, 405, 406) and method == "HEAD":
                continue
            return exc.code, exc.reason
        except Exception as exc:                      # noqa: BLE001 - report anything
            if method == "HEAD":
                continue
            return None, type(exc).__name__
    return None, "unreachable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    targets = []
    parts = {}
    for name in sorted(os.listdir(os.path.join(ROOT, "parts"))):
        if not name.endswith((".yaml", ".yml")):
            continue
        p = yaml.safe_load(open(os.path.join(ROOT, "parts", name), encoding="utf-8"))
        parts[p["id"]] = p
        for v in p.get("vendors") or []:
            targets.append((p["id"], "vendor", v["name"], v["url"]))
        for d in p.get("drivers") or []:
            targets.append((p["id"], "driver", d["name"], d["url"]))

    results = defaultdict(list)
    dead_total = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check, url, args.timeout): (pid, kind, label, url)
                   for pid, kind, label, url in targets}
        for fut in concurrent.futures.as_completed(futures):
            pid, kind, label, url = futures[fut]
            status, reason = fut.result()
            ok = status is not None and status < 400
            results[pid].append((kind, ok, status, label, url, reason))
            if not ok:
                dead_total += 1
                print(f"DEAD  [{status or 'ERR'}] {pid} · {kind} · {label}\n      {url}  {reason}")

    # Only a real failure if a part becomes unbuyable AND unsearchable.
    orphaned = []
    for pid, rows in results.items():
        vend = [r for r in rows if r[0] == "vendor"]
        if vend and not any(r[1] for r in vend) and not parts[pid].get("part_numbers"):
            orphaned.append(pid)

    print(f"\nchecked {len(targets)} links across {len(parts)} parts; {dead_total} unreachable")
    if orphaned:
        print("\nFAIL - every vendor link dead and no part_numbers to search on:")
        for pid in orphaned:
            print(f"  {pid}")
        return 1
    if dead_total:
        print("Dead links do not fail the build - replace the URL, or rely on part_numbers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
