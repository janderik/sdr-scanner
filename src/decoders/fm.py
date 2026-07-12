"""FM radio demodulator."""

import math
import logging
from typing import List

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


class FMDecoder:
    """FM/PM demodulator for radio signals."""

    def __init__(self, deviation: float = 75000):
        """Initialize FM decoder.

        Args:
            deviation: Maximum frequency deviation in Hz (75kHz for broadcast FM)
        """
        self.deviation = deviation

    def demodulate(self, samples: IQSample) -> List[float]:
        """Demodulate FM signal.

        Args:
            samples: IQSample containing FM signal

        Returns:
            List of demodulated audio samples
        """
        data = samples.data
        if len(data) < 2:
            return []

        audio = []
        for i in range(1, len(data)):
            if abs(data[i-1]) > 0.0001:
                # Instantaneous frequency via conjugate multiplication
                product = data[i] * data[i-1].conjugate()
                phase = product.phase
                audio.append(phase * samples.sample_rate / (2 * math.pi * self.deviation))
            else:
                audio.append(0.0)

        return audio

    def demodulate_broadcast(self, samples: IQSample) -> dict:
        """Demodulate broadcast FM with stereo support.

        Returns:
            Dictionary with left and right audio channels
        """
        mono = self.demodulate(samples)

        # Simple stereo decode (L+R is mono, L-R would need subcarrier)
        return {
            "left": mono,
            "right": mono,
            "stereo": False,
            "sample_rate": samples.sample_rate,
        }

    def compute_signal_quality(self, audio: List[float]) -> dict:
        """Compute audio quality metrics."""
        if not audio:
            return {"rms": 0, "peak": 0, "dynamic_range": 0}

        rms = math.sqrt(sum(s ** 2 for s in audio) / len(audio))
        peak = max(abs(s) for s in audio)
        sorted_amps = sorted([abs(s) for s in audio])
        noise_floor = sum(sorted_amps[:len(sorted_amps)//10]) / max(len(sorted_amps)//10, 1)

        return {
            "rms": rms,
            "peak": peak,
            "noise_floor": noise_floor,
            "dynamic_range": 20 * math.log10(peak / max(noise_floor, 0.0001)),
        }
