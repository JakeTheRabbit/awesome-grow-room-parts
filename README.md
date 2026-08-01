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

_51 parts. Generated from `parts/*.yaml` by `scripts/gen_readme.py` — edit the YAML, not this table._

### Field-proven core

Parts named in the stated number of live production ESPHome device configs.

| Part | Live configs | Bus | I²C | Price | Notes |
|---|---:|---|---|---|---|
| [M5Stack PoESP32 / ESP32 Ethernet unit (IP101G PHY)](parts/m5stack-poesp32.yaml) | 48 | Ethernet/PoE/Grove/I2C/UART |  | NZD 65.0 | PoE ESP32 node with wired Ethernet PHY |
| [Sensirion SCD41 true NDIR CO2 sensor](parts/sensirion-scd41.yaml) | 29 | I2C/Grove | 0x62 | NZD 52.0 | CO2 / temperature / humidity |
| [MFRC522 / RC522 13.56 MHz RFID reader](parts/mfrc522-rfid.yaml) | 19 | I2C/SPI | 0x28 | NZD 8.0 | 13.56 MHz MIFARE reader |
| [M5Stack 4-Relay Unit](parts/m5stack-4relay.yaml) | 18 | I2C/Grove | 0x26 | NZD 38.0 | 4-channel I2C relay module, Grove |
| [M5Stack ATOM Lite (ESP32-PICO)](parts/m5stack-atom-lite.yaml) | 14 | WiFi/BLE/I2C/UART/Grove/GPIO |  | NZD 18.0 | Compact WiFi ESP32 |
| [METER TEROS 12 substrate VWC / EC / temperature probe](parts/meter-teros12.yaml) | 14 | SDI-12 |  | NZD 430.0 | SDI-12 dielectric probe |
| [PCF8563 real-time clock](parts/pcf8563-rtc.yaml) | 13 | I2C | 0x51 | NZD 6.0 | I2C real-time clock with battery backup |
| [TCA9548A 8-channel I2C multiplexer](parts/tca9548a-mux.yaml) | 9 | I2C | 0x70 | NZD 12.0 | 1-to-8 I2C switch |
| [M5Stack AirQ (SEN55 + SCD40 air quality node)](parts/m5stack-airq.yaml) | 8 | I2C/WiFi/BLE | 0x69 | NZD 145.0 | Integrated multi-sensor node |
| [Sensirion SEN55 PM / VOC / NOx / T / RH module](parts/sensirion-sen55.yaml) | 8 | I2C | 0x69 | NZD 125.0 | Particulate + VOC + NOx |
| [SSR-25DA solid state relay](parts/ssr-25da.yaml) | 8 | GPIO |  | NZD 18.0 | DC-controlled AC solid state relay |
| [Infiwin MT22 SDI-12 substrate probe](parts/infiwin-mt22.yaml) | 6 | SDI-12 |  | NZD 85.0 | SDI-12 dielectric probe (budget) |
| [M5Stack Dial (round display + rotary encoder + RFID)](parts/m5stack-dial.yaml) | 5 | I2C/SPI/WiFi/Grove/GPIO | 0x28 | NZD 110.0 | Round touch display node |
| [Sensirion SHT30 temperature & humidity sensor](parts/sensirion-sht30.yaml) | 5 | I2C | 0x44 | NZD 12.0 | Temperature / humidity |
| [HX711 24-bit load cell amplifier](parts/hx711-adc.yaml) | 4 | GPIO |  | NZD 6.0 | Load cell front end |
| [Load cell (50kg half-bridge or 200kg bar)](parts/load-cell-50kg.yaml) | 4 | Analog |  | NZD 15.0 | Strain gauge load cell |
| [M5Stack ENV III Unit (SHT30 + QMP6988)](parts/m5-env3.yaml) | 4 | I2C/Grove | 0x44 | NZD 18.0 | Temperature / humidity / pressure |
| [MLX90640 32x24 thermal camera array](parts/mlx90640-thermal.yaml) | 4 | I2C | 0x33 | NZD 120.0 | 32x24 far-infrared thermopile array |
| [Peristaltic dosing pump (12/24V, relay or PWM driven)](parts/peristaltic-pump-doser.yaml) | 4 | GPIO/PWM/UART |  | NZD 65.0 | Nutrient dosing pump |
| [Growlink TerraLink substrate probe](parts/growlink-terralink.yaml) | 3 | SDI-12 |  | $$$ | SDI-12 dielectric probe |
| [24VAC irrigation solenoid valve](parts/solenoid-valve-24vac.yaml) | 3 | Mains |  | NZD 42.0 | Zone valve |

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
| [MFRC522 / RC522 13.56 MHz RFID reader](parts/mfrc522-rfid.yaml) | **field-proven** | 19 | I2C/SPI | 0x28 | NZD 8.0 |
| [Seeed LeapMMW 24 GHz mmWave presence radar](parts/seeed-leapmmw-mmwave.yaml) | **avoid** |  | UART |  | NZD 40.0 |

