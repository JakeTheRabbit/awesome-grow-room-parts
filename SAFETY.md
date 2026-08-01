# The safety pattern

> Every output in this catalogue that can move water, gas or heat carries the same
> three-part pattern. It exists because each part of it was added after something
> went wrong. In the source configs these lines are tagged with a `# SAFETY:`
> comment and a date — 12 production device files carry them.

A grow room controller is not a smart-home gadget. A light that stays on wastes
power. **A valve that stays open floods a room, drowns a crop, and can take out
the electrics underneath it.** The whole point of this page is that the failure
modes are not exotic — they are a power cut, a network blip, and a wedged
controller. All three are routine, and all three are survivable if you write the
config defensively.

---

## 1. `restore_mode: ALWAYS_OFF` — never resume a feed after a power cut

ESPHome's default is to restore the previous switch state on boot. For a lamp
that is friendly. For an irrigation valve it means:

> power cut at 14:00 mid-feed → power returns at 14:40 → **the valve reopens by
> itself**, unattended, with nobody watching, and stays open.

```yaml
switch:
  - platform: gpio
    pin: GPIO26
    id: zone_valve
    restore_mode: ALWAYS_OFF   # SAFETY: a power cut must never resume a feed
```

Apply it to **every** valve, pump, CO₂ solenoid and heater. The correct state
after an unexpected reboot is always *off*, and the controller should be told to
turn things on again deliberately, from a known-good state.

---

## 2. Auto-shutoff delay — a dead-man timer on every output

`restore_mode` handles reboots. It does nothing if the controller stays up but
stops making sense — a wedged automation, a lost HA connection mid-feed, an
`on_turn_on` that never gets its matching `off`.

The fix is to make "on" *self-limiting*: the device itself turns the output off
after a bounded time, with no help from the network.

```yaml
switch:
  - platform: m5stack4relay
    relay4:                      # NOTE: relay4 is PHYSICAL relay 1 on this module
      id: relay_1
      name: "Zone 1 valve"
      restore_mode: ALWAYS_OFF
      on_turn_on:                # SAFETY: dead-man timer
        - delay: 1200s           # 20 min — just above the longest real feed
        - switch.turn_off: relay_1
```

**Size it deliberately.** The live room 1 config shows this being tuned rather than
guessed: it started at 5 minutes, and was raised to 20 minutes when a legitimate
20-minute feed kept getting cut off. Too short and it fights normal operation
until someone disables it — which is worse than not having it. Too long and it
stops being a safety net.

> Rule of thumb: longest legitimate run, plus ~25%. Never "an hour, to be safe".

---

## 3. Network killguard — de-energise on **sustained** loss, not on a blip

This is the part people get wrong, and getting it wrong is worse than omitting it.

The obvious implementation is to kill outputs on `on_disconnect`. Do that and the
first flaky switch port will interrupt every feed you run. From the live config:

> `SAFETY: 2026-03-02 killed all relays INSTANTLY on any network drop.`
> `2026-06-12: replaced instant kill with a 90s grace timer.`
> Ethernet was observed flapping every few minutes; the instant kill was cutting
> real feeds short.

The correct shape is a **restartable grace timer**. A short flap is absorbed; a
sustained loss still fails safe.

```yaml
ethernet:
  type: IP101
  # ... pins ...
  on_connect:
    - script.stop: disconnect_killguard      # link came back — stand down
  on_disconnect:
    - script.execute: disconnect_killguard   # start (or restart) the countdown

script:
  - id: disconnect_killguard
    mode: restart          # each disconnect restarts the 90s window
    then:
      - delay: 90s
      - logger.log: "Sustained network loss >90s - flood safety: all valves off"
      - switch.turn_off: relay_1
      - switch.turn_off: relay_2
      - switch.turn_off: relay_3
      - switch.turn_off: relay_4
```

`mode: restart` is load-bearing. Without it, overlapping disconnect events stack
up and you get several pending shutdowns racing each other.

### The matching API timeout

`api.reboot_timeout` is the same idea one layer up: if the device cannot reach
Home Assistant for that long, it reboots (and `restore_mode: ALWAYS_OFF` then
guarantees everything comes back off). It has to be **longer than your longest
feed**, or it will reboot mid-irrigation:

```yaml
api:
  encryption:
    key: !secret api_encryption_key
  # SAFETY: was 5min; raised to 15min so a 20-min feed survives a brief HA blip.
  reboot_timeout: 15min
```

---

## Putting it together

The three layers cover three different failures, which is why you want all of
them:

| Failure | Caught by |
|---|---|
| Power cut, then power returns | `restore_mode: ALWAYS_OFF` |
| Controller alive but wedged; no `off` ever sent | `on_turn_on` auto-shutoff delay |
| Network or HA unreachable for a sustained period | killguard script + `reboot_timeout` |
| Brief network flap during a legitimate feed | killguard **grace timer** (absorbs it) |

## What this pattern does *not* cover

Be honest about the limits — software cannot fix these:

- **A relay welded closed.** SSRs and mechanical relays fail *on* more often than
  off. `switch.turn_off` will happily report success while the contact stays
  made. Put a mechanical contactor downstream of anything important.
- **A valve stuck open mechanically.** Grit in a solenoid does not care what the
  controller thinks.
- **The controller losing power while the valve is powered.** If your valve is
  energised-to-open, a dead controller closes it — good. If it is
  energised-to-close, you have built a flood machine; change the valve.

So: put a **physical** backstop under the software one. A float switch in a tray,
a drain to somewhere harmless, an RCD, and a water alarm that shouts at a phone.
The config patterns above are the cheap layer, not the only layer.

---

## Checklist before you energise anything

- [ ] Every water/gas/heat output has `restore_mode: ALWAYS_OFF`
- [ ] Every one has an `on_turn_on` auto-shutoff sized to the longest real run + 25%
- [ ] A killguard script exists, uses `mode: restart`, and has a grace delay (not instant)
- [ ] `on_connect` cancels the killguard
- [ ] `api.reboot_timeout` is longer than the longest legitimate feed
- [ ] Tested: pull the network cable mid-feed, confirm the feed survives 30 s and dies by 90 s
- [ ] Tested: power-cycle mid-feed, confirm nothing reopens on boot
- [ ] There is a physical backstop — drain, float switch, contactor, or alarm
