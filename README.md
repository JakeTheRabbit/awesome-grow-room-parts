# Awesome Grow Room Parts

A parts catalogue for automated grow rooms, where **the quality ratings are
earned from evidence instead of asserted**.

Most "awesome" hardware lists are a pile of links someone thought looked good.
This one starts from a different question: *which of these parts has actually
survived in a production room, and how do we know?*

The seed data comes from a real commercial indoor growing operation — 149 live
ESPHome device configs across three flower/veg rooms, a drying room and back of
house. A part tagged **field-proven** is named in a stated number of those live
configs, and the filenames are recorded in the entry so you can check the claim.
A part tagged **avoid** has a documented reason, usually "someone already tried
this here and it did not work".

Everything beyond that seed is contributable. If you have run a part in anger,
[send it in](CONTRIBUTING.md).

**→ [Browse the catalogue site](https://jaketherabbit.github.io/awesome-grow-room-parts/)**
· searchable, filterable, with a copy-paste config example per part and an
[I²C address collision map](#the-i²c-collision-map).

---

## DIY vs proprietary — what the platforms actually cost

**→ [Read the cost comparison](https://jaketherabbit.github.io/awesome-grow-room-parts/diy-vs-proprietary.html)**

A sourced comparison of AROYA, Growlink, TrolMaster, Pulse Grow and Argus against a
DIY build, with an interactive break-even calculator. Every figure carries the
confidence level and the source it came from, and modelled numbers are not presented
with the same weight as published ones.

The table groups by what each product actually **does**, because a monitor and a
controller are not substitutes and ranking them together implies they are.
Runs the room: **TrolMaster ~$6.4k · Growlink ~$27k · Argus ~$51k** at four rooms over
five years (Argus's own published 9-zone cannabis example is ~$195k, 2018 dollars).
Analytics rather than control: **AROYA ~$76k** at 8,000 sq ft canopy.
Monitoring only, and not a substitute for a controller: **Grow Sensor ~$3.8k ·
Pulse ~$12k**.

Some of what the research turned up:

- **AROYA's commercial subscription tiers are published in their ROI calculator's page
  JavaScript** — $150–$3,900/month, billed per canopy square foot facility-wide. They
  corroborate three independent user-reported quotes, including one that an AROYA
  employee publicly disputed.
- **"No subscription" is not the same as no recurring cost.** TrolMaster's app is free,
  but their own API Gateway page charges $15/month per device for programmatic access
  to your own data.
- **Only two of five vendors will say what happens to your hardware if you stop paying.**
  TrolMaster and Pulse both answer it. AROYA's FAQ declines and routes to a sales demo.
  Growlink's Terms of Service contains no "Effect of Termination" clause at all.
- **Monitoring is not control.** Pulse Grow and Grow Sensor are monitoring and alerting
  platforms with no relay outputs and no equipment control — they cannot run a room, and
  the page groups them separately rather than listing their cost beside a controller's.
- **Priva and iUNU could not be priced at all** — not published anywhere, including
  through distributors. iUNU has also exited cannabis: their own contact form no longer
  lists it as a crop.

The page also reproduces, in full and unsoftened, **the case against DIY** — no support
contract, no warranty, you are the integrator, calibration is your problem, no compliance
audit trail, key-person risk. You should be able to read that section and reasonably
decide to buy. If it were not there, the rest would not be worth trusting.

---

## Start here

| | |
|---|---|
| 🚿 **[SAFETY.md](SAFETY.md)** | The three-part pattern that stops a network blip flooding a room. **Read this before you wire a valve to anything.** |
| 🔌 **[Build recipes](recipes/)** | Complete BOMs with auto-calculated totals: budget tent monitor, PoE room controller, multi-zone substrate array. |
| 🧭 **[I²C collision map](#the-i²c-collision-map)** | Every part's bus address side by side, so you find conflicts while planning instead of while soldering. |
| ✍️ **[CONTRIBUTING.md](CONTRIBUTING.md)** | The part template and what counts as evidence. |

---

## How the quality tiers work

| Tier | What it means |
|---|---|
| **field-proven** | Named in ≥3 live production device configs. The count and the filenames are in the entry. |
| **works** | Known good, but not deployed at scale here — or deployed once and uneventful. |
| **experimental** | Someone got it running. Not yet trustworthy for anything load-bearing. |
| **avoid** | Documented dead end. The entry says exactly what went wrong. |

The tier is not an opinion field. CI enforces that anything claiming
**field-proven** carries `deployment_count ≥ 3` **and** the list of config
filenames backing it, and that anything marked **avoid** states its
`failure_modes`.

### Why "deployment count" and not star ratings

A five-star review tells you someone liked a part on the day it arrived. A
deployment count tells you the part is still in a wall, in a hot humid room,
eighteen months later, and nobody has ripped it out. Those are very different
claims. This catalogue only makes the second one.

---

## The I²C collision map

The single most annoying failure when building a sensor node: two parts that
both want the same I²C address, discovered *after* everything is mounted.

The [site's I²C page](https://jaketherabbit.github.io/awesome-grow-room-parts/)
lists every part by address, flags every collision, and shows which parts can be
strapped to an alternate. It also handles composite modules properly — an M5Stack
ENV.III is *two* chips occupying **0x44** and **0x70**, and that second address
is what silently collides with a TCA9548A multiplexer's default. That is exactly
the kind of thing you want to find on a web page rather than with a logic analyser.

Known collisions in the current catalogue: `0x28`, `0x44`, `0x51`, `0x62`,
`0x69`, `0x70`, `0x76`.

---

## Data model

The catalogue is **data first**. One YAML file per part in [`parts/`](parts/),
validated in CI against [`schema/part.schema.json`](schema/part.schema.json).
The README tables, the website and the recipe totals are all generated from it —
nothing is maintained by hand in two places.

```
parts/<id>.yaml        one part, schema-validated
recipes/<id>.yaml      a BOM referencing parts by id
schema/                the JSON Schema
assets/parts/          self-hosted thumbnails (never hotlinked)
docs/                  generated static site (GitHub Pages)
scripts/               validate · build site · generate README · check links
```

Vendor links rot, so every entry also records canonical
`part_numbers`. When a shop URL dies, the part is still findable — and
`scripts/check_links.py` only fails the build if a part has *no* reachable
vendor **and** no part number to search on.

### Regenerate everything

```bash
python scripts/validate.py        # schema + cross-refs + secret scan
python scripts/gen_thumbnails.py  # placeholder art for any part missing an image
python scripts/build_site.py      # -> docs/
python scripts/gen_readme.py      # -> the tables below
python scripts/check_links.py     # vendor/driver link rot
```

---

<!-- AUTOGEN:PARTS START -->

_66 parts. Generated from `parts/*.yaml` by `scripts/gen_readme.py` — edit the YAML, not this table._

_Prices: each part records **one** price - what was actually paid, in the currency it was paid in. Figures marked `~` are **derived, not quoted**, converted at `1 NZD = 0.5879 USD` (rate date 2026-08-01; see [`data/fx.yaml`](data/fx.yaml)). Rates move, so treat the band as the durable signal. Parts with no observed price show a band only. `^r` = from a purchase receipt (what was actually paid); `^l` = a vendor listing; unmarked = an estimate._

### Field-proven core

Parts named in the stated number of live production ESPHome device configs.

| Part | Live configs | Bus | I²C | Price | Notes |
|---|---:|---|---|---|---|
| [M5Stack PoESP32 / ESP32 Ethernet unit (IP101G PHY)](parts/m5stack-poesp32.yaml) | 48 | Ethernet/PoE/Grove/I2C/UART |  | NZ$65.00 (~US$38.21) | PoE ESP32 node with wired Ethernet PHY |
| [Sensirion SCD41 true NDIR CO2 sensor](parts/sensirion-scd41.yaml) | 29 | I2C/Grove | 0x62 | NZ$77.11 (~US$45.33) ^l | CO2 / temperature / humidity |
| [MFRC522 / RC522 13.56 MHz RFID reader](parts/mfrc522-rfid.yaml) | 19 | I2C/SPI | 0x28 | NZ$8.00 (~US$4.70) | 13.56 MHz MIFARE reader |
| [M5Stack 4-Relay Unit](parts/m5stack-4relay.yaml) | 18 | I2C/Grove | 0x26 | NZ$22.72 (~US$13.36) ^r | 4-channel I2C relay module, Grove |
| [M5Stack ATOM Lite (ESP32-PICO)](parts/m5stack-atom-lite.yaml) | 14 | WiFi/BLE/I2C/UART/Grove/GPIO |  | NZ$18.00 (~US$10.58) | Compact WiFi ESP32 |
| [METER TEROS 12 substrate VWC / EC / temperature probe](parts/meter-teros12.yaml) | 14 | SDI-12 |  | NZ$430.00 (~US$252.80) | SDI-12 dielectric probe |
| [PCF8563 real-time clock](parts/pcf8563-rtc.yaml) | 13 | I2C | 0x51 | NZ$6.00 (~US$3.53) | I2C real-time clock with battery backup |
| [TCA9548A 8-channel I2C multiplexer](parts/tca9548a-mux.yaml) | 9 | I2C | 0x70 | NZ$12.00 (~US$7.05) | 1-to-8 I2C switch |
| [M5Stack AirQ (SEN55 + SCD40 air quality node)](parts/m5stack-airq.yaml) | 8 | I2C/WiFi/BLE | 0x69 | NZ$145.00 (~US$85.25) | Integrated multi-sensor node |
| [Sensirion SEN55 PM / VOC / NOx / T / RH module](parts/sensirion-sen55.yaml) | 8 | I2C | 0x69 | NZ$125.00 (~US$73.49) | Particulate + VOC + NOx |
| [SSR-25DA solid state relay](parts/ssr-25da.yaml) | 8 | GPIO |  | NZ$18.00 (~US$10.58) | DC-controlled AC solid state relay |
| [Hunter PGV 24 VAC irrigation solenoid valve](parts/hunter-pgv-solenoid.yaml) | 6 | Mains |  | NZ$47.06 (~US$27.67) ^r | 24 VAC in-line solenoid zone valve |
| [Infiwin MT22 SDI-12 substrate probe](parts/infiwin-mt22.yaml) | 6 | SDI-12 |  | NZ$85.00 (~US$49.97) | SDI-12 dielectric probe (budget) |
| [Netafim white lateral dripline pipe (20 mm, 3 bar)](parts/netafim-lateral-pipe.yaml) | 6 | None |  | NZ$182.00 (~US$107.00) ^r _per 200 m roll_ | 20 mm LDPE lateral, 200 m roll |
| [Netafim PCJ pressure-compensating dripper](parts/netafim-pcj-dripper.yaml) | 6 | None |  | NZ$1.23 (~US$0.72) ^r _per dripper, incl. spike and tube_ | Pressure-compensating emitter with spike and tube |
| [M5Stack Dial (round display + rotary encoder + RFID)](parts/m5stack-dial.yaml) | 5 | I2C/SPI/WiFi/Grove/GPIO | 0x28 | NZ$110.00 (~US$64.67) | Round touch display node |
| [Sensirion SHT30 temperature & humidity sensor](parts/sensirion-sht30.yaml) | 5 | I2C | 0x44 | NZ$12.00 (~US$7.05) | Temperature / humidity |
| [Amiad 25 mm compact screen filter (130 micron)](parts/amiad-screen-filter.yaml) | 4 | None |  | NZ$48.82 (~US$28.70) ^r | In-line screen filter, stainless element |
| [HX711 24-bit load cell amplifier](parts/hx711-adc.yaml) | 4 | GPIO |  | NZ$6.00 (~US$3.53) | Load cell front end |
| [Load cell (50kg half-bridge or 200kg bar)](parts/load-cell-50kg.yaml) | 4 | Analog |  | NZ$15.00 (~US$8.82) | Strain gauge load cell |
| [M5Stack ENV III Unit (SHT30 + QMP6988)](parts/m5-env3.yaml) | 4 | I2C/Grove | 0x44 | NZ$18.00 (~US$10.58) | Temperature / humidity / pressure |
| [MLX90640 32x24 thermal camera array](parts/mlx90640-thermal.yaml) | 4 | I2C | 0x33 | NZ$115.50 (~US$67.90) ^l | 32x24 far-infrared thermopile array |
| [Peristaltic dosing pump (12/24V, relay or PWM driven)](parts/peristaltic-pump-doser.yaml) | 4 | GPIO/PWM/UART |  | NZ$51.32 (~US$30.17) ^r | Nutrient dosing pump |
| [25 mm PVC pressure pipe (PN12)](parts/pvc-pressure-pipe-25.yaml) | 4 | None |  | NZ$15.49 (~US$9.11) ^r _per 5.8 m length_ | Rigid mains-side distribution pipe |
| [240 V to 24 VAC 150 VA transformer](parts/transformer-24vac.yaml) | 4 | Mains |  | NZ$95.90 (~US$56.38) ^r | Mains-to-24 VAC supply for solenoid valves |
| [Tygon A-60-G chemical-resistant peristaltic tubing](parts/tygon-chemical-tubing.yaml) | 4 | None |  | NZ$14.59 (~US$8.58) ^r _per metre_ | Peristaltic pump tubing, chemical dispensing grade |
| [Growlink TerraLink substrate probe](parts/growlink-terralink.yaml) | 3 | SDI-12 |  | $$$ | SDI-12 dielectric probe |
| [24VAC irrigation solenoid valve](parts/solenoid-valve-24vac.yaml) | 3 | Mains |  | NZ$47.06 (~US$27.67) ^r | Zone valve |

### Hall of shame

Documented dead ends. Listed so nobody repeats the work.

| Part | Why it is here |
|---|---|
| [Seeed LeapMMW 24 GHz mmWave presence radar](parts/seeed-leapmmw-mmwave.yaml) | Written and debugged, then abandoned before a single production deployment - the component is dead code. |
| [ZPHS01B all-in-one air quality module](parts/zphs01b-multigas.yaml) | The shipped lambdas return `{}` (no value) rather than a reading - the integration was never finished. |

### Everything, by category

#### Access control & presence

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [MFRC522 / RC522 13.56 MHz RFID reader](parts/mfrc522-rfid.yaml) | **field-proven** | 19 | I2C/SPI | 0x28 | NZ$8.00 (~US$4.70) |
| [Seeed LeapMMW 24 GHz mmWave presence radar](parts/seeed-leapmmw-mmwave.yaml) | **avoid** |  | UART |  | NZ$40.00 (~US$23.52) |

#### Actuation & relays

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack 4-Relay Unit](parts/m5stack-4relay.yaml) | **field-proven** | 18 | I2C/Grove | 0x26 | NZ$22.72 (~US$13.36) ^r |
| [SSR-25DA solid state relay](parts/ssr-25da.yaml) | **field-proven** | 8 | GPIO |  | NZ$18.00 (~US$10.58) |
| [M5Stack 2-channel SPST relay unit](parts/m5stack-2ch-relay.yaml) | works |  | I2C/Grove | 0x25 | NZ$24.75 (~US$14.55) ^l |
| [KinCony F16 16-channel relay controller](parts/kincony-f16-relay.yaml) | experimental | 1 | Ethernet/RS485/Modbus/I2C | 0x24 | NZ$210.00 (~US$123.46) |

#### Air quality & CO2

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [Sensirion SCD41 true NDIR CO2 sensor](parts/sensirion-scd41.yaml) | **field-proven** | 29 | I2C/Grove | 0x62 | NZ$77.11 (~US$45.33) ^l |
| [M5Stack AirQ (SEN55 + SCD40 air quality node)](parts/m5stack-airq.yaml) | **field-proven** | 8 | I2C/WiFi/BLE | 0x69 | NZ$145.00 (~US$85.25) |
| [Sensirion SEN55 PM / VOC / NOx / T / RH module](parts/sensirion-sen55.yaml) | **field-proven** | 8 | I2C | 0x69 | NZ$125.00 (~US$73.49) |
| [Sensirion SHT30 temperature & humidity sensor](parts/sensirion-sht30.yaml) | **field-proven** | 5 | I2C | 0x44 | NZ$12.00 (~US$7.05) |
| [M5Stack ENV III Unit (SHT30 + QMP6988)](parts/m5-env3.yaml) | **field-proven** | 4 | I2C/Grove | 0x44 | NZ$18.00 (~US$10.58) |
| [Bosch BME680 gas / T / RH / pressure sensor](parts/bosch-bme680.yaml) | works | 1 | I2C/SPI | 0x76 | NZ$28.00 (~US$16.46) |
| [Bosch BMP280 pressure & temperature sensor](parts/bosch-bmp280.yaml) | works | 1 | I2C/SPI | 0x76 | NZ$6.00 (~US$3.53) |
| [ComWinTop CWT-LEAF-TH-S-N leaf surface temperature & wetness sensor](parts/cwt-leaf-th.yaml) | works | 1 | RS485/Modbus |  | NZ$95.00 (~US$55.85) |
| [Sensirion SHT40 temperature & humidity sensor](parts/sensirion-sht40.yaml) | works | 1 | I2C | 0x44 | NZ$14.00 (~US$8.23) |
| [Bosch BME280 temperature / humidity / pressure sensor](parts/bosch-bme280.yaml) | works |  | I2C/SPI | 0x76 | NZ$9.00 (~US$5.29) |
| [Sensirion SCD30 NDIR CO2 sensor](parts/sensirion-scd30.yaml) | works |  | I2C | 0x61 | NZ$105.00 (~US$61.73) |
| [Sensirion SCD40 NDIR CO2 sensor](parts/sensirion-scd40.yaml) | works |  | I2C/Grove | 0x62 | NZ$40.00 (~US$23.52) |
| [ComWinTop CWT-SWS-C wind speed sensor](parts/cwt-sws-wind.yaml) | experimental |  | RS485/Modbus |  | $$ |
| [ZPHS01B all-in-one air quality module](parts/zphs01b-multigas.yaml) | **avoid** |  | UART |  | NZ$180.00 (~US$105.82) |

#### Bus infrastructure

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [PCF8563 real-time clock](parts/pcf8563-rtc.yaml) | **field-proven** | 13 | I2C | 0x51 | NZ$6.00 (~US$3.53) |
| [TCA9548A 8-channel I2C multiplexer](parts/tca9548a-mux.yaml) | **field-proven** | 9 | I2C | 0x70 | NZ$12.00 (~US$7.05) |
| [MAX485 / SP3485 RS485-to-TTL transceiver](parts/rs485-ttl-transceiver.yaml) | works | 2 | RS485/Modbus/UART |  | NZ$8.00 (~US$4.70) |

#### Controllers & boards

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack ATOM Lite (ESP32-PICO)](parts/m5stack-atom-lite.yaml) | **field-proven** | 14 | WiFi/BLE/I2C/UART/Grove/GPIO |  | NZ$18.00 (~US$10.58) |
| [M5Stack AtomS3 Lite (ESP32-S3)](parts/m5stack-atoms3-lite.yaml) | works | 25 | WiFi/BLE/I2C/UART/Grove/USB/GPIO |  | NZ$22.00 (~US$12.93) |
| [WT32-ETH01 (ESP32 + LAN8720 Ethernet)](parts/wt32-eth01.yaml) | works |  | Ethernet/UART/I2C/GPIO |  | NZ$20.00 (~US$11.76) |

#### Displays & HMI

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack Dial (round display + rotary encoder + RFID)](parts/m5stack-dial.yaml) | **field-proven** | 5 | I2C/SPI/WiFi/Grove/GPIO | 0x28 | NZ$110.00 (~US$64.67) |

#### Energy monitoring

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [Shelly Pro 3EM three-phase energy meter](parts/shelly-pro-3em.yaml) | works |  | Ethernet/WiFi/Mains |  | NZ$249.99 (~US$146.97) ^l |

#### Irrigation hardware

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [Hunter PGV 24 VAC irrigation solenoid valve](parts/hunter-pgv-solenoid.yaml) | **field-proven** | 6 | Mains |  | NZ$47.06 (~US$27.67) ^r |
| [Netafim PCJ pressure-compensating dripper](parts/netafim-pcj-dripper.yaml) | **field-proven** | 6 | None |  | NZ$1.23 (~US$0.72) ^r _per dripper, incl. spike and tube_ |
| [Netafim white lateral dripline pipe (20 mm, 3 bar)](parts/netafim-lateral-pipe.yaml) | **field-proven** | 6 | None |  | NZ$182.00 (~US$107.00) ^r _per 200 m roll_ |
| [240 V to 24 VAC 150 VA transformer](parts/transformer-24vac.yaml) | **field-proven** | 4 | Mains |  | NZ$95.90 (~US$56.38) ^r |
| [25 mm PVC pressure pipe (PN12)](parts/pvc-pressure-pipe-25.yaml) | **field-proven** | 4 | None |  | NZ$15.49 (~US$9.11) ^r _per 5.8 m length_ |
| [Amiad 25 mm compact screen filter (130 micron)](parts/amiad-screen-filter.yaml) | **field-proven** | 4 | None |  | NZ$48.82 (~US$28.70) ^r |
| [24VAC irrigation solenoid valve](parts/solenoid-valve-24vac.yaml) | **field-proven** | 3 | Mains |  | NZ$47.06 (~US$27.67) ^r |
| [Netafim automatic line flush valve (16 mm)](parts/netafim-line-flush-valve.yaml) | works | 2 | None |  | NZ$12.38 (~US$7.28) ^r |
| [Senninger 20 psi fixed pressure regulator](parts/senninger-pressure-regulator.yaml) | works | 2 | None |  | NZ$22.32 (~US$13.12) ^r |
| [Adjustable pressure reducing valve (15-50 mm)](parts/pressure-reducing-valve.yaml) | works | 1 | None |  | NZ$152.15 (~US$89.45) ^r |

#### Light measurement

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [BH1750 ambient light sensor](parts/bh1750.yaml) | works | 2 | I2C | 0x23 | NZ$7.00 (~US$4.12) |
| [AS7341 11-channel spectral sensor](parts/as7341.yaml) | works |  | I2C | 0x39 | NZ$48.00 (~US$28.22) |
| [ComWinTop CWT-PS PAR / quantum sensor](parts/cwt-ps-par.yaml) | experimental |  | RS485/Modbus |  | $$ |

#### Networking & power

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack PoESP32 / ESP32 Ethernet unit (IP101G PHY)](parts/m5stack-poesp32.yaml) | **field-proven** | 48 | Ethernet/PoE/Grove/I2C/UART |  | NZ$65.00 (~US$38.21) |
| [W5500 SPI Ethernet module](parts/w5500-eth-module.yaml) | works | 2 | SPI/Ethernet |  | NZ$12.00 (~US$7.05) |

#### Substrate sensing

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [METER TEROS 12 substrate VWC / EC / temperature probe](parts/meter-teros12.yaml) | **field-proven** | 14 | SDI-12 |  | NZ$430.00 (~US$252.80) |
| [Infiwin MT22 SDI-12 substrate probe](parts/infiwin-mt22.yaml) | **field-proven** | 6 | SDI-12 |  | NZ$85.00 (~US$49.97) |
| [Growlink TerraLink substrate probe](parts/growlink-terralink.yaml) | **field-proven** | 3 | SDI-12 |  | $$$ |
| [Chill Division SDI-12 substrate sensor](parts/chill-division-sdi12.yaml) | works |  | SDI-12/WiFi |  | $$ |
| [THC-S RS485 soil moisture / EC / temperature probe](parts/thc-s-rs485.yaml) | works |  | RS485/Modbus |  | NZ$45.00 (~US$26.46) |

#### Thermal & optical

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [MLX90640 32x24 thermal camera array](parts/mlx90640-thermal.yaml) | **field-proven** | 4 | I2C | 0x33 | NZ$115.50 (~US$67.90) ^l |
| [MLX90614 non-contact IR thermometer (M5Stack NCIR)](parts/mlx90614-ncir.yaml) | works |  | I2C/Grove | 0x5a | NZ$33.52 (~US$19.71) ^l |

#### Water & fertigation

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [HX711 24-bit load cell amplifier](parts/hx711-adc.yaml) | **field-proven** | 4 | GPIO |  | NZ$6.00 (~US$3.53) |
| [Load cell (50kg half-bridge or 200kg bar)](parts/load-cell-50kg.yaml) | **field-proven** | 4 | Analog |  | NZ$15.00 (~US$8.82) |
| [Peristaltic dosing pump (12/24V, relay or PWM driven)](parts/peristaltic-pump-doser.yaml) | **field-proven** | 4 | GPIO/PWM/UART |  | NZ$51.32 (~US$30.17) ^r |
| [Tygon A-60-G chemical-resistant peristaltic tubing](parts/tygon-chemical-tubing.yaml) | **field-proven** | 4 | None |  | NZ$14.59 (~US$8.58) ^r _per metre_ |
| [Ultrasonic distance sensor for tank level](parts/ultrasonic-tank-sensor.yaml) | works | 3 | GPIO/UART/I2C | 0x57 | NZ$25.00 (~US$14.70) |
| [Metric food-grade push-to-connect check valve (10 mm)](parts/foodgrade-check-valve.yaml) | works | 2 | None |  | NZ$31.50 (~US$18.52) ^r |
| [Float switch (tank level interlock)](parts/float-switch.yaml) | works | 1 | GPIO |  | NZ$13.65 (~US$8.02) ^r |
| [Submersible clean/dirty water transfer pump (750 W)](parts/submersible-transfer-pump.yaml) | works | 1 | Mains |  | $$ |
| [DS18B20 1-Wire temperature probe](parts/ds18b20.yaml) | works |  | 1-Wire |  | NZ$9.00 (~US$5.29) |
| [Atlas Scientific EZO-EC conductivity circuit + probe](parts/atlas-ezo-ec.yaml) | experimental | 1 | I2C/UART | 0x64 | NZ$245.00 (~US$144.04) |
| [Atlas Scientific EZO-RTD temperature circuit + PT-1000 probe](parts/atlas-ezo-rtd.yaml) | experimental | 1 | I2C/UART | 0x66 | NZ$140.00 (~US$82.31) |
| [Atlas Scientific EZO-pH circuit + probe](parts/atlas-ezo-ph.yaml) | experimental | 1 | I2C/UART | 0x63 | NZ$230.00 (~US$135.22) |
| [DFRobot Gravity analog ORP sensor](parts/dfrobot-gravity-orp.yaml) | experimental | 1 | Analog |  | NZ$80.00 (~US$47.03) |
| [Chill Division ABD automated batch doser (STM32, hw v2.1)](parts/stm32-abd-doser.yaml) | experimental |  | UART/GPIO |  | $$$ |
| [ComWinTop CWT-BL-EC-4400-S inline EC sensor](parts/cwt-bl-ec-4400.yaml) | experimental |  | RS485/Modbus |  | $$ |
| [ComWinTop CWT-WLS RS485 water level sensor](parts/cwt-wls-water-level.yaml) | experimental |  | RS485/Modbus |  | $$ |

<!-- AUTOGEN:PARTS END -->

---

## Provenance and honesty

- **Deployment counts** were derived by scanning 149 ESPHome device configs for
  *active* (uncommented) component blocks. Archived and backup configs were
  excluded. Where a count looked ambiguous it is explained in the entry's
  `evidence` field.
- **Prices** are indicative, mostly NZD, with the observation date recorded.
  They will drift. Treat the band (`$`–`$$$$`) as the durable signal.
- **Config examples** are distilled from real production configs and have been
  **scrubbed** of credentials — see [SECURITY.md](SECURITY.md). They use
  `!secret` placeholders; they are not drop-in copies of anyone's live system.
- This is one facility's experience. It is a strong signal, not a universal
  truth — a part that failed here may work fine in your conditions, and vice
  versa. Contributions that contradict the seed data with evidence are welcome.

## Product images

Thumbnails are **self-hosted**, never hotlinked — a vendor reorganising their CDN
must not break the catalogue. Each image is downloaded, normalised to a square
white-backed PNG at two sizes, and committed.

Product images remain **the property of their respective manufacturers and
vendors**, and are reproduced here for the sole purpose of identifying the part
being catalogued. Every image records `image_source` and `image_source_url` in
its part file, so the origin of any picture is traceable in one step.

Preference order when sourcing: the manufacturer's own product page or press
kit, then a vendor listing, then nothing. Where no usable image is found the
entry keeps a generated placeholder — a truthful placeholder beats a wrong or
misleading picture.

**Takedown:** if you hold rights to an image here and would like it removed,
open an issue on this repository, or contact the maintainer through the GitHub
profile linked from it. Images are removed on request, no argument — the entry
falls back to a generated placeholder and nothing else about it changes.

## Licence

Catalogue data and documentation: [CC BY 4.0](LICENSE).
Scripts and site code: [MIT](LICENSE-CODE).
