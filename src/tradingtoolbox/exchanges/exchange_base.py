import ccxt
import ccxt.pro
import msgspec

from tradingtoolbox.utils.cache import FileFormat
from .contract import Contract
from tradingtoolbox.rs import OHLCV, Bars
from .exchange_config import ExchangeConfig
from tradingtoolbox.utils import Cache, print


class ExchangeBase(msgspec.Struct):
    config: ExchangeConfig
    exchange_name: str
    exchange: ccxt.pro.Exchange
    contracts: dict[str, Contract] = {}
    file_name: str = ""
