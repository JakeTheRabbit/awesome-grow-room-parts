#!/usr/bin/env python3
"""Generate docs/diy-vs-proprietary.html.

The DIY side is derived from this repository's own build recipes rather than
re-entered, so it cannot drift from the catalogue. The vendor side comes from
data/vendor-pricing.yaml, where every figure carries the confidence tag and
source it came from - both of which are rendered on the page.

Run:  python scripts/build_comparison.py
"""
import html
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# AROYA bill by canopy square footage facility-wide, not by room. Published in
# their ROI calculator page JavaScript and labelled by AROYA as 2025 pricing.
AROYA_TIERS = [
    (2500, 150), (5000, 300), (10000, 600), (20000, 900),
    (50000, 1800), (75000, 2900), (100000, 3900),
]


def load(path):
    return yaml.safe_load(open(path, encoding="utf-8"))


def build_diy(fx):
    """DIY cost per room, derived from the repo's own recipes."""
    parts = {}
    pdir = os.path.join(ROOT, "parts")
    for name in os.listdir(pdir):
        if name.endswith((".yaml", ".yml")):
            p = load(os.path.join(pdir, name))
            parts[p["id"]] = p

    base = fx.get("base", "NZD")
    rates = fx.get("rates") or {}

    def to_usd(amount, cur):
        if cur == "USD":
            return amount
        in_base = amount if cur == base else (amount / rates[cur] if rates.get(cur) else None)
        if in_base is None:
            return None
        return in_base * rates["USD"] if rates.get("USD") else None

    recipes = {}
    rdir = os.path.join(ROOT, "recipes")
    for name in sorted(os.listdir(rdir)):
        if not name.endswith((".yaml", ".yml")):
            continue
        r = load(os.path.join(rdir, name))
        total_usd, priced, unpriced = 0.0, 0, 0
        lines = []
        for it in r.get("items") or []:
            p = parts.get(it.get("part"))
            if not p:
                continue
            pr = p.get("price") or {}
            obs, cur = pr.get("observed"), pr.get("currency")
            usd = to_usd(obs, cur) if obs is not None else None
            qty = it.get("qty", 1)
            if usd is None:
                unpriced += 1
            else:
                priced += 1
                total_usd += usd * qty
            lines.append({
                "name": p["name"], "qty": qty,
                "usd": round(usd, 2) if usd is not None else None,
                "source": (pr.get("source") or "estimate"),
            })
        recipes[r["id"]] = {
            "name": r["name"], "summary": r.get("summary", ""),
            "total_usd": round(total_usd, 2), "priced": priced,
            "unpriced": unpriced, "lines": lines,
        }
    return recipes


def money(n):
    return "${:,.0f}".format(n)


def esc(s):
    return html.escape(str(s if s is not None else ""))


TAG_TITLE = {
    "a": "Vendor-published - on the vendor's own site, docs, contract or product feed",
    "b": "Reseller or distributor listing",
    "c": "User-reported - forum, Reddit, or trade press quoting a named customer",
    "d": "NOT publicly available - quote-only, or searched for and not found",
}


def tag_badge(tag):
    if not tag:
        return ""
    return (f'<span class="tag tag-{esc(tag)}" title="{esc(TAG_TITLE.get(tag, ""))}">'
            f'({esc(tag)})</span>')


def conf_badge(conf, note=None):
    if not conf:
        return ""
    cls = conf.split("-")[0].lower()
    t = note or ""
    return (f'<span class="conf conf-{esc(cls)}"{f" title={json.dumps(t)}" if t else ""}>'
            f'{esc(conf)}</span>')


