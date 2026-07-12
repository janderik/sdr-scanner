# sdr-scanner

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![SDR](https://img.shields.io/badge/SDR-RTL--SDR%20HackRF%20airspy-blue.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

**Software Defined Radio security testing toolkit for RF signal analysis and protocol decoding.**

`blr-scanner` provides tools for capturing, analyzing, and decoding radio frequency signals using Software Defined Radio (SDR) hardware. It supports RTL-SDR, HackRF, and Airspy devices for security research, protocol analysis, and signal intelligence.

---

## Architecture

```
sdr-scanner/
├── src/
│   ├── scanner/           # Core SDR scanning engine
│   │   ├── __init__.py
│   │   ├── engine.py      # Main SDR engine
│   │   ├── devices.py     # SDR device abstraction
│   │   ├── models.py      # Signal and frequency models
│   │   └── config.py      # Scanner configuration
│   ├── analyzers/         # Signal analyzers
│   │   ├── __init__.py
│   │   ├── spectrum.py    # Spectrum analyzer
│   │   ├── waterfall.py   # Waterfall display
│   │   ├── modulation.py  # Modulation detector
│   │   └── signal.py      # Signal strength analysis
│   └── decoders/          # Protocol decoders
│       ├── __init__.py
│       ├── fm.py          # FM radio decoder
│       ├── am.py          # AM radio decoder
│       ├── ais.py         # AIS (ship tracking) decoder
│       ├── adsb.py        # ADS-B (aircraft) decoder
│       └── pager.py       # Pager protocol decoder
├── cli.py
├── requirements.txt
├── setup.py
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── LICENSE
```

## Features

### Core SDR Engine
- **Multi-device support** - RTL-SDR, HackRF, Airspy, and compatible devices
- **Wide frequency range** - 1 MHz to 6 GHz depending on hardware
- **IQ capture** - Raw IQ sample recording and playback
- **Real-time processing** - Live signal analysis with FFT
- **Batch processing** - Analyze recorded IQ files

### Signal Analysis
- **Spectrum analysis** - Frequency domain visualization
- **Waterfall display** - Time-frequency spectrogram
- **Modulation detection** - Auto-detect AM, FM, SSB, digital modulations
- **Signal strength** - RSSI measurement and logging
- **Band scanning** - Automated frequency sweep

### Protocol Decoders
- **FM Broadcast** - WFM/NFM radio reception
- **AM Broadcast** - Medium wave and aviation AM
- **AIS** - Automatic Identification System (ship tracking)
- **ADS-B** - Automatic Dependent Surveillance-Broadcast (aircraft)
- **POCSAG/FLEX** - Pager protocol decoding

### Security Testing
- **Signal identification** - Unknown signal classification
- **Replay analysis** - Capture and analyze RF emissions
- **Key fob analysis** - Rolling code assessment
- **ISM band monitoring** - Industrial/Scientific/Medical band traffic

## Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev librtlsdr-dev libhackrf-dev libusb-1.0-0-dev cmake

# macOS
brew install librtlsdr hackrf cmake

# Windows - Install Zadig for USB drivers
# Download from https://zadig.akeo.ie/
```

### From Source

```bash
git clone https://github.com/janderik/sdr-scanner.git
cd sdr-scanner
pip install -e .
```

### Dependencies

```
pip install -r requirements.txt
```

## Usage

### Basic Spectrum Scanning

```bash
# Scan a frequency band
sdr-scanner scan --freq 433.92e6 --bandwidth 2e6

# Scan with specific device
sdr-scanner scan --freq 100e6 --device rtl --duration 30

# Wideband scan
sdr-scanner scan --freq-start 88e6 --freq-stop 108e6 --step 100e3
```

### Signal Recording

```bash
# Record IQ samples
sdr-scanner record --freq 433.92e6 --duration 60 --output capture.iq

# Record with specific sample rate
sdr-scanner record --freq 1090e6 --sample-rate 2.4e6 --output adsb.iq
```

### Protocol Decoding

```bash
# Decode FM radio
sdr-scanner decode fm --freq 101.1e6

# Decode AIS (ship tracking)
sdr-scanner decode ais --freq 161.975e6 --freq2 162.025e6

# Decode ADS-B (aircraft)
sdr-scanner decode adsb --freq 1090e6

# Decode pager signals
sdr-scanner decode pager --freq 152.0e6 --protocol pocsag
```

### Signal Analysis

```bash
# Analyze modulation type
sdr-scanner analyze --freq 433.92e6 --modulation

# Measure signal strength over time
sdr-scanner analyze --freq 433.92e6 --rssi --duration 300

# Find active signals in a band
sdr-scanner scan --freq-start 430e6 --freq-stop 440e6 --detect
```

### Python API

```python
from src.scanner.engine import SDREngine
from src.scanner.devices import RTLSDRDevice
from src.analyzers.spectrum import SpectrumAnalyzer
from src.decoders.adsb import ADSBDecoder

# Initialize device
device = RTLSDRDevice()
engine = SDREngine(device)

# Capture samples
samples = engine.capture(frequency=1090e6, sample_rate=2.4e6, duration=10)

# Analyze spectrum
spectrum = SpectrumAnalyzer()
freqs, power = spectrum.analyze(samples, sample_rate=2.4e6)

# Decode ADS-B
decoder = ADSBDecoder()
messages = decoder.decode(samples, sample_rate=2.4e6)
for msg in messages:
    print(f"Aircraft: {msg['icao']}, Altitude: {msg['altitude']}")
```

## SDR Security Testing Concepts

### What is SDR?

Software Defined Radio replaces traditional hardware-based radio components with software implementations. This allows flexible access to a wide range of frequencies and modulation schemes.

### Common SDR Hardware

| Device | Frequency Range | Bandwidth | Price |
|--------|----------------|-----------|-------|
| RTL-SDR | 24 MHz - 1.7 GHz | 2.4 MHz | $25 |
| HackRF One | 1 MHz - 6 GHz | 20 MHz | $300 |
| Airspy Mini | 24 MHz - 1.8 GHz | 6 MHz | $100 |
| USRP B200 | 70 MHz - 6 GHz | 56 MHz | $1,300 |

### RF Security Concerns

#### Key Fob Replay Attacks
Many vehicle key fobs and garage door openers use simple RF protocols:
- **Fixed codes** - Same code every press (trivially replayed)
- **Rolling codes** - Pre-shared key stream (vulnerable to jam-and-replay)
- **KeeLoq** - Widely used but has known vulnerabilities

#### ISM Band Abuse
The 433 MHz, 868 MHz, and 915 MHz ISM bands are commonly used by:
- IoT sensors and home automation
- Weather stations
- Tire pressure monitoring systems (TPMS)
- Wireless cameras

#### Aviation Security
- **ADS-B** - Broadcasts aircraft position, altitude, and identity in clear text
- **ACARS** - Aircraft Communications Addressing and Reporting System
- **VDL Mode 2** - VHF Data Link for ACARS messages

#### Maritime AIS
- **Class A** - Used by large vessels (mandatory)
- **Class B** - Used by smaller vessels
- AIS data includes vessel identity, position, course, and speed

### Signal Modulation Types

| Modulation | Use Case | Characteristics |
|-----------|----------|----------------|
| AM (Amplitude) | Aviation, MW radio | Simple, noise-prone |
| FM (Frequency) | Broadcast radio, voice | Noise-resistant |
| SSB (Single Sideband) | Amateur radio, maritime | Bandwidth efficient |
| FSK (Frequency Shift) | Digital data, pagers | Binary data encoding |
| PSK (Phase Shift) | Digital comms, WiFi | High data rate |
| OOK (On-Off Keying) | Key fobs, sensors | Very simple |

### Legal Considerations

> **Warning:** RF transmission laws vary by jurisdiction. In most countries:
> - **Receiving** RF signals is generally legal
> - **Transmitting** without a license is illegal on most frequencies
> - **ISM bands** (433/868/915 MHz) have limited unlicensed transmission rights
> - **Jamming** is illegal everywhere

Always comply with local telecommunications regulations.

### Defensive Measures

1. **Encrypt RF communications** - Never transmit sensitive data in clear text
2. **Use frequency hopping** - Spread spectrum reduces interception risk
3. **Implement authentication** - Prevent unauthorized command execution
4. **Monitor RF environment** - Detect unauthorized transmissions
5. **Shield sensitive equipment** - Use Faraday cages for critical systems

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.
