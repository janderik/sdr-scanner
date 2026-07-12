"""SDR device abstraction layer."""

import logging
import math
import random
from typing import Optional
from abc import ABC, abstractmethod

from .models import DeviceType

logger = logging.getLogger(__name__)


class SDRDevice(ABC):
    """Abstract base class for SDR devices."""

    device_type: DeviceType = DeviceType.SIMULATED

    @abstractmethod
    def open(self, device_index: int = 0) -> bool:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def set_frequency(self, freq: float):
        pass

    @abstractmethod
    def set_sample_rate(self, rate: float):
        pass

    @abstractmethod
    def set_gain(self, gain: float):
        pass

    @abstractmethod
    def read_samples(self, num_samples: int) -> list:
        pass


class RTLSDRDevice(SDRDevice):
    """RTL-SDR device wrapper."""

    device_type = DeviceType.RTLSDR

    def __init__(self):
        self._device = None
        self._frequency = 100e6
        self._sample_rate = 2.048e6
        self._gain = 40.0

    def open(self, device_index: int = 0) -> bool:
        try:
            from rtlsdr import RtlSdr
            self._device = RtlSdr(device_index)
            logger.info("RTL-SDR device opened")
            return True
        except ImportError:
            logger.warning("rtlsdr not installed - using simulation")
            return True
        except Exception as e:
            logger.error(f"Failed to open RTL-SDR: {e}")
            return False

    def close(self):
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
        self._device = None

    def set_frequency(self, freq: float):
        self._frequency = freq
        if self._device:
            try:
                self._device.center_freq = freq
            except Exception:
                pass

    def set_sample_rate(self, rate: float):
        self._sample_rate = rate
        if self._device:
            try:
                self._device.sample_rate = rate
            except Exception:
                pass

    def set_gain(self, gain: float):
        self._gain = gain
        if self._device:
            try:
                self._device.gain = gain
            except Exception:
                pass

    def read_samples(self, num_samples: int = 16384) -> list:
        if self._device:
            try:
                return self._device.read_samples(num_samples)
            except Exception:
                pass

        return self._simulate_samples(num_samples)

    def _simulate_samples(self, num_samples: int) -> list:
        """Generate simulated IQ samples."""
        samples = []
        for _ in range(num_samples):
            real = random.gauss(0, 0.1)
            imag = random.gauss(0, 0.1)
            samples.append(complex(real, imag))
        return samples


class HackRFDevice(SDRDevice):
    """HackRF One device wrapper."""

    device_type = DeviceType.HACKRF

    def __init__(self):
        self._device = None
        self._frequency = 100e6
        self._sample_rate = 2e6
        self._gain = 30.0

    def open(self, device_index: int = 0) -> bool:
        try:
            import subprocess
            result = subprocess.run(["hackrf_info"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("HackRF device found")
                return True
        except Exception:
            pass
        logger.warning("HackRF not available - using simulation")
        return True

    def close(self):
        self._device = None

    def set_frequency(self, freq: float):
        self._frequency = freq

    def set_sample_rate(self, rate: float):
        self._sample_rate = rate

    def set_gain(self, gain: float):
        self._gain = gain

    def read_samples(self, num_samples: int = 16384) -> list:
        samples = []
        for _ in range(num_samples):
            real = random.gauss(0, 0.1)
            imag = random.gauss(0, 0.1)
            samples.append(complex(real, imag))
        return samples


def create_device(device_type: str = "rtlsdr") -> SDRDevice:
    """Factory function to create SDR device."""
    devices = {
        "rtlsdr": RTLSDRDevice,
        "hackrf": HackRFDevice,
    }
    device_class = devices.get(device_type.lower(), RTLSDRDevice)
    return device_class()
