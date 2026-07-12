"""Pager protocol decoder (POCSAG/FLEX)."""

import logging
from typing import List
from dataclasses import dataclass

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


@dataclass
class PagerMessage:
    """Decoded pager message."""
    address: int = 0
    message: str = ""
    protocol: str = ""
    baud_rate: int = 0
    timestamp: float = 0.0
    raw: str = ""


class POCSAGDecoder:
    """POCSAG pager protocol decoder."""

    BAUD_RATES = [512, 1200, 2400]

    def __init__(self, baud_rate: int = 1200):
        self.baud_rate = baud_rate

    def decode(self, samples: IQSample) -> List[PagerMessage]:
        """Decode POCSAG messages from IQ samples."""
        messages = []
        logger.debug(f"POCSAG decoder: {len(samples.data)} samples at {self.baud_rate} baud")
        return messages

    def decode_batch(self, data: List[int]) -> PagerMessage:
        """Decode a POCSAG batch."""
        msg = PagerMessage(protocol="POCSAG", baud_rate=self.baud_rate)
        return msg


class FLEXDecoder:
    """FLEX pager protocol decoder."""

    def __init__(self):
        pass

    def decode(self, samples: IQSample) -> List[PagerMessage]:
        """Decode FLEX messages from IQ samples."""
        messages = []
        logger.debug(f"FLEX decoder: {len(samples.data)} samples")
        return messages


class PagerDecoder:
    """Combined pager decoder supporting multiple protocols."""

    def __init__(self):
        self.pocsag = POCSAGDecoder()
        self.flex = FLEXDecoder()

    def decode_all(self, samples: IQSample) -> List[PagerMessage]:
        """Attempt to decode pager messages with all protocols."""
        messages = []
        messages.extend(self.pocsag.decode(samples))
        messages.extend(self.flex.decode(samples))
        return messages
