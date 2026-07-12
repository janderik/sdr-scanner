"""Spectrum analyzer for frequency domain analysis."""

import math
import logging
from typing import Tuple, List, Optional

from ..scanner.models import IQSample, SignalInfo

logger = logging.getLogger(__name__)


class SpectrumAnalyzer:
    """Frequency domain spectrum analyzer."""

    def __init__(self, fft_size: int = 1024):
        self.fft_size = fft_size

    def analyze(self, samples: IQSample) -> Tuple[List[float], List[float]]:
        """Compute power spectrum from IQ samples.

        Args:
            samples: IQSample containing IQ data

        Returns:
            Tuple of (frequencies, power_db) arrays
        """
        data = samples.data
        sample_rate = samples.sample_rate

        # Compute FFT
        fft_result = self._fft(data[:self.fft_size])

        # Compute power in dB
        n = len(fft_result)
        power = []
        for val in fft_result:
            p = abs(val) ** 2 / (n ** 2)
            if p > 0:
                power.append(10 * math.log10(p * 1000))
            else:
                power.append(-100.0)

        # Compute frequency axis
        freq_step = sample_rate / n
        center = samples.frequency
        frequencies = [center + (i - n // 2) * freq_step for i in range(n)]

        # Shift to center DC
        power = self._fftshift(power)
        frequencies = self._fftshift(frequencies)

        return frequencies, power

    def detect_peaks(self, frequencies: List[float], power: List[float],
                     threshold: float = -60.0, min_distance: int = 5) -> List[SignalInfo]:
        """Detect peaks in the spectrum.

        Args:
            frequencies: Frequency array
            power: Power array in dB
            threshold: Minimum power threshold in dBm
            min_distance: Minimum distance between peaks (in bins)

        Returns:
            List of detected signals
        """
        signals = []
        peaks = []
        n = len(power)

        # Simple peak detection
        for i in range(1, n - 1):
            if (power[i] > power[i-1] and power[i] > power[i+1] and
                power[i] > threshold):
                peaks.append((i, power[i]))

        # Filter by minimum distance
        filtered_peaks = []
        for idx, power_val in peaks:
            too_close = False
            for f_idx, _ in filtered_peaks:
                if abs(idx - f_idx) < min_distance:
                    too_close = True
                    break
            if not too_close:
                filtered_peaks.append((idx, power_val))

        # Create SignalInfo objects
        for idx, power_val in filtered_peaks:
            signals.append(SignalInfo(
                frequency=frequencies[idx],
                bandwidth=0,  # Would need more analysis
                power_dbm=power_val,
            ))

        return signals

    def get_band_power(self, frequencies: List[float], power: List[float],
                       freq_start: float, freq_stop: float) -> float:
        """Compute total power in a frequency band."""
        total_power = 0
        count = 0
        for f, p in zip(frequencies, power):
            if freq_start <= f <= freq_stop:
                total_power += 10 ** (p / 10)
                count += 1
        if count > 0:
            avg = total_power / count
            return 10 * math.log10(avg) if avg > 0 else -100.0
        return -100.0

    def _fft(self, data: list) -> list:
        """Compute FFT using Cooley-Tukey algorithm."""
        n = len(data)
        if n <= 1:
            return data

        if n & (n - 1) != 0:
            # Pad to next power of 2
            next_pow2 = 1
            while next_pow2 < n:
                next_pow2 <<= 1
            data = data + [complex(0, 0)] * (next_pow2 - n)
            n = next_pow2

        if n <= 1:
            return data

        even = self._fft(data[0::2])
        odd = self._fft(data[1::2])

        result = [complex(0, 0)] * n
        for k in range(n // 2):
            twiddle = complex(
                math.cos(-2 * math.pi * k / n),
                math.sin(-2 * math.pi * k / n)
            )
            t = twiddle * odd[k]
            result[k] = even[k] + t
            result[k + n // 2] = even[k] - t

        return result

    def _fftshift(self, data: list) -> list:
        """Shift FFT output to center DC component."""
        n = len(data)
        mid = n // 2
        return data[mid:] + data[:mid]
