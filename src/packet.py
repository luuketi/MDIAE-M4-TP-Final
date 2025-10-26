from abc import ABC, abstractmethod
import struct
from datetime import datetime
from typing import Any, Self

class Packet(ABC):
    @classmethod
    @abstractmethod
    def from_bytes(cls, packet_bytes: bytes) -> Self:
        pass

    @classmethod
    @abstractmethod
    def packet_size(cls) -> int:
        pass

    @abstractmethod
    def values_to_plot(cls) -> (Any, Any):
        pass


class SACDPacket(Packet):

    def __init__(self, timestamp: datetime, voltage: float):
        super().__init__()
        self.timestamp = timestamp
        self.voltage = voltage

    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> Self:
        timestamp = cls._read_timestamp(packet_bytes)
        voltage = cls._read_voltage(packet_bytes)
        return cls(timestamp, voltage)

    @classmethod
    def _read_timestamp(cls, packet_bytes: bytes) -> datetime:
        TIMESTAMP_POSITION = 598
        TIMESTAMP_LEN = 4  # 4 bytes for 32-bit timestamp
        timestamp_raw = packet_bytes[TIMESTAMP_POSITION: TIMESTAMP_POSITION + TIMESTAMP_LEN]
        timestamp = struct.unpack("<L", timestamp_raw)[0]
        return datetime.fromtimestamp(timestamp)

    @classmethod
    def _read_voltage(cls, packet_bytes):
        VOLTAGE_POSITION = 2354
        VOLTAGE_LEN = 2  # 2 bytes for 16-bit voltage
        voltage_raw = packet_bytes[VOLTAGE_POSITION: VOLTAGE_POSITION + VOLTAGE_LEN]
        voltage = struct.unpack(">H", voltage_raw)[0] * 0.01873128 - 38.682956
        return voltage

    @classmethod
    def packet_size(cls) -> int:
        return 4000

    def values_to_plot(self) -> (Any, Any):
        return self.timestamp, self.voltage

