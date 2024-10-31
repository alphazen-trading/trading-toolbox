import ccxt
import ccxt.pro
import msgspec
from datetime import datetime

from tradingtoolbox.utils.cache import FileFormat
from .contract import Contract
from tradingtoolbox.rs import Bars, Trade, Side
from .exchange_config import ExchangeConfig
from tradingtoolbox.utils import Cache, print


class ExchangeTrades:
    config: ExchangeConfig
    exchange_name: str
    exchange: ccxt.pro.Exchange
    contracts: dict[str, Contract] = {}
    file_name: str = ""

    async def fetch_historical_trades(
        self, contract: Contract, since, reload=False
    ) -> Bars:
        self.file_name = f"./data/{self.exchange_name}_{contract.id}_trades.parquet"
        cache = Cache(
            file_format=FileFormat.PARQUET,
            dump_format=FileFormat.NONE,
            cache_path=self.file_name,
            method=self._fetch_historical_trades,
        )
        # cache.clean_cache()
        data = await cache.get_async(reload=reload, contract=contract, since=since)

        bars = Bars()
        for i in range(len(data)):
            trade = data.iloc[i]
            side = Side.Long if trade.side == "buy" else Side.Short
            bar = Trade(
                contract.symbol,
                trade.timestamp_ms,
                trade.price,
                trade.size,
                side,
            )
            bars.add_trade(bar)

        return bars

    async def _fetch_historical_trades(self, contract: Contract, since) -> Bars:
        trades = await self.exchange.fetch_trades(
            contract.symbol,
            since=since,
            params={"paginate": True, "paginationDirection": "backward"},
        )  # dynamic/time-based pagination starting from 1664812416000
        print(len(trades))
        # # since = 1664812416000
        # d = datetime.fromtimestamp(since)
        # trades = []
        # while since < self.exchange.milliseconds():
        #     limit = 10000  # change for your limit
        #     _trades = await self.exchange.fetch_trades(contract.symbol, since, limit)
        #     if len(_trades) > 1:
        #         since = int(_trades[-1]["timestamp"])
        #         d = datetime.fromtimestamp(since / 1000)
        #         trades += _trades
        #     else:
        #         break
        # print(len(trades))

        if len(trades) > 0:
            bars = Bars()
            for trade in trades:
                side = Side.Long if trade["side"] == "buy" else Side.Short
                trade = Trade(
                    contract.symbol,
                    timestamp_ms=trade["timestamp"],
                    price=trade["price"],
                    size=trade["amount"],
                    side=side,
                )
                bars.add_trade(trade)
            bars.write_trades_to_parquet(self.file_name)
