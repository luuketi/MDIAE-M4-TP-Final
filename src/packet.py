from abc import ABC, abstractmethod
import struct
from collections import namedtuple
from datetime import datetime
from typing import Self, Tuple


Field = namedtuple("Field", "format position length")


class Packet(ABC):
    """Abstract base class for a data packet."""

    @classmethod
    @abstractmethod
    def from_bytes(cls, packet_bytes: bytes) -> Self:
        """Create a Packet instance from a byte sequence."""
        pass

    @classmethod
    @abstractmethod
    def packet_size(cls) -> int:
        """Return the size of the packet in bytes."""
        pass

    @abstractmethod
    def values_to_plot(cls, *args) -> Tuple:
        """Return a tuple of values to be plotted."""
        pass


class SACDPacket(Packet):
    """Represents a SAC-D satellite data packet."""

    SCHEMA = {
        "timestamp": Field("<L", 598, 4),  # 4 bytes for 32-bit timestamp
        "voltage": Field(">H", 2354, 2),  # 2 bytes for 16-bit voltage
    }

    def __init__(self, **kwargs):
        """
        Initialize a SACDPacket with data.

        Args:
            **kwargs: The fields of the packet as keyword arguments.
        """
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> Self:
        """
        Create a SACDPacket instance from a byte sequence.

        Args:
            packet_bytes: The raw bytes of the packet.

        Returns:
            A new SACDPacket instance.
        """
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
        """
        Return the size of the SAC-D packet in bytes.

        Returns:
            The packet size.
        """
        return 4000

    def values_to_plot(self, *args) -> Tuple:
        """
        Return a tuple of specified attribute values for plotting.

        Args:
            *args: The names of the attributes to return.

        Returns:
            A tuple containing the values of the requested attributes.
        """
        return tuple(getattr(self, a) for a in args)
