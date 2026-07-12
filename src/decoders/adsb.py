"""ADS-B (Automatic Dependent Surveillance-Broadcast) decoder."""

import logging
import math
from typing import List, Dict
from dataclasses import dataclass, field

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


@dataclass
class ADSBMessage:
    """Decoded ADS-B message."""
    icao: str = ""
    message_type: int = 0
    category: str = ""
    altitude: int = 0
    latitude: float = 0.0
    longitude: float = 0.0
    heading: float = 0.0
    speed_knots: int = 0
    vertical_rate: int = 0
    squawk: str = ""
    callsign: str = ""
    emitter_category: str = ""
    raw: str = ""
    timestamp: float = 0.0


class ADSBDecoder:
    """ADS-B message decoder for aircraft tracking."""

    ADSB_FREQUENCY = 1090e6
    BIT_RATE = 1e6
    PREAMBLE = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]

    def __init__(self):
        self._messages: List[ADSBMessage] = []
        self._aircraft: Dict[str, ADSBMessage] = {}

    def decode(self, samples: IQSample) -> List[ADSBMessage]:
        """Decode ADS-B messages from IQ samples.

        Args:
            samples: IQSample at 1090 MHz

        Returns:
            List of decoded ADS-B messages
        """
        # In a real implementation:
        # 1. Detect preamble pattern
        # 2. Extract pulse positions
        # 3. Decode messages using PPM modulation
        messages = []
        logger.debug(f"Processing {len(samples.data)} samples for ADS-B")
        return messages

    def decode_message(self, data: bytes) -> ADSBMessage:
        """Decode a raw ADS-B message.

        Args:
            data: 14-byte ADS-B message

        Returns:
            Decoded ADSBMessage
        """
        msg = ADSBMessage()
        msg.raw = data.hex()

        if len(data) < 14:
            return msg

        # Extract Downlink Format
        df = (data[0] >> 3) & 0x1F
        if df != 17:
            return msg

        # Extract ICAO (bytes 1-3)
        msg.icao = f"{data[1]:02X}{data[2]:02X}{data[3]:02X}"

        # Extract message type (bits 32-36)
        msg.message_type = data[4] & 0x1F

        # Decode based on type
        if 1 <= msg.message_type <= 4:
            msg = self._decode_identification(msg, data)
        elif msg.message_type == 9:
            msg = self._decode_altitude(msg, data)
        elif msg.message_type in (10, 11):
            msg = self._decode_position(msg, data)
        elif msg.message_type == 19:
            msg = self._decode_velocity(msg, data)

        self._messages.append(msg)
        self._aircraft[msg.icao] = msg
        return msg

    def _decode_identification(self, msg: ADSBMessage, data: bytes) -> ADSBMessage:
        """Decode identification message (Types 1-4)."""
        # Category
        cat = (data[4] >> 5) | ((data[5] >> 5) & 0x06)
        categories = {
            0: "Reserved", 1: "Light", 2: "Small", 3: "Large",
            4: "High vortex large", 5: "Heavy", 6: "High performance",
            7: "Rotorcraft",
        }
        msg.emitter_category = categories.get(cat, f"Unknown ({cat})")

        # Callsign (6 chars, 6-bit encoding)
        chars = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        callsign = ""
        for i in range(6):
            c = (data[5 + i] >> 2) if i < 5 else data[10] & 0x3F
            idx = c & 0x3F
            if idx < len(chars):
                callsign += chars[idx]
        msg.callsign = callsign.strip()
        return msg

    def _decode_altitude(self, msg: ADSBMessage, data: bytes) -> ADSBMessage:
        """Decode altitude message (Type 9)."""
        alt_code = ((data[5] & 0x1F) << 4) | (data[6] >> 4)
        if alt_code & 0x01:
            msg.altitude = ((alt_code >> 1) & 0xFF) * 25 - 1000
        else:
            msg.altitude = ((alt_code >> 1) & 0xFF) * 100
        return msg

    def _decode_position(self, msg: ADSBMessage, data: bytes) -> ADSBMessage:
        """Decode position message (Types 10, 11)."""
        if len(data) >= 11:
            lat_cpr = ((data[6] & 0x03) << 15) | (data[7] << 7) | (data[8] >> 1)
            lon_cpr = ((data[8] & 0x01) << 16) | (data[9] << 8) | data[10]

            msg.latitude = (lat_cpr / (2 ** 17)) * 360 - 90
            msg.longitude = (lon_cpr / (2 ** 17)) * 360 - 180
        return msg

    def _decode_velocity(self, msg: ADSBMessage, data: bytes) -> ADSBMessage:
        """Decode velocity message (Type 19)."""
        subtype = data[5] & 0x07
        if subtype in (1, 2):
            ew_speed = ((data[5] >> 1) & 0x3FF)
            ns_speed = ((data[7] >> 1) & 0x3FF)
            msg.speed_knots = int(math.sqrt(ew_speed ** 2 + ns_speed ** 2))

            ew_vr = ((data[8] & 0x80) >> 6) | ((data[9] >> 7) & 0x01)
            msg.vertical_rate = ((data[9] & 0x7F) * (64 if ew_vr else -64))
        return msg

    def get_aircraft(self) -> Dict[str, ADSBMessage]:
        """Get all tracked aircraft."""
        return self._aircraft.copy()

    def get_messages(self) -> List[ADSBMessage]:
        return self._messages.copy()
