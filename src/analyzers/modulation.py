"""Modulation type detection and analysis."""

import math
import logging
from typing import Tuple

from ..scanner.models import IQSample, ModulationType

logger = logging.getLogger(__name__)


class ModulationDetector:
    """Detects and classifies signal modulation types."""

    def detect(self, samples: IQSample) -> ModulationType:
        """Detect modulation type of a signal.

        Args:
            samples: IQSample containing the signal

        Returns:
            Detected ModulationType
        """
        data = samples.data
        if len(data) < 100:
            return ModulationType.UNKNOWN

        # Compute signal statistics
        am_var = self._amplitude_variance(data)
        pm_var = self._phase_variance(data)

        # Decision logic
        am_threshold = 0.1
        pm_threshold = 0.05

        if am_var > am_threshold and pm_var < pm_threshold:
            return ModulationType.AM
        elif pm_var > pm_threshold and am_var < am_threshold * 0.5:
            return ModulationType.FM
        elif pm_var > pm_threshold and am_var > am_threshold:
            return ModulationType.QAM
        elif self._is_binary(data):
            return ModulationType.FSK
        else:
            return ModulationType.UNKNOWN

    def analyze_signal_quality(self, samples: IQSample) -> dict:
        """Analyze signal quality metrics."""
        data = samples.data
        return {
            "snr_db": self._estimate_snr(data),
            "frequency_offset": self._estimate_freq_offset(data, samples.sample_rate),
            "amplitude_variance": self._amplitude_variance(data),
            "phase_variance": self._phase_variance(data),
        }

    def _amplitude_variance(self, data: list) -> float:
        """Compute normalized amplitude variance."""
        amps = [abs(s) for s in data]
        mean_amp = sum(amps) / len(amps)
        if mean_amp == 0:
            return 0
        variance = sum((a - mean_amp) ** 2 for a in amps) / len(amps)
        return variance / (mean_amp ** 2)

    def _phase_variance(self, data: list) -> float:
        """Compute phase variance."""
        phases = []
        for i in range(1, len(data)):
            if abs(data[i-1]) > 0.001:
                phases.append(data[i].phase - data[i-1].phase)

        if not phases:
            return 0

        mean_phase = sum(phases) / len(phases)
        return sum((p - mean_phase) ** 2 for p in phases) / len(phases)

    def _is_binary(self, data: list) -> bool:
        """Check if signal appears to be binary FSK."""
        freqs = []
        for i in range(1, len(data)):
            if abs(data[i-1]) > 0.001:
                freqs.append((data[i] * data[i-1].conjugate()).phase)

        if not freqs:
            return False

        # Check for two distinct frequency clusters
        mean = sum(freqs) / len(freqs)
        high = sum(1 for f in freqs if f > mean)
        low = sum(1 for f in freqs if f <= mean)

        return min(high, low) / len(freqs) > 0.3

    def _estimate_snr(self, data: list) -> float:
        """Estimate signal-to-noise ratio."""
        signal_power = sum(abs(s) ** 2 for s in data) / len(data)
        # Rough noise estimate from weakest 10%
        sorted_amps = sorted([abs(s) for s in data])
        noise_idx = len(sorted_amps) // 10
        noise_power = sum(a ** 2 for a in sorted_amps[:max(noise_idx, 1)]) / max(noise_idx, 1)

        if noise_power > 0:
            return 10 * math.log10(signal_power / noise_power)
        return 0.0

    def _estimate_freq_offset(self, data: list, sample_rate: float) -> float:
        """Estimate frequency offset from center."""
        if len(data) < 10:
            return 0.0

        total_phase = 0
        count = 0
        for i in range(1, min(len(data), 100)):
            if abs(data[i-1]) > 0.001:
                total_phase += (data[i] * data[i-1].conjugate()).phase
                count += 1

        if count > 0:
            avg_phase = total_phase / count
            return avg_phase * sample_rate / (2 * math.pi)
        return 0.0
