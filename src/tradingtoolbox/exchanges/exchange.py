import ccxt
import ccxt.pro
import msgspec

from tradingtoolbox.exchanges.exchange_trades import ExchangeTrades
from tradingtoolbox.utils.cache import FileFormat
from .contract import Contract
from tradingtoolbox.rs import OHLCV, Bars
from .exchange_config import ExchangeConfig
from tradingtoolbox.utils import Cache, print

from .exchange_base import ExchangeBase
from .exchange_ohlcv import ExchangeOHLCV


class Exchange(ExchangeBase, ExchangeOHLCV, ExchangeTrades):
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
