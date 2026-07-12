"""Signal strength analysis and monitoring."""

import math
import time
import logging
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


@dataclass
class SignalStrengthRecord:
    """A recorded signal strength measurement."""
    frequency: float
    power_dbm: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0


class SignalStrengthAnalyzer:
    """Analyzes signal strength over time."""

    def __init__(self):
        self._history: List[SignalStrengthRecord] = []

    def measure(self, samples: IQSample) -> float:
        """Measure average signal power in dBm.

        Args:
            samples: IQSample containing signal data

        Returns:
            Average power in dBm
        """
        power_linear = sum(abs(s) ** 2 for s in samples.data) / len(samples.data)
        if power_linear > 0:
            power_dbm = 10 * math.log10(power_linear * 1000)
        else:
            power_dbm = -100.0

        record = SignalStrengthRecord(
            frequency=samples.frequency,
            power_dbm=power_dbm,
            duration_ms=samples.duration * 1000,
        )
        self._history.append(record)

        return power_dbm

    def get_statistics(self) -> dict:
        """Get signal strength statistics."""
        if not self._history:
            return {"count": 0}

        powers = [r.power_dbm for r in self._history]
        return {
            "count": len(powers),
            "mean_dbm": sum(powers) / len(powers),
            "min_dbm": min(powers),
            "max_dbm": max(powers),
            "std_dbm": self._std_dev(powers),
        }

    def get_history(self) -> List[SignalStrengthRecord]:
        """Get signal strength history."""
        return self._history.copy()

    def clear_history(self):
        """Clear measurement history."""
        self._history.clear()

    def _std_dev(self, values: list) -> float:
        """Compute standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(variance)
