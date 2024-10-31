from tradingtoolbox.utils import print
import pytest

from tradingtoolbox.clickhouse import ClickhouseSync, ClickhouseAsync

from tradingtoolbox.utils.time_manip import time_manip

import pandas as pd
import asyncio
import uvloop
import msgspec
import ccxt
import ccxt.pro
from tradingtoolbox.utils import print
from tradingtoolbox.exchanges import Exchange, ExchangeConfig
from tradingtoolbox.utils import Cache
# from tradingtoolbox.exchanges.binance import BinanceKlines, Timeframes


def test_clickhouse():
    print("Hello")

    # logger.warning("Warning")
    # logger.error("Error message")

    a = 4
    assert a == 4


#     bt = BinanceKlines()
#     df = bt.get_futures_klines(
#         Timeframes.TF_1HOUR, asset="BTCUSDT", ago="1 day ago UTC"
#     )
#     print(df)

#     klines = OKXKlines()
#     df = klines.load_klines("PEPE-USDT-SWAP", "1m", days_ago=30)
#     print(df)

#     ch = ClickhouseSync.create()
#     a = ch.client.command("SELECT 1")
#     print(a)
#     # self.clickhouse = await Clickhouse.create()
#     dic = {"test": "123"}
#     print("Hello wotld", 123, dic)

#     async def main():
#         ch = await ClickhouseAsync.create()
#         a = await ch.async_client.command("SELECT 1")
#         print(a)

#     asyncio.run(main())

#     days = time_manip.days_ago(3)
#     print(days)
