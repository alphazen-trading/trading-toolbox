import pandas as pd
import requests
from numpy.typing import NDArray
from datetime import datetime
import os
import time


class OKXKlines:
    """
    A class that helps downloading klines from OKX.

    Usage:
        ```python
        from tradingtoolbox.exchanges import OKXKlines


        klines = OKXKlines()
        df = klines.load_klines(
            "PEPE-USDT-SWAP", "1m", days_ago=30
        )
        ```
    """

    def _get_kline_file_name(self, instrument: str, tf: str):
        return f"./data/kline_{instrument}_{tf}.parquet"

    def _find_kline_file(self, instrument: str, tf: str):
        path = self._get_kline_file_name(instrument, tf)

        if not os.path.exists("./data"):
            os.mkdir("./data")
        if os.path.exists(path):
            df = pd.read_parquet(path)
            return df
        return None

    def _parse_klines(self, klines: NDArray) -> pd.DataFrame:
        values = []
        columns = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "volCcy",
            "volCcyQuote",
            "confirm",
        ]
        for line in klines:
            float_line = [float(element) for element in line]
            values.append(float_line)

        df = pd.DataFrame(values, columns=columns)  # type: ignore
        df.drop(columns=["volCcy", "volCcyQuote", "confirm"], inplace=True)
        df = df.sort_values(by=["date"], ascending=True)
        # df["date"] = pd.to_datetime(df["date"], unit="ms")
        return df

    def load_klines(
        self, instrument: str, tf: str, days_ago: int = 1, end=datetime.now()
    ) -> pd.DataFrame:
        """
        Load klines from the past X days.
        OKX's api is limited in to a max of 100 items. This method, will loop until it finds the amount needed

        Parameters:
            instrument: The instrument to fetch
            tf: The timeframe to fetch
            days_ago: The number of days ago to look at
            end: The end date
        """
        df = self._find_kline_file(instrument, tf)

        if df is None:
            df = self._fetch_lines(instrument, tf, None)

        start_date = end - pd.Timedelta(days=days_ago)
        while start_date.timestamp() < df["date"].min():  # type: ignore
            new_df = self._fetch_lines(instrument, tf, df["date"].min())
            df = pd.concat([df, new_df])
            df["d"] = pd.to_datetime(df["date"], unit="ms")
            name = self._get_kline_file_name(instrument, tf)
            print(name)
            df.to_parquet(self._get_kline_file_name(instrument, tf))
            time.sleep(0.1)
            print(df)

        df = df.sort_values(by=["date"], ascending=True)
        df["date"] = pd.to_datetime(df["date"], unit="ms")
        return df

    def _fetch_lines(self, instrument: str, tf: str, before=None) -> pd.DataFrame:
        url = f"https://www.okx.com/api/v5/market/history-candles?instId={instrument}&bar={tf}&limit=100"
        if before:
            url += f"&after={int(before)}"
        response = requests.get(
            url,
            timeout=10,
        )
        if response.status_code == 200:
            return self._parse_klines(response.json()["data"])
        else:
            return pd.DataFrame()
