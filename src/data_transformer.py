from typing import List, Self
import pandas as pd
from src.packet import Packet


class DataTransformer:
    """Transforms packet data into formats suitable for plotting."""

    @classmethod
    def using(cls, data: list[Packet]) -> Self:
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
        df = df.set_index([timestamp_column])
        df["hour"] = df.index.hour
        df["hourly_interval"] = df["hour"] // interval_hours

        num_intervals = 24 // interval_hours
        interval_labels = [
            f"{i*interval_hours:02d}:00-{(i+1)*interval_hours:02d}:00"
            for i in range(num_intervals)
        ]
        df["hourly_interval"] = pd.Categorical(
            df["hourly_interval"].apply(lambda x: interval_labels[x]),
            categories=interval_labels,
            ordered=True,
        )
        return df
