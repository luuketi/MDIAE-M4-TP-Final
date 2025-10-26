import os
from typing import Type
import matplotlib.pyplot as plt
from packet import Packet
import pandas as pd
import seaborn as sns


class PacketReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = open(file_path, "rb")
        self.data = []
        self.PacketClass = None

    def read_as(self, PacketClass: Type[Packet]) -> None:
        self.PacketClass = PacketClass
        self._validate_file_size()
        while packet_bytes := self.file.read(self.PacketClass.packet_size()):
            packet = self.PacketClass.from_bytes(packet_bytes)
            self.data.append(packet)

    def _validate_file_size(self) -> None:
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

    def plot(
        self,
        output_file: str,
        x_axis: str,
        y_axis: str,
        title: str,
        x_label: str,
        y_label: str,
    ) -> None:
        x, y = zip(*[packet.values_to_plot(x_axis, y_axis) for packet in self.data])
        plt.plot(x, y, marker="o", linestyle="-", color="blue", linewidth=1)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.gcf().autofmt_xdate()
        plt.savefig(output_file)

    def __del__(self) -> None:
        if hasattr(self, "file") and self.file is not None:
            self.file.close()
