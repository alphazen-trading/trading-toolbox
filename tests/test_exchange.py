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


async def init() -> Exchange:
    print("")
    # config = ExchangeConfig.create(config_file_path="./config/bybit_config.json")
    # ex = Exchange.create(exchange_name="bybit", config=config)

    config = ExchangeConfig.create(config_file_path="./config/okx_config.json")
    ex = Exchange.create(exchange_name="okx", config=config)

    await ex.load_contracts(reload=False)
    assert len(ex.contracts) == 2392
    return ex


@pytest.mark.asyncio
async def test_ohlc():
    ex = await init()

    contracts = ex.find_contracts(symbol_name="PEPE/USDT:USDT", contract_type="swap")
    for contract in contracts:
        candles = await ex.fetch_historical_ohlcv(
            contract, timeframe="1m", pages=1, reload=False
        )
        print(candles)
        ohlcv = candles.ohlcvs
        print(ohlcv[0].open)
        print(type(candles))

    await Cache.wait_till_all_tasks_complete()
    await ex.close()


@pytest.mark.asyncio
async def test_trades():
    ex = await init()
    print("Testing trades")
    contracts = ex.find_contracts(symbol_name="PEPE/USDT:USDT", contract_type="swap")
    for contract in contracts:
        bars = await ex.fetch_historical_trades(
            contract,
            since=time_manip.minutes_ago(30, to_timestamp=True),
            reload=True,
        )
        print(bars.trades[0].time)
        print(bars.trades[-1].time)
        print(len(bars.trades))
        bars.build_range_bars(threshold=0.26, is_percentage=True)
        print(len(bars.range_bars))

    # await asyncio.sleep(10)
    await Cache.wait_till_all_tasks_complete()
    await ex.close()