def main():
    data = load(os.path.join(ROOT, "data", "vendor-pricing.yaml"))
    fx = load(os.path.join(ROOT, "data", "fx.yaml"))
    recipes = build_diy(fx)

    diy_room = recipes.get("poe-room-controller", {}).get("total_usd", 0)
    diy_substrate = recipes.get("substrate-sensing-array", {}).get("total_usd", 0)
    diy_per_room = round(diy_room + diy_substrate, 2)

    gbp_usd = (fx.get("cross_rates") or {}).get("GBP_USD")
    for v in data["vendors"]:
        for scope in ("four_room", "single_room"):
            blk = v.get(scope) or {}
            if blk.get("hardware_gbp") is not None:
                if not gbp_usd:
                    raise SystemExit(f"{v['id']}: priced in GBP but no GBP_USD cross-rate in data/fx.yaml")
                blk["hardware"] = round(blk["hardware_gbp"] * gbp_usd)
                blk["converted_from"] = f"GBP at {gbp_usd}"

    payload = {
        "vendors": data["vendors"],
        "aroya_tiers": AROYA_TIERS,
        "diy": {
            "per_room": diy_per_room,
            "controller": diy_room,
            "substrate": diy_substrate,
            "recipes": recipes,
            "fx_rate": (fx.get("rates") or {}).get("USD"),
            "fx_base": fx.get("base"),
            "fx_date": fx.get("rate_date"),
        },
    }

    tpl = open(os.path.join(ROOT, "scripts", "comparison_template.html"), encoding="utf-8").read()

    # Server-rendered sections: these must be readable without JavaScript,
    # because the honest-limits material is the part that most needs to survive.
    against = data["case_against_diy"]
    against_html = "".join(
        f'<li><h4>{esc(p["title"])}</h4><p>{esc(p["detail"])}</p></li>'
        for p in against["points"])

    notob_html = "".join(
        f'<div class="notob"><h4>{esc(v["name"])} '
        f'{tag_badge(v.get("tag"))}</h4><p>{esc(v["finding"])}</p>'
        f'<p class="rel"><b>Relevance:</b> {esc(v["relevance"])}</p>'
        f'<p class="src"><a href="{esc(v["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(v["url"])}</a></p></div>'
        for v in data["not_obtainable"])

    recs = data.get("recommendations") or {}
    rec_html = "".join(
        f'<div class="rec rec-{esc(p.get("rating","qualified"))}">'
        f'<h3>{esc(p["subject"])}</h3>'
        f'<p class="verdict">{esc(p["verdict"])}</p>'
        f'<p>{esc(p["detail"])}</p>'
        + (f'<p><b>Why it fits a DIY-minded build:</b> {esc(p["why_it_fits"])}</p>'
           if p.get("why_it_fits") else "")
        + (f'<p class="caveat"><b>Caveat.</b> {esc(p["caveat"])}</p>'
           if p.get("caveat") else "")
        + "</div>"
        for p in recs.get("picks") or [])

    hidden_html = "".join(
        f'<tr><td>{esc(h["item"])}</td><td>{esc(h["detail"])}</td></tr>'
        for h in data["hidden_costs"])

    CAP_LABEL = {
        "control": "Runs the room",
        "monitor": "Monitoring only",
        "analytics": "Analytics / agronomy",
    }
    vend_html = ""
    for v in data["vendors"]:
        cites = "".join(
            f'<li><a href="{esc(c["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(c["label"])}</a> {tag_badge(c.get("tag"))}</li>'
            for c in v.get("citations") or [])
        fr = v.get("four_room") or {}
        vend_html += f'''<div class="vcard">
  <h3>{esc(v["name"])} <span class="cap cap-{esc(v.get("capability", ""))}">{esc(CAP_LABEL.get(v.get("capability"), ""))}</span></h3>
  <p class="pos">{esc(v["positioning"])}</p>
  {f'<p class="capnote">{esc(v["capability_note"])}</p>' if v.get("capability_note") else ''}
  <dl class="kv">
    <dt>Subscription</dt><dd>{esc(v["subscription_model"])}</dd>
    <dt>Recurring cost</dt><dd>{esc(v["recurring_note"])}</dd>
    <dt>Stop paying &mdash; what happens?</dt>
    <dd>{esc(v["stops_paying_answer"])} {tag_badge(v.get("stops_paying_tag"))}</dd>
    <dt>4-room figure</dt>
    <dd>{money(fr.get("hardware", 0))} hardware
      {f'+ {money(fr["install"])} implementation' if fr.get("install") else ''}
      {f', {money(fr["recurring_per_year"])}/yr recurring' if fr.get("recurring_per_year") else ', no recurring'}
      {tag_badge(fr.get("tag"))} {conf_badge(fr.get("confidence"), fr.get("confidence_note"))}
      {f'<div class="note">{esc(fr["confidence_note"])}</div>' if fr.get("confidence_note") else ''}
      {f'<div class="note">{esc(fr["canopy_note"])}</div>' if fr.get("canopy_note") else ''}
      <div class="note">Source: <a href="{esc(fr.get("source", "#"))}" target="_blank" rel="noopener noreferrer">{esc(fr.get("source_label", ""))}</a></div>
    </dd>
  </dl>
  {f'<ul class="cites">{cites}</ul>' if cites else ''}
</div>'''

    out = (tpl
           .replace("__DATA__", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
           .replace("__VENDORS__", vend_html)
           .replace("__AGAINST_PREAMBLE__", esc(against["preamble"]))
           .replace("__AGAINST__", against_html)
           .replace("__NOTOBTAINABLE__", notob_html)
           .replace("__HIDDEN__", hidden_html)
           .replace("__RECS__", rec_html)
           .replace("__REC_CLASS__", esc(recs.get("evidence_class", "")))
           .replace("__MIDDLE_HEAD__", esc(data["middle_path"]["headline"]))
           .replace("__MIDDLE__", esc(data["middle_path"]["detail"]))
           .replace("__METHODOLOGY__", esc(data["meta"]["methodology"]))
           .replace("__RESEARCH_DATE__", esc(data["meta"]["research_date"]))
           .replace("__DIY_PER_ROOM__", money(diy_per_room))
           .replace("__FX__", f'1 {fx.get("base")} = {(fx.get("rates") or {}).get("USD")} USD'
                              f' (rate date {fx.get("rate_date")})'))

    os.makedirs(DOCS, exist_ok=True)
    path = os.path.join(DOCS, "diy-vs-proprietary.html")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)

    size = os.path.getsize(path) / 1024
    print(f"docs/diy-vs-proprietary.html  {size:.0f} KB")
    print(f"  DIY per room {money(diy_per_room)} = controller {money(diy_room)}"
          f" + substrate {money(diy_substrate)}  [derived from recipes]")
    print(f"  {len(data['vendors'])} vendors, {len(data['not_obtainable'])} not-obtainable,"
          f" {len(against['points'])} DIY counterpoints")
    return 0


if __name__ == "__main__":
    sys.exit(main())
