import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src.plotter import LinePlotter, BoxPlotter
from src.packet import Packet


class MockPacket(Packet):
    """Mock packet class for testing."""

    def __init__(self, timestamp: datetime, voltage: float):
        self.timestamp = timestamp
        self.voltage = voltage

    @classmethod
    def from_bytes(cls, packet_bytes: bytes) -> "MockPacket":
        """Mock implementation of from_bytes."""
        return cls(timestamp=datetime.now(), voltage=0.0)

    @classmethod
    def packet_size(cls) -> int:
        """Mock implementation of packet_size."""
        return 8

    def values_to_plot(self, values: list[str]) -> tuple:
        return tuple(getattr(self, a) for a in values)


@pytest.fixture
def sample_data():
    """Fixture to provide sample packet data."""
    base_time = datetime(2024, 1, 1, 0, 0)
    data = []
    for i in range(48):  # 48 hours of data
        timestamp = base_time + timedelta(hours=i)
        voltage = 30.0 + (i % 10)  # Voltage varies between 30-40V
        data.append(MockPacket(timestamp=timestamp, voltage=voltage))
    return data


@pytest.fixture
def small_sample_data():
    """Fixture to provide a small sample of packet data."""
    data = [
        MockPacket(timestamp=datetime(2024, 1, 1, 0, 0), voltage=30.0),
        MockPacket(timestamp=datetime(2024, 1, 1, 1, 0), voltage=32.0),
        MockPacket(timestamp=datetime(2024, 1, 1, 2, 0), voltage=35.0),
    ]
    return data


class TestLinePlotter:
    """Tests for LinePlotter class."""

    def test_using_creates_instance(self, sample_data):
        """Test that using() creates a LinePlotter instance with data."""
        plotter = LinePlotter.using(sample_data)
        assert isinstance(plotter, LinePlotter)
        assert plotter._data == sample_data

    @patch("plotly.express.line")
    def test_plot_calls_plotly_express(self, mock_line, small_sample_data):
        """Test that plot() calls plotly express line correctly."""
        mock_figure = MagicMock()
        mock_line.return_value = mock_figure

        plotter = LinePlotter.using(small_sample_data)
        result = plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time",
            y_label="Voltage (V)",
            title="Test Plot",
        )

        assert result is plotter  # Test method chaining
        mock_line.assert_called_once()
        call_args = mock_line.call_args
        assert call_args[1]["x"] == "timestamp"
        assert call_args[1]["y"] == "voltage"
        assert call_args[1]["title"] == "Test Plot"
        assert call_args[1]["labels"]["timestamp"] == "Time"
        assert call_args[1]["labels"]["voltage"] == "Voltage (V)"

    def test_plot_extracts_correct_values(self, small_sample_data):
        """Test that plot() extracts correct x and y values."""
        plotter = LinePlotter.using(small_sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time",
            y_label="Voltage (V)",
            title="Test Plot",
        )

        expected_x = (
            datetime(2024, 1, 1, 0, 0),
            datetime(2024, 1, 1, 1, 0),
            datetime(2024, 1, 1, 2, 0),
        )
        expected_y = (30.0, 32.0, 35.0)
        assert plotter._x == expected_x
        assert plotter._y == expected_y

    def test_show_calls_figure_show(self, small_sample_data):
        """Test that show() calls the figure's show method."""
        plotter = LinePlotter.using(small_sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time",
            y_label="Voltage (V)",
            title="Test Plot",
        )
        plotter._figure = MagicMock()

        result = plotter.show()

        assert result is plotter  # Test method chaining
        plotter._figure.show.assert_called_once()

    def test_export_calls_write_image(self, small_sample_data):
        """Test that export() calls the figure's write_image method."""
        plotter = LinePlotter.using(small_sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time",
            y_label="Voltage (V)",
            title="Test Plot",
        )
        plotter._figure = MagicMock()

        result = plotter.export("output.png")

        assert result is plotter  # Test method chaining
        plotter._figure.write_image.assert_called_once_with("output.png")


class TestBoxPlotter:
    """Tests for BoxPlotter class."""

    def test_using_creates_instance(self, sample_data):
        """Test that using() creates a BoxPlotter instance with data."""
        plotter = BoxPlotter.using(sample_data)
        assert isinstance(plotter, BoxPlotter)
        assert plotter._data == sample_data

    @patch("plotly.express.box")
    def test_plot_calls_plotly_express(self, mock_box, sample_data):
        """Test that plot() calls plotly express box correctly."""
        mock_figure = MagicMock()
        mock_box.return_value = mock_figure

        plotter = BoxPlotter.using(sample_data)
        result = plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time Interval",
            y_label="Voltage (V)",
            title="Test Boxplot",
            interval_in_hours=2,
        )

        assert result is plotter  # Test method chaining
        mock_box.assert_called_once()

    def test_plot_creates_hourly_intervals(self, sample_data):
        """Test that plot() creates correct hourly intervals."""
        plotter = BoxPlotter.using(sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time Interval",
            y_label="Voltage (V)",
            title="Test Boxplot",
            interval_in_hours=2,
        )

        # Verify that data was extracted
        assert len(plotter._x) == len(sample_data)
        assert len(plotter._y) == len(sample_data)

    def test_plot_with_different_intervals(self, sample_data):
        """Test that plot() works with different interval sizes."""
        plotter = BoxPlotter.using(sample_data)

        # Test with 6-hour intervals
        result = plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time Interval",
            y_label="Voltage (V)",
            title="Test Boxplot",
            interval_in_hours=6,
        )

        assert result is plotter

    def test_show_calls_figure_show(self, sample_data):
        """Test that show() calls the figure's show method."""
        plotter = BoxPlotter.using(sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time Interval",
            y_label="Voltage (V)",
            title="Test Boxplot",
            interval_in_hours=2,
        )
        plotter._figure = MagicMock()

        result = plotter.show()

        assert result is plotter
        plotter._figure.show.assert_called_once()

    def test_export_calls_write_image(self, sample_data):
        """Test that export() calls the figure's write_image method."""
        plotter = BoxPlotter.using(sample_data)
        plotter.plot(
            values_to_plot=["timestamp", "voltage"],
            x_axis="timestamp",
            y_axis="voltage",
            x_label="Time Interval",
            y_label="Voltage (V)",
            title="Test Boxplot",
            interval_in_hours=2,
        )
        plotter._figure = MagicMock()

        result = plotter.export("boxplot.png")

        assert result is plotter
        plotter._figure.write_image.assert_called_once_with("boxplot.png")
