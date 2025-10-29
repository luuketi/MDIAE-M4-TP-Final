
from typing import List, Self
import pandas as pd
from src.packet import Packet


class DataTransformer:
    """Transforms packet data into formats suitable for plotting."""

    @classmethod
    def using(cls, data: list[Packet]) -> Self:
        """Factory method to create a transformer with data."""
        obj = cls()
        obj._data = data
        return obj

    def to_dataframe(
        self, values_to_plot: List[str], column_names: List[str]
    ) -> pd.DataFrame:
        """
        Convert packet data to a pandas DataFrame.

        Args:
            values_to_plot: Names of attributes to extract.
            column_names: Names for the DataFrame columns.

        Returns:
            DataFrame containing the extracted data.
        """
        x, y = zip(*[packet.values_to_plot(values_to_plot) for packet in self._data])
        return pd.DataFrame({column_names[0]: x, column_names[1]: y})

    @staticmethod
    def add_time_intervals(
        df: pd.DataFrame, timestamp_column: str, interval_hours: int
    ) -> pd.DataFrame:
        """
        Add time interval categorization to DataFrame.

        Args:
            df: DataFrame with timestamp data.
            timestamp_column: Name of the timestamp column.
            interval_hours: Size of intervals in hours.

        Returns:
            DataFrame with added interval columns.
        """
        df["hour"] = df[timestamp_column].dt.hour
        df["hourly_interval"] = (df["hour"] // interval_hours) * interval_hours
        df["hourly_interval"] = df["hourly_interval"].astype(str) + ":00"
        return df

    @staticmethod
    def identify_eclipse_periods(
        df: pd.DataFrame, voltage_column: str, threshold: float = 32.0
    ) -> pd.DataFrame:
        """
        Identify eclipse periods based on voltage drops.
        
        Args:
            df: DataFrame with voltage data
            voltage_column: Name of the voltage column
            threshold: Voltage threshold below which we consider it an eclipse period
            
        Returns:
            DataFrame with added 'eclipse' boolean column
        """
        df["eclipse"] = df[voltage_column] < threshold
        return df
