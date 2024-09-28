from binance.client import Client
from enum import Enum
import pandas as pd
import os

from pydantic import BaseModel, ConfigDict


class Timeframes(Enum):
    """
    Timeframes for Binance

    Usage:

    Attributes:
        TF_1MINUTE (Literal): Binance 1 minute interval.
        TF_3MINUTE (Literal): Binance 3 minute interval.
        TF_5MINUTE (Literal): Binance 5 minute interval.
        TF_15MINUTE (Literal): Binance 15 minute interval.
        TF_30MINUTE (Literal): Binance 30 minute interval.
        TF_1HOUR (Literal): Binance 1 hour interval.
        TF_2HOUR (Literal): Binance 2 hour interval.
        TF_4HOUR (Literal): Binance 4 hour interval.
        TF_6HOUR (Literal): Binance 6 hour interval.
        TF_8HOUR (Literal): Binance 8 hour interval.
        TF_12HOUR (Literal): Binance 12 hour interval.
        TF_1DAY (Literal): Binance 1 day interval.
        TF_3DAY (Literal): Binance 3 day interval.
        TF_1WEEK (Literal): Binance 1 week interval.
        TF_1MONTH (Literal): Binance 1 month interval.
    """

    TF_1MINUTE = Client.KLINE_INTERVAL_1MINUTE
    TF_3MINUTE = Client.KLINE_INTERVAL_3MINUTE
    TF_5MINUTE = Client.KLINE_INTERVAL_5MINUTE
    TF_15MINUTE = Client.KLINE_INTERVAL_15MINUTE
    TF_30MINUTE = Client.KLINE_INTERVAL_30MINUTE
    TF_1HOUR = Client.KLINE_INTERVAL_1HOUR
    TF_2HOUR = Client.KLINE_INTERVAL_2HOUR
    TF_4HOUR = Client.KLINE_INTERVAL_4HOUR
    TF_6HOUR = Client.KLINE_INTERVAL_6HOUR
    TF_8HOUR = Client.KLINE_INTERVAL_8HOUR
    TF_12HOUR = Client.KLINE_INTERVAL_12HOUR
    TF_1DAY = Client.KLINE_INTERVAL_1DAY
    TF_3DAY = Client.KLINE_INTERVAL_3DAY
    TF_1WEEK = Client.KLINE_INTERVAL_1WEEK
    TF_1MONTH = Client.KLINE_INTERVAL_1MONTH

    def __str__(self):
        return self.value


class BinanceKlines(BaseModel):
    """
    A class that allows downloading klines from Binance.

    Usage:
        ```python
        from tradingtoolbox.exchanges import BinanceKlines, Timeframes

        klines = BinanceKlines()
        df = klines.get_futures_klines(
            Timeframes.TF_1HOUR, asset="BTCUSDT", ago="1 day ago UTC"
        )
        ```
    """

    client: Client = Client()

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
    )

    def _create_binance_dataframe(self, klines: list, set_index: bool):
        columns = [
            "Open Time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close time",
            "Quote asset volume",
            "Number of trades",
            "Taker buy base asset volume",
            "Taker buy quote asset volume",
            "Ignore",
        ]
        df = pd.DataFrame(
            klines,
            dtype=float,
            columns=columns,  # type: ignore
        )

        df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
        df.drop(
            columns=[
                "Close time",
                "Quote asset volume",
                "Number of trades",
                "Taker buy base asset volume",
                "Taker buy quote asset volume",
                "Ignore",
            ],
            inplace=True,
        )
        # Rename columns using a dictionary
        new_column_names = {
            "Open Time": "Date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
        df = df.rename(columns=new_column_names)
        if set_index:
            df.set_index("Date", inplace=True)

        return df

    def _create_data_dir(self, directory="./data"):
        os.makedirs(directory, exist_ok=True)

    def _get_klines(
        self,
        asset_type: str,
        tf: Timeframes,
        asset="BTCUSDT",
        ago="1 day ago UTC",
        cache=True,
        data_directory="./data",
        set_index=True,
    ) -> pd.DataFrame:
        file = f"./data/binance_{asset_type}_{asset}_{tf}_klines.parquet"
        self._create_data_dir(directory=data_directory)
        if cache:
            self._create_data_dir(directory=data_directory)
            if os.path.exists(file):
                df = pd.read_parquet(file)
                return df
        if asset_type == "futures":
            klines = self.client.futures_historical_klines(asset, tf.value, ago)
        else:
            klines = self.client.get_historical_klines(asset, tf.value, ago)

        df = self._create_binance_dataframe(klines, set_index)
        df["asset"] = asset
        df["timeframe"] = tf.value
        df.to_parquet(file)
        return df

    def get_futures_klines(
        self,
        tf: Timeframes,
        asset: str = "BTCUSDT",
        ago: str = "1 day ago UTC",
        cache: bool = True,
        data_directory: str = "./data",
        set_index: bool = True,
    ) -> pd.DataFrame:
        """
        Fetches the Futures (Perp Swaps) klines

        Parameters:
            tf: The timeframe to fetch.
            asset: The asset name.
            ago: The time ago you want to fetch it. Ex: '30 day ago UTC', or '3 months ago UTC'
            cache: Whether to cache the data. Subsequent calls will **not** call the API.
            data_directory: The directory where the klines fill be stored as parquet files
            set_index: Whether to set the index of the returned DataFrame. If True, the 'Date' column will be set as index
        """
        return self._get_klines(
            asset_type="futures",
            tf=tf,
            asset=asset,
            ago=ago,
            cache=cache,
            data_directory=data_directory,
            set_index=set_index,
        )

    def get_klines(
        self,
        tf: Timeframes,
        asset="BTCUSDT",
        ago="1 day ago UTC",
        cache=True,
        data_directory="./data",
        set_index=True,
    ) -> pd.DataFrame:
        return self._get_klines(
            asset_type="spot",
            tf=tf,
            asset=asset,
            ago=ago,
            cache=cache,
            data_directory=data_directory,
            set_index=set_index,
        )
