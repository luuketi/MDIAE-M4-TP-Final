import os
from typing import Type
import matplotlib.pyplot as plt
from .packet import Packet
import pandas as pd
import seaborn as sns


class PacketReader:
    """
    A reader for binary files containing data packets.

    This class provides functionality to read a binary file, parse it into a
    series of data packets, and then generate various plots from the extracted data.
    """

    def __init__(self, file_path: str):
        """
        Initialize the PacketReader.

        Args:
            file_path: The path to the binary file to be read.
        """
        self.file_path = file_path
        self.file = open(file_path, "rb")
        self.data = []
        self.PacketClass = None

    def read_as(self, PacketClass: Type[Packet]) -> None:
        """
        Read the file and parse it as packets of a specific type.

        Args:
            PacketClass: The class of the packet to use for parsing.
                         This class should be a subclass of `Packet`.
        """
        self.PacketClass = PacketClass
        self._validate_file_size()
        while packet_bytes := self.file.read(self.PacketClass.packet_size()):
            packet = self.PacketClass.from_bytes(packet_bytes)
            self.data.append(packet)

    def _validate_file_size(self) -> None:
        """
        Validate that the file size is a multiple of the packet size.

        Raises:
            ValueError: If the file size is not a multiple of the packet size.
        """
        file_size = os.path.getsize(self.file_path)
        if file_size % self.PacketClass.packet_size() != 0:
            raise ValueError(
                f"Invalid file size. Expected a multiple of {self.PacketClass.packet_size()}, but found {file_size}"
            )

    def boxplot(
        self,
        output_file: str,
        interval_in_hours: int,
        x_axis: str,
        y_axis: str,
        y_label: str,
    ) -> None:
        """
        Generate a boxplot of the packet data over time intervals.

        Args:
            output_file: The path to save the generated plot image.
            interval_in_hours: The time interval in hours for grouping the data.
            x_axis: The name of the attribute to use for the x-axis (usually time).
            y_axis: The name of the attribute to use for the y-axis (the value to plot).
            y_label: The label for the y-axis.
        """
        x, y = zip(*[packet.values_to_plot(x_axis, y_axis) for packet in self.data])
        df = pd.DataFrame({x_axis: x, y_axis: y})
        df = df.set_index([x_axis])

        # Group by n-hour intervals of the day
        df["hour"] = df.index.hour
        df["hourly_interval"] = df["hour"] // interval_in_hours

        num_intervals = 24 // interval_in_hours
        interval_labels = [
            f"{i*interval_in_hours:02d}:00-{(i+1)*interval_in_hours:02d}:00"
            for i in range(num_intervals)
        ]
        df["hourly_interval"] = pd.Categorical(
            df["hourly_interval"].apply(lambda x: interval_labels[x]),
            categories=interval_labels,
            ordered=True,
        )

        fig, ax = plt.subplots(figsize=(15, 7))
        sns.boxplot(x="hourly_interval", y=y_axis, data=df, ax=ax, palette="hls")
        ax.set_title(
            f"Distribution of {y_label.title()} by {interval_in_hours}-Hour Intervals of the Day"
        )
        ax.set_xlabel(f"Time Interval ({interval_in_hours}-hour)")
        ax.set_ylabel(y_label)
        ax.grid(True, linestyle="--", alpha=0.7)
        fig.tight_layout()
        fig.savefig(output_file)
        plt.close(fig)

    def plot(
        self,
        output_file: str,
        x_axis: str,
        y_axis: str,
        title: str,
        x_label: str,
        y_label: str,
    ) -> None:
        """
        Generate a line plot of the packet data.

        Args:
            output_file: The path to save the generated plot image.
            x_axis: The name of the attribute for the x-axis.
            y_axis: The name of the attribute for the y-axis.
            title: The title of the plot.
            x_label: The label for the x-axis.
            y_label: The label for the y-axis.
        """
        x, y = zip(*[packet.values_to_plot(x_axis, y_axis) for packet in self.data])
        plt.plot(x, y, marker="o", linestyle="-", color="blue", linewidth=1)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.gcf().autofmt_xdate()
        plt.savefig(output_file)
        plt.clf()

    def __del__(self) -> None:
        """Ensure the file is closed when the object is deleted."""
        if hasattr(self, "file") and self.file is not None:
            self.file.close()
