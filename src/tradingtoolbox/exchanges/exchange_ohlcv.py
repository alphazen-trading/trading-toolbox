import ccxt
import ccxt.pro
import msgspec

from tradingtoolbox.utils.cache import FileFormat
from .contract import Contract
from tradingtoolbox.rs import OHLCV, Bars
from .exchange_config import ExchangeConfig
from tradingtoolbox.utils import Cache, print


class ExchangeOHLCV:
    config: ExchangeConfig
    exchange_name: str
    exchange: ccxt.pro.Exchange
    contracts: dict[str, Contract] = {}
    file_name: str = ""

    async def fetch_historical_ohlcv(
        self, contract: Contract, timeframe="1d", pages=3, reload=False
    ) -> Bars:
        """
        Fetches historical OHLCV (Open, High, Low, Close, Volume) data for a specified contract.

        This asynchronous method retrieves the specified number of historical candle data pages
        for a given contract and timeframe. It can be used for various candle manipulation operations.

        Attributes:
            contract (Contract): The contract for which historical data is being fetched.
            timeframe (str): The time interval for the OHLCV data (default is "1d").
            pages (int): The number of pages of data to fetch (default is 3).
            reload (bool): Flag indicating whether to reload data if it exists (default is False).

        Returns:
            Bars: An instance of Bars containing the historical OHLCV data.

        Examples:
            >>> bars = await fetch_historical_ohlcv(contract, "1h", pages=5)
            >>> print(bars)
        """
        file_name = (
            f"./data/{self.exchange_name}_{contract.id}_{timeframe}_ohlcv.parquet"
        )
        cache = Cache(
            file_format=FileFormat.PARQUET,
            dump_format=FileFormat.NONE,
            cache_path=file_name,
            method=self._fetch_historical_ohlcv,
        )
        data = await cache.get_async(
            reload=reload, contract=contract, timeframe=timeframe, pages=pages
        )

        bars = Bars()
        for i in range(len(data)):
            candle = data.iloc[i]
            bar = OHLCV(
                contract.symbol,
                candle.timestamp_ms,
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            )
            bars.add_ohlcv(bar)

        return bars

    async def _fetch_historical_ohlcv(
        self, contract: Contract, timeframe="1d", pages=3
    ) -> Bars:
        file_name = (
            f"./data/{self.exchange_name}_{contract.id}_{timeframe}_ohlcv.parquet"
        )
        print("Fetching historical")

        candles = await self.exchange.fetch_ohlcv(
            contract.symbol,
            timeframe,
            params={"paginate": True, "paginationCalls": pages},
        )

        if len(candles) > 0:
            bars = Bars()
            for candle in candles:
                bar = OHLCV(contract.symbol, *candle)
                # print(bar)
                bars.add_ohlcv(bar)
            bars.write_ohlcv_to_parquet(file_name)
