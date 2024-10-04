import ccxt
import ccxt.pro
import msgspec

from tradingtoolbox.utils.cache import FileFormat
from .contract import Contract
from tradingtoolbox.rs import OHLCV, Bars
from .exchange_config import ExchangeConfig
from tradingtoolbox.utils import Cache, print


class Exchange(msgspec.Struct):
    config: ExchangeConfig
    exchange_name: str
    exchange: ccxt.pro.Exchange
    contracts: dict[str, Contract] = {}

    @staticmethod
    def available_exchanges():
        return ccxt.pro.exchanges

    @classmethod
    def create(cls, **kwargs):
        exchange_name = kwargs["exchange_name"]
        if exchange_name not in ccxt.pro.exchanges:
            raise ValueError(f"Exchange {exchange_name} not available")

        config = msgspec.json.decode(msgspec.json.encode(kwargs["config"]))
        kwargs["exchange"] = getattr(ccxt.pro, exchange_name)(config)
        self = cls(**kwargs)

        return self

    async def load_contracts(self, reload=True) -> dict:
        cache = Cache(
            cache_path=f"./cache/{self.exchange_name}_markets.json",
            method=self.exchange.load_markets,
        )
        self.contracts = {}
        data = await cache.get_async(reload=reload)

        for key in data:
            curr = Contract(**data[key])
            self.contracts[key] = curr

        return self.contracts

    async def close(self):
        await self.exchange.close()

    def find_contracts(self, symbol_name: str, contract_type: str) -> list[Contract]:
        matches = []
        for key in self.contracts:
            if symbol_name in self.contracts[key].symbol:
                contract = self.contracts[key]
                if contract.type == contract_type:
                    matches.append(contract)
        return matches

    async def fetch_historical_ohlcv(
        self, contract: Contract, timeframe="1d", pages=3, reload=False
    ):
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
        return data

    async def _fetch_historical_ohlcv(
        self, contract: Contract, timeframe="1d", pages=3
    ):
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
