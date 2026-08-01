# Security

## No credentials in this repository

Every configuration example here is **distilled from** a real production system,
never copied verbatim. Real ESPHome device configs contain live secrets, and the
source material behind this catalogue is no exception.

Anything lifted from a working config must have the following replaced with
`!secret` references or obvious placeholders **before** it enters the repo:

- API encryption keys (44-character base64)
- OTA passwords (32-character hex)
- WiFi SSIDs and passwords, and AP fallback passwords
- Static IP addresses, gateways and MAC addresses
- RFID / NFC card UIDs and the names they map to
- RTSP camera URLs containing credentials
- Zigbee network keys
- MQTT broker credentials and API tokens

## Automated enforcement

`scripts/validate.py` scans every part file for these patterns and **fails the
build** on a match. It runs on every push and pull request via
`.github/workflows/validate.yml`.

The scanner is a safety net, not a substitute for reading what you paste. It has
false positives by design — it would rather flag a harmless-looking string than
miss a real key. If it flags something genuinely safe, make the value obviously
a placeholder (`YOUR_...`, `CHANGE_ME`, `!secret ...`) rather than tuning the
scanner around it.

## Using these examples safely

The examples use `!secret` placeholders throughout. To use one:

1. Copy the snippet into your own ESPHome config.
2. Create or update your own `secrets.yaml` with **your** values.
3. Never commit your `secrets.yaml` — the shipped `.gitignore` already excludes
   `secrets.yaml`, `*.secret.yaml` and `.env`.

Generate your own keys rather than reusing any string you find in an example:

```bash
# API encryption key
openssl rand -base64 32

# OTA password
openssl rand -hex 16
```

## A note on RFID

Several examples involve MIFARE Classic RFID readers. Treat card UIDs as
**identifiers, not secrets** — MIFARE Classic UIDs are trivially cloned with
commodity hardware.

Two consequences:

- Do not paste real card UIDs into a public repo. They map to real people and
  real doors, and publishing them is a physical-security problem, not a data one.
- Do not treat an RFID fob as a security boundary. It is a convenience
  credential. Back it with a real lock, cameras, and an audit log.

Store the UID→person mapping in Home Assistant rather than hard-coding it in
device YAML. Revoking a lost fob then means editing one place, not reflashing a
door node — and it keeps access credentials out of your config repo entirely.

## Reporting a problem

If you find committed credentials in this repository — in history as well as at
HEAD — please open an issue **without quoting the secret** and it will be
scrubbed and the credential rotated.
