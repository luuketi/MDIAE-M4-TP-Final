
from src.plotter import LinePlotter, BoxPlotter
from .packet import SACDPacket
from .packet_reader import PacketReader
import argparse


def main():
    parser = argparse.ArgumentParser(description="SAC-D packet reader.")
    parser.add_argument("file_name", help="File name to read.")
    args = parser.parse_args()

    reader = PacketReader(args.file_name)
    reader.read_as(SACDPacket)

    LinePlotter.using(reader.get_data()).plot(
        ["timestamp", "voltage"],
        x_axis="timestamp",
        y_axis="voltage",
        title="SAC-D Voltages",
        x_label="Timestamp",
        y_label="Voltage (V)",
        show_eclipse=True,
    ).show().export("voltage_plot.png")

    boxplotter = BoxPlotter.using(reader.get_data())
    boxplotter.plot(
        ["timestamp", "voltage"],
        interval_in_hours=2,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    ).show()

    boxplotter.plot(
        ["timestamp", "voltage"],
        interval_in_hours=6,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    ).show()


if __name__ == "__main__":
    main()
