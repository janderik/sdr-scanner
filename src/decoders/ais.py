"""AIS (Automatic Identification System) decoder for maritime vessel tracking."""

import logging
import math
from typing import List, Dict, Optional
from dataclasses import dataclass

from ..scanner.models import IQSample

logger = logging.getLogger(__name__)


@dataclass
class AISMessage:
    """Decoded AIS message."""
    mmsi: int = 0
    message_type: int = 0
    vessel_name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    course_over_ground: float = 0.0
    speed_over_ground: float = 0.0
    heading: int = 0
    ship_type: str = ""
    destination: str = ""
    raw_payload: str = ""


class AISDecoder:
    """AIS (Automatic Identification System) message decoder."""

    AIS_FREQUENCIES = [161.975e6, 162.025e6]
    BIT_RATE = 9600
    ENCODING = "NRZI"

    def __init__(self):
        self._messages: List[AISMessage] = []

    def decode(self, samples: IQSample) -> List[AISMessage]:
        """Attempt to decode AIS messages from IQ samples.

        Args:
            samples: IQSample at AIS frequency

        Returns:
            List of decoded AIS messages
        """
        # In a real implementation, this would:
        # 1. Demodulate GMSK signal
        # 2. Extract HDLC frames
        # 3. Decode AIS payload
        # For now, return empty list (requires heavy DSP)
        messages = []
        logger.debug(f"Processing {len(samples.data)} samples for AIS decoding")
        return messages

    def decode_payload(self, payload: bytes) -> AISMessage:
        """Decode an AIS message payload.

        Args:
            payload: Decoded AIS payload bytes

        Returns:
            AISMessage with decoded fields
        """
        msg = AISMessage()
        msg.raw_payload = payload.hex()

        if len(payload) < 7:
            return msg

        # Extract message type (bits 0-5)
        msg.message_type = (payload[0] >> 2) & 0x3F

        # Extract MMSI (bits 8-37)
        msg.mmsi = int.from_bytes(payload[1:5], "big") & 0x3FFFFFFF

        # Decode based on message type
        if msg.message_type in (1, 2, 3):
            msg = self._decode_position(msg, payload)
        elif msg.message_type == 5:
            msg = self._decode_static(msg, payload)

        self._messages.append(msg)
        return msg

    def _decode_position(self, msg: AISMessage, payload: bytes) -> AISMessage:
        """Decode position report (Types 1, 2, 3)."""
        if len(payload) >= 12:
            # Course over ground (bytes 8-9)
            cog = int.from_bytes(payload[8:10], "big") & 0x3FF
            msg.course_over_ground = cog / 10.0

            # Speed over ground (bytes 10-11)
            sog = int.from_bytes(payload[10:12], "big") & 0x1FF
            msg.speed_over_ground = sog / 10.0

        return msg

    def _decode_static(self, msg: AISMessage, payload: bytes) -> AISMessage:
        """Decode static/voyage data (Type 5)."""
        if len(payload) >= 42:
            # Vessel name (bytes 26-41, 20 chars, 6-bit ASCII)
            name_bytes = payload[26:42]
            name = ""
            for b in name_bytes:
                c = b & 0x3F
                if 32 <= c < 96:
                    name += chr(c)
            msg.vessel_name = name.strip()

        return msg

    def get_messages(self) -> List[AISMessage]:
        return self._messages.copy()

    def get_vessels(self) -> Dict[int, AISMessage]:
        """Get latest message per vessel (by MMSI)."""
        vessels = {}
        for msg in self._messages:
            vessels[msg.mmsi] = msg
        return vessels
