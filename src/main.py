from packet import SACDPacket
from packet_reader import PacketReader
import argparse


def main():
    parser = argparse.ArgumentParser(description="SAC-D packet reader.")
    parser.add_argument("file_name", help="File name to read.")
    args = parser.parse_args()
    reader = PacketReader(args.file_name)

    reader.read_as(SACDPacket)
    reader.plot(
        "voltages.png",
        x_axis="timestamp",
        y_axis="voltage",
        title="SAC-D Voltages",
        x_label="Timestamp",
        y_label="Voltage (V)",
    )
    reader.boxplot(
        "boxplot-voltages-2h.png",
        interval_in_hours=2,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    )
    reader.boxplot(
        "boxplot-voltages-6h.png",
        interval_in_hours=6,
        x_axis="timestamp",
        y_axis="voltage",
        y_label="Voltage (V)",
    )


if __name__ == "__main__":
    main()
