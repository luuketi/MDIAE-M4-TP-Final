from abc import ABC, abstractmethod
import struct
from collections import namedtuple
from datetime import datetime
from typing import Self, Tuple


Field = namedtuple("Field", "format position length")


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
    def values_to_plot(cls, *args) -> Tuple:
        pass


class SACDPacket(Packet):
    SCHEMA = {
        "timestamp": Field("<L", 598, 4),  # 4 bytes for 32-bit timestamp
        "voltage": Field(">H", 2354, 2),  # 2 bytes for 16-bit voltage
    }

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> Self:
        timestamp = cls._read_timestamp(packet_bytes)
        voltage = cls._read_voltage(packet_bytes)
        return cls(timestamp=timestamp, voltage=voltage)

    @classmethod
    def _read_timestamp(cls, packet_bytes: bytes) -> datetime:
        format, position, length = cls.SCHEMA["timestamp"]
        timestamp_raw = packet_bytes[position : position + length]
        timestamp = struct.unpack(format, timestamp_raw)[0]
        return datetime.fromtimestamp(timestamp)

    @classmethod
    def _read_voltage(cls, packet_bytes):
        format, position, length = cls.SCHEMA["voltage"]
        voltage_raw = packet_bytes[position : position + length]
        voltage = struct.unpack(format, voltage_raw)[0] * 0.01873128 - 38.682956
        return voltage

    @classmethod
    def packet_size(cls) -> int:
        return 4000

    def values_to_plot(self, *args) -> Tuple:
        return tuple(getattr(self, a) for a in args)
