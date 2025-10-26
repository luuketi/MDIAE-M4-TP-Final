from packet import SACDPacket
from packet_reader import PacketReader
import argparse

def main():
    parser = argparse.ArgumentParser(description="SAC-D packet reader.")
    parser.add_argument("file_name", help="File name to read.")

    args = parser.parse_args()
    reader = PacketReader(args.file_name)
    reader.read_as(SACDPacket)
    reader.plot("voltages.png")
    reader.boxplot("boxplot-voltages-2h.png", 2)
    reader.boxplot("boxplot-voltages-6h.png", 6)


if __name__ == "__main__":
    main()