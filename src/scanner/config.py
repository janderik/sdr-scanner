"""Scanner configuration."""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScannerConfig:
    """Configuration for SDR scanning."""
    device_type: str = "rtlsdr"
    device_index: int = 0
    frequency: float = 100e6
    sample_rate: float = 2.048e6
    gain: float = 40.0
    bandwidth: float = 200e3
    duration: int = 10
    output_file: Optional[str] = None
    output_format: str = "console"
    fft_size: int = 1024
    averaging: int = 10
    db_offset: float = 0.0

    @classmethod
    def from_file(cls, path: str) -> "ScannerConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


DEFAULT_BANDS = {
    "fm": {"freq": 100e6, "bandwidth": 200e3},
    "ais": {"freq": 161.975e6, "bandwidth": 25e3},
    "adsb": {"freq": 1090e6, "bandwidth": 2e6},
    "433": {"freq": 433.92e6, "bandwidth": 200e3},
}
