import os
from typing import Type
from .packet import Packet


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

    def get_data(self) -> list[Packet]:
        return self.data

    def __del__(self) -> None:
        """Ensure the file is closed when the object is deleted."""
        if hasattr(self, "file") and self.file is not None:
            self.file.close()
