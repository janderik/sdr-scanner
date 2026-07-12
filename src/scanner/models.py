"""Data models for SDR signal analysis."""

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class ModulationType(Enum):
    """Signal modulation types."""
    AM = "am"
    FM = "fm"
    USB = "usb"
    LSB = "lsb"
    SSB = "ssb"
    FSK = "fsk"
    PSK = "psk"
    OOK = "ook"
    QAM = "qam"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """SDR device types."""
    RTLSDR = "rtlsdr"
    HACKRF = "hackrf"
    AIRSPY = "airspy"
    USRP = "usrp"
    SIMULATED = "simulated"


@dataclass
class FrequencyBand:
    """Represents a frequency band."""
    name: str
    start_freq: float  # Hz
    stop_freq: float   # Hz
    description: str = ""

    @property
    def center_freq(self) -> float:
        return (self.start_freq + self.stop_freq) / 2

    @property
    def bandwidth(self) -> float:
        return self.stop_freq - self.start_freq


@dataclass
class SignalInfo:
    """Information about a detected signal."""
    frequency: float
    bandwidth: float
    power_dbm: float
    modulation: ModulationType = ModulationType.UNKNOWN
    snr_db: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class IQSample:
    """IQ sample data container."""
    data: list  # Complex IQ samples
    sample_rate: float
    frequency: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    gain: float = 0.0

    @property
    def duration(self) -> float:
        return len(self.data) / self.sample_rate

    def to_numpy(self):
        """Convert to numpy array if available."""
        try:
            import numpy as np
            return np.array(self.data, dtype=np.complex64)
        except ImportError:
            return self.data


# Predefined frequency bands
COMMON_BANDS = {
    "FM_BROADCAST": FrequencyBand("FM Broadcast", 88e6, 108e6, "FM radio broadcasting"),
    "AM_BROADCAST": FrequencyBand("AM Broadcast", 535e6, 1705e6, "AM/MW radio broadcasting"),
    "ISM_433": FrequencyBand("ISM 433 MHz", 433.05e6, 434.79e6, "ISM band - Europe"),
    "ISM_868": FrequencyBand("ISM 868 MHz", 868e6, 870e6, "ISM band - Europe"),
    "ISM_915": FrequencyBand("ISM 915 MHz", 902e6, 928e6, "ISM band - Americas"),
    "AIS_1": FrequencyBand("AIS 1", 161.975e6, 161.975e6, "Maritime AIS channel 1"),
    "AIS_2": FrequencyBand("AIS 2", 162.025e6, 162.025e6, "Maritime AIS channel 2"),
    "ADS_B": FrequencyBand("ADS-B", 1090e6, 1090e6, "Aircraft ADS-B transponder"),
    "AVIATION_AM": FrequencyBand("Aviation AM", 118e6, 137e6, "Airband VHF"),
    "HAM_2M": FrequencyBand("2m Ham", 144e6, 148e6, "Amateur radio 2m band"),
    "HAM_70CM": FrequencyBand("70cm Ham", 420e6, 450e6, "Amateur radio 70cm band"),
}
