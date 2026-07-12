"""AM radio demodulator."""

import math
import logging
from typing import List

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


class AMDecoder:
    """AM envelope demodulator."""

    def __init__(self):
        pass

    def demodulate(self, samples: IQSample) -> List[float]:
        """Demodulate AM signal using envelope detection.

        Args:
            samples: IQSample containing AM signal

        Returns:
            List of demodulated audio samples
        """
        data = samples.data
        envelope = []

        for sample in data:
            # Envelope = magnitude of complex sample
            mag = abs(sample)
            envelope.append(mag)

        # Remove DC offset
        if envelope:
            dc = sum(envelope) / len(envelope)
            envelope = [e - dc for e in envelope]

        return envelope

    def demodulate_ssb(self, samples: IQSample, sideband: str = "usb") -> List[float]:
        """Demodulate SSB (Single Sideband) signal.

        Args:
            samples: IQSample containing SSB signal
            sideband: "usb" or "lsb"

        Returns:
            List of demodulated audio samples
        """
        data = samples.data
        audio = []

        for i in range(len(data)):
            # SSB demodulation via phase shifting
            sample = data[i]
            if sideband == "usb":
                audio.append(sample.real - sample.imag)
            else:
                audio.append(sample.real + sample.imag)

        return audio