#### Actuation & relays

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack 4-Relay Unit](parts/m5stack-4relay.yaml) | **field-proven** | 18 | I2C/Grove | 0x26 | NZD 38.0 |
| [SSR-25DA solid state relay](parts/ssr-25da.yaml) | **field-proven** | 8 | GPIO |  | NZD 18.0 |
| [KinCony F16 16-channel relay controller](parts/kincony-f16-relay.yaml) | experimental | 1 | Ethernet/RS485/Modbus/I2C | 0x24 | NZD 210.0 |

#### Air quality & CO2

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [Sensirion SCD41 true NDIR CO2 sensor](parts/sensirion-scd41.yaml) | **field-proven** | 29 | I2C/Grove | 0x62 | NZD 52.0 |
| [M5Stack AirQ (SEN55 + SCD40 air quality node)](parts/m5stack-airq.yaml) | **field-proven** | 8 | I2C/WiFi/BLE | 0x69 | NZD 145.0 |
| [Sensirion SEN55 PM / VOC / NOx / T / RH module](parts/sensirion-sen55.yaml) | **field-proven** | 8 | I2C | 0x69 | NZD 125.0 |
| [Sensirion SHT30 temperature & humidity sensor](parts/sensirion-sht30.yaml) | **field-proven** | 5 | I2C | 0x44 | NZD 12.0 |
| [M5Stack ENV III Unit (SHT30 + QMP6988)](parts/m5-env3.yaml) | **field-proven** | 4 | I2C/Grove | 0x44 | NZD 18.0 |
| [Bosch BME680 gas / T / RH / pressure sensor](parts/bosch-bme680.yaml) | works | 1 | I2C/SPI | 0x76 | NZD 28.0 |
| [Bosch BMP280 pressure & temperature sensor](parts/bosch-bmp280.yaml) | works | 1 | I2C/SPI | 0x76 | NZD 6.0 |
| [ComWinTop CWT-LEAF-TH-S-N leaf surface temperature & wetness sensor](parts/cwt-leaf-th.yaml) | works | 1 | RS485/Modbus |  | NZD 95.0 |
| [Sensirion SHT40 temperature & humidity sensor](parts/sensirion-sht40.yaml) | works | 1 | I2C | 0x44 | NZD 14.0 |
| [Bosch BME280 temperature / humidity / pressure sensor](parts/bosch-bme280.yaml) | works |  | I2C/SPI | 0x76 | NZD 9.0 |
| [Sensirion SCD30 NDIR CO2 sensor](parts/sensirion-scd30.yaml) | works |  | I2C | 0x61 | NZD 105.0 |
| [Sensirion SCD40 NDIR CO2 sensor](parts/sensirion-scd40.yaml) | works |  | I2C/Grove | 0x62 | NZD 40.0 |
| [ComWinTop CWT-SWS-C wind speed sensor](parts/cwt-sws-wind.yaml) | experimental |  | RS485/Modbus |  | $$ |
| [ZPHS01B all-in-one air quality module](parts/zphs01b-multigas.yaml) | **avoid** |  | UART |  | NZD 180.0 |

#### Bus infrastructure

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [PCF8563 real-time clock](parts/pcf8563-rtc.yaml) | **field-proven** | 13 | I2C | 0x51 | NZD 6.0 |
| [TCA9548A 8-channel I2C multiplexer](parts/tca9548a-mux.yaml) | **field-proven** | 9 | I2C | 0x70 | NZD 12.0 |
| [MAX485 / SP3485 RS485-to-TTL transceiver](parts/rs485-ttl-transceiver.yaml) | works | 2 | RS485/Modbus/UART |  | NZD 8.0 |

#### Controllers & boards

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack ATOM Lite (ESP32-PICO)](parts/m5stack-atom-lite.yaml) | **field-proven** | 14 | WiFi/BLE/I2C/UART/Grove/GPIO |  | NZD 18.0 |
| [M5Stack AtomS3 Lite (ESP32-S3)](parts/m5stack-atoms3-lite.yaml) | works | 25 | WiFi/BLE/I2C/UART/Grove/USB/GPIO |  | NZD 22.0 |
| [WT32-ETH01 (ESP32 + LAN8720 Ethernet)](parts/wt32-eth01.yaml) | works |  | Ethernet/UART/I2C/GPIO |  | NZD 20.0 |

