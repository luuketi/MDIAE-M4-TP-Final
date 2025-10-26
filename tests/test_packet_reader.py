import pytest
import struct
from unittest.mock import patch, MagicMock
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

    def values_to_plot(self, *args) -> tuple:
        return tuple(getattr(self, a) for a in args)


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


@patch("matplotlib.pyplot.savefig")
@patch("matplotlib.pyplot.gcf")
@patch("matplotlib.pyplot.grid")
@patch("matplotlib.pyplot.title")
@patch("matplotlib.pyplot.ylabel")
@patch("matplotlib.pyplot.xlabel")
@patch("matplotlib.pyplot.plot")
@patch("matplotlib.pyplot.clf")
def test_plot_method_calls_matplotlib(
    mock_clf,
    mock_plot,
    mock_xlabel,
    mock_ylabel,
    mock_title,
    mock_grid,
    mock_gcf,
    mock_savefig,
    valid_file,
):
    """Tests that the plot method calls matplotlib correctly."""
    mock_fig = MagicMock()
    mock_gcf.return_value = mock_fig

    reader = PacketReader(str(valid_file))
    reader.read_as(MockPacket)
    reader.plot(
        "output.png",
        x_axis="timestamp",
        y_axis="voltage",
        title="Test Plot",
        x_label="Time",
        y_label="Voltage",
    )

    x_values = (
        datetime(2024, 1, 1, 1, 0),
        datetime(2024, 1, 1, 2, 0),
        datetime(2024, 1, 1, 3, 0),
    )
    y_values = (10.0, 20.0, 30.0)
    mock_plot.assert_called_once_with(
        x_values, y_values, marker="o", linestyle="-", color="blue", linewidth=1
    )
    mock_xlabel.assert_called_once_with("Time")
    mock_ylabel.assert_called_once_with("Voltage")
    mock_title.assert_called_once_with("Test Plot")
    mock_grid.assert_called_once_with(True)
    mock_gcf.assert_called_once()
    mock_fig.autofmt_xdate.assert_called_once()
    mock_savefig.assert_called_once_with("output.png")
    mock_clf.assert_called_once()


@patch("matplotlib.pyplot.subplots")
@patch("seaborn.boxplot")
def test_boxplot_method_calls_seaborn(mock_seaborn_boxplot, mock_subplots, valid_file):
    """Tests that the boxplot method calls seaborn and matplotlib correctly."""
    mock_ax = MagicMock()
    mock_fig = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    reader = PacketReader(str(valid_file))
    reader.read_as(MockPacket)
    reader.boxplot(
        "boxplot.png",
        interval_in_hours=2,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    )

    mock_subplots.assert_called_once_with(figsize=(15, 7))
    mock_seaborn_boxplot.assert_called_once()
    mock_ax.set_title.assert_called_once_with(
        "Distribution of Voltage (V) by 2-Hour Intervals of the Day"
    )
    mock_ax.set_xlabel.assert_called_once_with("Time Interval (2-hour)")
    mock_ax.set_ylabel.assert_called_once_with("Voltage (V)")
    mock_ax.grid.assert_called_once_with(True, linestyle="--", alpha=0.7)
    mock_fig.tight_layout.assert_called_once()
    mock_fig.savefig.assert_called_once_with("boxplot.png")


def test_boxplot_creates_file(valid_file, plot_output_file):
    """Tests that the boxplot method creates an output file."""
    reader = PacketReader(str(valid_file))
    reader.read_as(MockPacket)
    reader.boxplot(
        plot_output_file,
        interval_in_hours=2,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    )
    assert os.path.exists(plot_output_file)
