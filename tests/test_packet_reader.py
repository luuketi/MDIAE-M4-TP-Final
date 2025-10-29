import pytest
import struct
from src.packet_reader import PacketReader
from src.packet import Packet
from datetime import datetime
import os


# A mock Packet class for testing purposes to isolate PacketReader tests
class MockPacket(Packet):
    def __init__(self, timestamp: datetime, voltage: float):
        self.timestamp = timestamp
        self.voltage = voltage

    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> "MockPacket":
        hour, voltage = struct.unpack("<HH", packet_bytes)
        return cls(timestamp=datetime(2024, 1, 1, hour), voltage=float(voltage))

    @classmethod
    def packet_size(cls) -> int:
        return 4

    def values_to_plot(self, values) -> tuple:
        return tuple(getattr(self, a) for a in values)


@pytest.fixture
def plot_output_file(tmp_path):
    """Fixture to provide a temporary output file path for plots and clean it up."""
    file_path = tmp_path / "output.png"
    yield str(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def valid_file(tmp_path):
    """Creates a temporary binary file with valid data."""
    file_path = tmp_path / "valid_data.bin"
    with open(file_path, "wb") as f:
        # Write 3 packets of 4 bytes each (hour, voltage)
        f.write(struct.pack("<HH", 1, 10))  # Packet 1: 01:00, 10V
        f.write(struct.pack("<HH", 2, 20))  # Packet 2: 02:00, 20V
        f.write(struct.pack("<HH", 3, 30))  # Packet 3: 03:00, 30V
    return file_path


@pytest.fixture
def invalid_file(tmp_path):
    """Creates a temporary binary file with an invalid size."""
    file_path = tmp_path / "invalid_data.bin"
    with open(file_path, "wb") as f:
        f.write(b"\x00" * 10)  # 10 bytes, not divisible by 4
    return file_path


def test_read_as_with_valid_file(valid_file):
    """Tests reading a valid file and parsing it into packets."""
    reader = PacketReader(str(valid_file))
    reader.read_as(MockPacket)
    assert len(reader.data) == 3
    assert isinstance(reader.data[0], MockPacket)
    assert reader.data[0].timestamp == datetime(2024, 1, 1, 1, 0)
    assert reader.data[1].timestamp == datetime(2024, 1, 1, 2, 0)
    assert reader.data[2].voltage == 30.0


def test_read_as_with_invalid_file_size(invalid_file):
    """Tests that reading a file with an invalid size raises a ValueError."""
    reader = PacketReader(str(invalid_file))
    expected_error = "Invalid file size. Expected a multiple of 4, but found 10"
    with pytest.raises(ValueError, match=expected_error):
        reader.read_as(MockPacket)
