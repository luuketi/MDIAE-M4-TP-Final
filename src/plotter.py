from abc import ABC, abstractmethod
from typing import Self

import plotly.express as px

from src.packet import Packet
from src.data_transformer import DataTransformer


class Plotter(ABC):
    """
    Abstract base class for creating plots from packet data.

    This class provides a common interface for different types of plotters,
    handling data initialization and output operations (show/export).
    Subclasses must implement the plot() method to define specific visualization logic.

    Attributes:
        _data (list[Packet]): The packet data to be plotted.
        _figure: The plotly figure object created by the plot method.
        _transformer (DataTransformer): Helper for data transformation.
    """

    @classmethod
    def using(cls, data: list[Packet]) -> Self:
        """
        Factory method to create a plotter instance with the given data.

        Args:
            data (list[Packet]): List of Packet objects containing the data to plot.

        Returns:
            Self: A new instance of the plotter class initialized with the data.
        """
        obj = cls()
        obj._data = data
        obj._figure = None
        obj._transformer = DataTransformer.using(data)
        return obj

    @abstractmethod
    def plot(
        self,
        values_to_plot: list[str],
        *args,
        **kwargs,
    ) -> Self:
        """
        Abstract method to create a plot from the data.

        Subclasses must implement this method to define their specific plotting logic.

        Args:
            values_to_plot (list[str]): Names of the packet attributes to extract and plot.
            *args: Additional positional arguments specific to the plotter implementation.
            **kwargs: Additional keyword arguments specific to the plotter implementation.

        Returns:
            Self: The plotter instance for method chaining.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def show(self) -> Self:
        """
        Display the generated plot in an interactive window.

        Returns:
            Self: The plotter instance for method chaining.
        """
        if self._figure is None:
            raise ValueError("No plot has been created. Call plot() first.")
        self._figure.show()
        return self

    def export(self, filename: str) -> Self:
        """
        Export the generated plot to an image file.

        Args:
            filename (str): Path where the image file will be saved.

        Returns:
            Self: The plotter instance for method chaining.
        """
        if self._figure is None:
            raise ValueError("No plot has been created. Call plot() first.")
        self._figure.write_image(filename, width=1920, height=1200, scale=2)
        return self


class LinePlotter(Plotter):
    """
    Plotter for creating line charts from packet data.

    This plotter creates a line chart with separate lines for each day in the dataset,
    useful for visualizing time-series data and comparing patterns across different days.
    """

    def plot(self, values_to_plot: list[str], *args, **kwargs) -> Self:
        """
        Create a line plot from the packet data.

        Args:
            values_to_plot (list[str]): Names of the packet attributes to extract.
            **kwargs: Required keyword arguments:
                - x_axis (str): Name of the column to use for x-axis.
                - y_axis (str): Name of the column to use for y-axis.
                - x_label (str): Label for the x-axis.
                - y_label (str): Label for the y-axis.
                - title (str): Title of the plot.

        Returns:
            Self: The plotter instance for method chaining.
        """
        x_axis = kwargs["x_axis"]
        y_axis = kwargs["y_axis"]
        x_label = kwargs["x_label"]
        y_label = kwargs["y_label"]
        title = kwargs["title"]

        df = self._transformer.to_dataframe(values_to_plot, [x_axis, y_axis])

        # Add a 'date' column to group by day
        df["date"] = df[x_axis].dt.date

        self._figure = px.line(
            df,
            x=x_axis,
            y=y_axis,
            labels={x_axis: x_label, y_axis: y_label},
            title=title,
            color="date",
        )

        return self


class BoxPlotter(Plotter):
    """
    Plotter for creating box plots from packet data.

    This plotter creates box plots showing the distribution of values across
    time intervals of the day (e.g., hourly, 2-hour, 4-hour intervals).
    Useful for analyzing patterns and variations throughout the day.
    """

    def plot(
        self,
        values_to_plot: list[str],
        *args,
        **kwargs,
    ) -> Self:
        """
        Create a box plot from the packet data grouped by time intervals.

        Args:
            values_to_plot (list[str]): Names of the packet attributes to extract.
            **kwargs: Required keyword arguments:
                - x_axis (str): Name of the column containing timestamps.
                - y_axis (str): Name of the column to use for y-axis values.
                - y_label (str): Label for the y-axis.
                - interval_in_hours (int): Size of time intervals in hours.

        Returns:
            Self: The plotter instance for method chaining.
        """
        x_axis = kwargs["x_axis"]
        y_axis = kwargs["y_axis"]
        y_label = kwargs["y_label"]
        interval_in_hours = kwargs["interval_in_hours"]

        df = self._transformer.to_dataframe(values_to_plot, [x_axis, y_axis])
        df = self._transformer.add_time_intervals(df, x_axis, interval_in_hours)

        self._figure = px.box(
            df,
            x="hourly_interval",
            y=y_axis,
            labels={
                x_axis: f"Time Interval ({interval_in_hours}-hour)",
                y_axis: y_label,
            },
            title=f"Distribution of {y_label.title()} by {interval_in_hours}-Hour Intervals of the Day",
        )
        return self
