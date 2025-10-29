import struct
from datetime import datetime
import pytest
from src.packet import SACDPacket


@pytest.fixture
def sample_packet_bytes() -> bytes:
    """
    Creates a sample 4000-byte packet for testing.

    This fixture simulates a real data packet with known values for
    timestamp and raw voltage at their specified offsets.
    """
    packet = bytearray(4000)

    # Known timestamp: 2023-01-01 00:00:00 UTC
    timestamp_val = 1672531200
    timestamp_bytes = struct.pack("<L", timestamp_val)

    # Known raw voltage value that results in approx 33.0V
    # Calculation: (33.0 + 38.682956) / 0.01873128 = 3827
    raw_voltage_val = 3827
    voltage_bytes = struct.pack(">H", raw_voltage_val)

    # Insert values into the packet at correct positions
    packet[598 : 598 + 4] = timestamp_bytes
    packet[2354 : 2354 + 2] = voltage_bytes

    return bytes(packet)


def test_sacd_packet_size():
    """
    Tests if SACDPacket.packet_size() returns the correct size.
    """
    assert SACDPacket.packet_size() == 4000


def test_sacd_packet_from_bytes(sample_packet_bytes):
    """
    Tests the from_bytes classmethod for correct parsing and calculation.
    """
    packet = SACDPacket.from_bytes(sample_packet_bytes)

    # Expected timestamp
    expected_timestamp = datetime.fromtimestamp(1672531200)

    # Expected voltage after applying the formula
    expected_voltage = 3827 * 0.01873128 - 38.682956

    assert isinstance(packet, SACDPacket)
    assert packet.timestamp == expected_timestamp
    pytest.approx(packet.voltage, 1e-6) == expected_voltage


def test_sacd_packet_values_to_plot():
    """
    Tests the values_to_plot method.
    """
    # Create a packet instance with known values
    timestamp = datetime.now()
    voltage = 33.5
    packet = SACDPacket(timestamp=timestamp, voltage=voltage)

    # Test retrieving a single value
    assert packet.values_to_plot(["timestamp"]) == (timestamp,)

    # Test retrieving multiple values
    assert packet.values_to_plot(["timestamp", "voltage"]) == (timestamp, voltage)

    # Test retrieving in a different order
    assert packet.values_to_plot(["voltage", "timestamp"]) == (voltage, timestamp)


def test_from_bytes_with_invalid_size():
    """
    Tests that from_bytes handles packets of incorrect size gracefully.
    The underlying struct.unpack will raise an error, which is expected.
    """
    invalid_packet = b"\x00" * 100  # Too short
    with pytest.raises(struct.error):
        SACDPacket.from_bytes(invalid_packet)