#### Displays & HMI

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack Dial (round display + rotary encoder + RFID)](parts/m5stack-dial.yaml) | **field-proven** | 5 | I2C/SPI/WiFi/Grove/GPIO | 0x28 | NZD 110.0 |

#### Irrigation hardware

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [24VAC irrigation solenoid valve](parts/solenoid-valve-24vac.yaml) | **field-proven** | 3 | Mains |  | NZD 42.0 |

#### Light measurement

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [BH1750 ambient light sensor](parts/bh1750.yaml) | works | 2 | I2C | 0x23 | NZD 7.0 |
| [AS7341 11-channel spectral sensor](parts/as7341.yaml) | works |  | I2C | 0x39 | NZD 48.0 |
| [ComWinTop CWT-PS PAR / quantum sensor](parts/cwt-ps-par.yaml) | experimental |  | RS485/Modbus |  | $$ |

#### Networking & power

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [M5Stack PoESP32 / ESP32 Ethernet unit (IP101G PHY)](parts/m5stack-poesp32.yaml) | **field-proven** | 48 | Ethernet/PoE/Grove/I2C/UART |  | NZD 65.0 |
| [W5500 SPI Ethernet module](parts/w5500-eth-module.yaml) | works | 2 | SPI/Ethernet |  | NZD 12.0 |

#### Substrate sensing

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [METER TEROS 12 substrate VWC / EC / temperature probe](parts/meter-teros12.yaml) | **field-proven** | 14 | SDI-12 |  | NZD 430.0 |
| [Infiwin MT22 SDI-12 substrate probe](parts/infiwin-mt22.yaml) | **field-proven** | 6 | SDI-12 |  | NZD 85.0 |
| [Growlink TerraLink substrate probe](parts/growlink-terralink.yaml) | **field-proven** | 3 | SDI-12 |  | $$$ |
| [Chill Division SDI-12 substrate sensor](parts/chill-division-sdi12.yaml) | works |  | SDI-12/WiFi |  | $$ |
| [THC-S RS485 soil moisture / EC / temperature probe](parts/thc-s-rs485.yaml) | works |  | RS485/Modbus |  | NZD 45.0 |

#### Thermal & optical

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [MLX90640 32x24 thermal camera array](parts/mlx90640-thermal.yaml) | **field-proven** | 4 | I2C | 0x33 | NZD 120.0 |

#### Water & fertigation

| Part | Tier | Live | Bus | I²C | Price |
|---|---|---:|---|---|---|
| [HX711 24-bit load cell amplifier](parts/hx711-adc.yaml) | **field-proven** | 4 | GPIO |  | NZD 6.0 |
| [Load cell (50kg half-bridge or 200kg bar)](parts/load-cell-50kg.yaml) | **field-proven** | 4 | Analog |  | NZD 15.0 |
| [Peristaltic dosing pump (12/24V, relay or PWM driven)](parts/peristaltic-pump-doser.yaml) | **field-proven** | 4 | GPIO/PWM/UART |  | NZD 65.0 |
| [Ultrasonic distance sensor for tank level](parts/ultrasonic-tank-sensor.yaml) | works | 3 | GPIO/UART/I2C | 0x57 | NZD 25.0 |
| [Float switch (tank level interlock)](parts/float-switch.yaml) | works | 1 | GPIO |  | NZD 8.0 |
| [DS18B20 1-Wire temperature probe](parts/ds18b20.yaml) | works |  | 1-Wire |  | NZD 9.0 |
| [Atlas Scientific EZO-EC conductivity circuit + probe](parts/atlas-ezo-ec.yaml) | experimental | 1 | I2C/UART | 0x64 | NZD 245.0 |
| [Atlas Scientific EZO-RTD temperature circuit + PT-1000 probe](parts/atlas-ezo-rtd.yaml) | experimental | 1 | I2C/UART | 0x66 | NZD 140.0 |
| [Atlas Scientific EZO-pH circuit + probe](parts/atlas-ezo-ph.yaml) | experimental | 1 | I2C/UART | 0x63 | NZD 230.0 |
| [DFRobot Gravity analog ORP sensor](parts/dfrobot-gravity-orp.yaml) | experimental | 1 | Analog |  | NZD 80.0 |
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

## Licence

Catalogue data and documentation: [CC BY 4.0](LICENSE).
Scripts and site code: [MIT](LICENSE-CODE).
