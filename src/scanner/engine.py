"""Main SDR scanning engine."""

import logging
import time
import math
from typing import List, Optional

from .devices import SDRDevice, create_device
from .models import IQSample, SignalInfo, ModulationType
from .config import ScannerConfig

logger = logging.getLogger(__name__)


class SDREngine:
    """Core SDR scanning engine."""

    def __init__(self, device: Optional[SDRDevice] = None, config: Optional[ScannerConfig] = None):
        self.config = config or ScannerConfig()
        self.device = device or create_device(self.config.device_type)
        self._is_running = False

    def start(self) -> bool:
        """Open and configure the SDR device."""
        success = self.device.open(self.config.device_index)
        if success:
            self.device.set_frequency(self.config.frequency)
            self.device.set_sample_rate(self.config.sample_rate)
            self.device.set_gain(self.config.gain)
        return success

    def stop(self):
        """Stop the SDR device."""
        self._is_running = False
        self.device.close()

    def capture(self, frequency: float = None, sample_rate: float = None,
                duration: float = 1.0, gain: float = None) -> IQSample:
        """Capture IQ samples.

        Args:
            frequency: Center frequency in Hz
            sample_rate: Sample rate in Hz
            duration: Capture duration in seconds
            gain: Gain in dB

        Returns:
            IQSample containing captured data
        """
        freq = frequency or self.config.frequency
        rate = sample_rate or self.config.sample_rate
        g = gain or self.config.gain

        self.device.set_frequency(freq)
        self.device.set_sample_rate(rate)
        self.device.set_gain(g)

        num_samples = int(rate * duration)
        samples = self.device.read_samples(num_samples)

        return IQSample(
            data=samples,
            sample_rate=rate,
            frequency=freq,
            gain=g,
        )

    def scan_band(self, start_freq: float, stop_freq: float,
                  step: float = None, dwell_time: float = 0.1) -> List[SignalInfo]:
        """Scan a frequency band and detect signals.

        Args:
            start_freq: Start frequency in Hz
            stop_freq: Stop frequency in Hz
            step: Frequency step size in Hz (default: sample_rate)
            dwell_time: Time to spend at each frequency in seconds

        Returns:
            List of detected signals
        """
        step = step or self.config.sample_rate
        signals = []
        freq = start_freq

        logger.info(f"Scanning {start_freq/1e6:.3f} - {stop_freq/1e6:.3f} MHz")

        while freq <= stop_freq:
            self.device.set_frequency(freq)
            num_samples = int(self.config.sample_rate * dwell_time)
            samples = self.device.read_samples(num_samples)

            # Simple signal detection via power threshold
            power = self._compute_power(samples)
            if power > -80:  # Signal detected above -80 dBm
                signal = SignalInfo(
                    frequency=freq,
                    bandwidth=self.config.bandwidth,
                    power_dbm=power,
                    modulation=self._detect_modulation(samples),
                )
                signals.append(signal)
                logger.info(f"Signal at {freq/1e6:.3f} MHz: {power:.1f} dBm")

            freq += step

        return signals

    def record(self, output_path: str, frequency: float = None,
               duration: float = 60.0) -> str:
        """Record IQ samples to a file.

        Args:
            output_path: Path to save IQ data
            frequency: Center frequency in Hz
            duration: Recording duration in seconds

        Returns:
            Path to the recorded file
        """
        freq = frequency or self.config.frequency
        sample = self.capture(frequency=freq, duration=duration)

        # Save as raw IQ (complex float32)
        import struct
        with open(output_path, "wb") as f:
            # Write header
            f.write(b"IQSCANNER")
            f.write(struct.pack("<f", sample.sample_rate))
            f.write(struct.pack("<f", sample.frequency))
            f.write(struct.pack("<f", sample.gain))
            f.write(struct.pack("<I", len(sample.data)))
            # Write samples
            for s in sample.data:
                f.write(struct.pack("<ff", s.real, s.imag))

        logger.info(f"Recorded {duration}s to {output_path}")
        return output_path

    def _compute_power(self, samples: list) -> float:
        """Compute average power of samples in dBm."""
        if not samples:
            return -100.0
        power_linear = sum(abs(s) ** 2 for s in samples) / len(samples)
        if power_linear > 0:
            power_dbm = 10 * math.log10(power_linear * 1000)
        else:
            power_dbm = -100.0
        return power_dbm

    def _detect_modulation(self, samples: list) -> ModulationType:
        """Simple modulation detection based on signal characteristics."""
        if not samples:
            return ModulationType.UNKNOWN

        # Compute instantaneous frequency
        freqs = []
        for i in range(1, len(samples)):
            if abs(samples[i-1]) > 0.001:
                phase_diff = (samples[i] * samples[i-1].conjugate()).phase
                freqs.append(phase_diff)

        if not freqs:
            return ModulationType.UNKNOWN

        freq_variance = sum((f - sum(freqs)/len(freqs))**2 for f in freqs) / len(freqs)
        amp_variance = sum((abs(s) - sum(abs(s2) for s2 in samples)/len(samples))**2
                          for s in samples) / len(samples)

        if amp_variance > freq_variance * 2:
            return ModulationType.AM
        elif freq_variance > amp_variance * 2:
            return ModulationType.FM
        else:
            return ModulationType.UNKNOWN
