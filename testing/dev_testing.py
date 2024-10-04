from tradingtoolbox.utils import print
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


# def _dev():
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


async def main():
    # config = ExchangeConfig.create(config_file_path="./config/okx_config.json")
    # ex = Exchange.create(exchange_name="okx", config=config)

    config = ExchangeConfig.create(config_file_path="./config/bybit_config.json")
    ex = Exchange.create(exchange_name="bybit", config=config)

    await ex.load_contracts(reload=False)

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


async def _dev():
    await asyncio.gather(
        asyncio.create_task(main(), name="Main"),
    )


def dev():
    print("In dev")

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(_dev())


dev()
