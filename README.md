# RFGhost

**RFGhost** is a passive RF anomaly detector and spectral logger for Raspberry Pi Zero + CC1101. Designed for RF reconnaissance, IoT ghost hunting, and alternate reality infrastructure monitoring, it scans sub-GHz ISM bands (315/433/868/915 MHz), detects strange signals, and logs or reports them in stylized ARG-style formats.

## Features

- 📡 Passive RF scanning across multiple frequencies
- ⚠️ Entropy and anomaly detection for unknown or suspicious signals
- 🧾 JSONL/CSV logging of spectral data (RSSI, duration, entropy, freq)
- 🔔 Slack/Discord/webhook alerts on high-interest detections
- 🧙 ARG-style outputs with glitch fonts, corrupted sigils, and narrative hooks
- 🔌 Integration hooks for n8n or other automations

## Hardware Requirements

- Raspberry Pi Zero W
- CC1101 RF Transceiver (SPI)
- Optional OLED SPI display
- Optional GPS USB dongle (for timestamp/location)

## File Overview

| File             | Purpose                              |
|------------------|---------------------------------------|
| `main.py`        | Starts scanning loop and core logic   |
| `rf_interface.py`| SPI-based RF control via CC1101       |
| `anomaly_engine.py` | Detects unusual patterns or entropy |
| `logger.py`      | Logs to file                          |
| `alerts.py`      | Sends alerts to Slack/webhook         |
| `config.yaml`    | Configurable system settings          |

## Example Slack Alert

```
*RFGhost Alert:* `Ghost Echo`
> Freq: 433.92 MHz | Duration: 3.4s | Entropy: 92%
"The signal has returned. We have no record of it."
```

## License

MIT
