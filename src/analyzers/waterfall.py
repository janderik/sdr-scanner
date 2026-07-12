"""Waterfall (spectrogram) display data generation."""

import math
from typing import List, Tuple


class WaterfallGenerator:
    """Generates waterfall/spectrogram display data."""

    def __init__(self, num_rows: int = 100, num_cols: int = 256):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._buffer: List[List[float]] = []

    def add_row(self, power_spectrum: List[float]) -> List[float]:
        """Add a row to the waterfall display.

        Args:
            power_spectrum: Power values in dB

        Returns:
            Normalized values for display (0-255)
        """
        # Resample to fit column count
        resampled = self._resample(power_spectrum, self.num_cols)

        # Normalize to 0-255
        if resampled:
            min_val = min(resampled)
            max_val = max(resampled)
            range_val = max_val - min_val if max_val != min_val else 1
            normalized = [int((v - min_val) / range_val * 255) for v in resampled]
        else:
            normalized = [0] * self.num_cols

        self._buffer.append(normalized)

        # Trim to max rows
        if len(self._buffer) > self.num_rows:
            self._buffer = self._buffer[-self.num_rows:]

        return normalized

    def get_display_data(self) -> List[List[int]]:
        """Get the current waterfall display data."""
        return self._buffer.copy()

    def _resample(self, data: List[float], target_length: int) -> List[float]:
        """Resample data to target length."""
        if not data or target_length <= 0:
            return []

        if len(data) == target_length:
            return data

        result = []
        for i in range(target_length):
            idx = i * (len(data) - 1) / (target_length - 1) if target_length > 1 else 0
            idx_int = int(idx)
            frac = idx - idx_int
            if idx_int >= len(data) - 1:
                result.append(data[-1])
            else:
                result.append(data[idx_int] * (1 - frac) + data[idx_int + 1] * frac)

        return result

    @staticmethod
    def color_map(value: int) -> Tuple[int, int, int]:
        """Map a 0-255 value to RGB color using a heatmap."""
        if value < 64:
            return (0, 0, value * 4)
        elif value < 128:
            return (0, (value - 64) * 4, 255)
        elif value < 192:
            return ((value - 128) * 4, 255, 255 - (value - 128) * 4)
        else:
            return (255, 255 - (value - 192) * 4, 0)
