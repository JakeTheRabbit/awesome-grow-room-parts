# Contributing

The whole value of this list is that its claims are checkable. So the bar for a
contribution is not "is this a good part" — it is **"can someone else verify what
you said about it"**.

## Before you open a PR

```bash
pip install pyyaml jsonschema
python scripts/validate.py     # must print 0 errors
python scripts/build_site.py   # regenerate docs/
python scripts/gen_readme.py   # regenerate the README tables
```

CI runs the same three. A red build is almost always the schema telling you
something specific — read the error, it names the field.

---

## Adding a part

Create `parts/<id>.yaml`. The filename **must** match the `id` field, and the
`id` is permanent once merged — recipes and cross-references point at it.

Copy this template:

```yaml
id: my-sensor-x1                    # lowercase-kebab, matches the filename
name: Acme X1 substrate probe
manufacturer: Acme
part_numbers: [X1, X1-SDI]          # canonical PNs — the fallback when links die
category: Substrate sensing         # must be one of the schema's categories
subcategory: SDI-12 dielectric probe
bus: [SDI-12]

# Required for anything sitting on an I2C bus — this feeds the collision map.
# i2c:
#   address: "0x44"
#   alternates: ["0x45"]            # addresses it can MOVE to (escape routes)
#   also_occupies: ["0x70"]         # addresses it ALSO holds (composite modules)
#   configurable: true
#   how_to_change: Pull ADDR high for 0x45.

protocol_settings: SDI-12, 1200 baud 7-E-1 half duplex
voltage: { min: 3.6, max: 15.0, nominal: 12.0 }
price:
  band: "$$"                        # $ <25, $$ 25-100, $$$ 100-500, $$$$ 500+
  observed: 85.0
  currency: NZD
  observed_date: "2026-03-01"
vendors:
  - name: Acme Direct
    url: https://example.com/x1
    part_number: X1-SDI
    region: Global
ip_rating: IP68                     # or 'none' for a bare board, or 'unknown'
calibration_required: media-specific
calibration_notes: >-
  Raw counts are not VWC. Needs a substrate-specific curve.

quality_tier: works                 # see the tier rules below
deployment_count: 2
deployment_evidence:                # FILENAMES ONLY — never file contents
  - my-room-node.yaml
  - my-second-node.yaml
evidence: >-                        # REQUIRED. Why this tier, in a sentence or two.
  Two nodes running 8 months in coco under drip. No dropouts.

failure_modes:                      # how it actually breaks. Be specific.
  - Reads high for the first ~30 min after insertion until the medium settles.
notes: >-
  Anything a buyer would want to know that does not fit above.
drivers:
  - name: ESPHome sdi12 (external)
    url: https://github.com/ssieb/esphome_components
    kind: esphome-external
platforms: [ESPHome, Home Assistant]   # ecosystems it works with
works_with: [m5stack-atom-lite]         # ids of other parts — must exist
alternatives: [meter-teros12]           # ids of parts doing the same job
image: assets/parts/my-sensor-x1.svg
example:
  lang: yaml
  title: Acme X1 on a half-duplex SDI-12 bus
  source: my-room-node.yaml
  code: |
    sensor:
      - platform: sdi12
        address: 0
tags: [substrate, sdi-12, vwc]
```

Then generate a thumbnail and validate:

```bash
python scripts/gen_thumbnails.py   # makes a placeholder if you have no photo
python scripts/validate.py
```

---

## The tier rules

| Tier | Requirement |
|---|---|
| `field-proven` | **≥3** live deployments, `deployment_count` set, and the config filenames listed. Enforced by CI. |
| `works` | You have run it. Say for how long and in what conditions in `evidence`. |
| `experimental` | You got it working but would not trust it with a crop yet. |
| `avoid` | Requires `failure_modes`. Enforced by CI. |

**`field-proven` is not "the datasheet looks good".** It means the part is
installed, in service, and has stayed there. If you are describing a part you
bought and bench-tested, that is `works` at best.

`avoid` needs to be about the *part*, not your afternoon. "I could not get the
library to compile" is not an `avoid`; "the electrochemical cell drifts 20% in
six months and cannot be recalibrated" is.

---

## Never commit credentials

**This is the one rule that will get a PR closed rather than reviewed.**

The example configs in this repo are distilled from real production systems.
Real ESPHome configs contain API encryption keys, OTA passwords, WiFi SSIDs and
passwords, static IPs, MAC addresses, and RFID card UIDs. None of that may ever
land here.

When lifting an example from a working config, replace:

| Real thing | Put this instead |
|---|---|
| `api: encryption: key: "<44-char base64>"` | `key: !secret api_encryption_key` |
| `ota: password: "<32 hex>"` | `password: !secret ota_password` |
| `wifi: ssid:` / `password:` | `!secret wifi_ssid` / `!secret wifi_password` |
| AP fallback password | `!secret ap_password` |
| `manual_ip:` / real IPs | remove, or `192.168.1.x` |
| MAC addresses | remove |
| RFID `uid: "A1-B2-C3-D4"` | `uid: "00-00-00-00"` |
| RTSP camera URLs with credentials | remove entirely |

`scripts/validate.py` scans every part file for these patterns and **fails the
build** on a hit. It is a safety net with false positives, not a substitute for
looking at what you paste. If it flags something genuinely safe, make the value
obviously a placeholder (`YOUR_...`, `CHANGE_ME`) rather than working around the
scanner.

See [SECURITY.md](SECURITY.md).

---

## Images

Self-host in `assets/parts/`. **Do not hotlink marketplace images** — AliExpress
and eBay image URLs rot within months and would leave dead tiles across the site.

- Have a photo? Drop it in as `<id>.png|jpg|webp` and point `image:` at it.
  `gen_thumbnails.py` will not overwrite a real photo.
- No photo? Run `gen_thumbnails.py` and ship the generated placeholder. A clean
  placeholder beats a blank tile, and beats someone else's copyrighted product shot.
- Only upload photos you took or that are licensed for reuse. Note the source in
  `image_credit`.

---

## Adding a build recipe

`recipes/<id>.yaml`, referencing parts **by id** so totals stay correct
automatically:

```yaml
id: my-build
name: My build
summary: One paragraph on what this is for and what it does not do.
skill_level: beginner            # beginner | intermediate | advanced
estimated_build_time: 2 hours
network: WiFi
items:
  - part: sensirion-scd41        # must be an existing part id
    qty: 1
    role: What this part does in THIS build.
notes: Bus addresses, gotchas, wiring order.
watch_out: The thing that will actually bite someone.
```

If the build can move water, gas or heat, its `watch_out` must point at
[SAFETY.md](SAFETY.md).

---

## Style

- Write what you observed, not what the marketing says.
- Prefer specific over safe: "welds closed after ~50k inductive switching cycles"
  beats "may be unreliable".
- Contradicting the existing seed data is welcome — bring your evidence and we
  will note both. One facility's experience is a strong signal, not a law.
- Keep prose tight. Every field has a length cap in the schema; if you are
  hitting it, you are probably writing a blog post.
