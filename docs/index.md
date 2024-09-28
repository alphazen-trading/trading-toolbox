Trading Toolbox

A Python library providing essential tools for traders to manage and interact with financial market data.
This library consists of three main modules: exchange kline download, database management, and general utilities.

Attributes:

- [clickhouse](reference/tradingtoolbox/clickhouse/__init__/): Functions for database-related operations.
- [exchanges](reference/tradingtoolbox/clickhouse/__init__/): Functions to download and manage OHLCV data.
- [utils](reference/tradingtoolbox/clickhouse/__init__/) : Utility functions for time manipulation, logging, and other tasks.


## Example:

Download OHLCV futures data from Binance

```python
from tradingtoolbox.exchanges import binanceklines, timeframes

klines = binanceklines()
ohlcv = klines.get_futures_klines(
    timeframes.tf_1hour, asset="btcusdt", ago="1 day ago utc"
)
```

Connect to a ClickHouse database, and write the OHLCV data to it

```python
from tradingtoolbox.clickhouse import ClickhouseSync

client = ClickhouseSync.create(
    host="localhost",
    port=8123,
    user="default",
    password="",
    database="default",
)

# Or you can create it without passing anything, and it will use the above defaults
async_client = ClickhouseSync.create()

client.insert_df(ohlcv, "OHLCV")
```

Upgraded Log that uses [rich](https://rich.readthedocs.io/en/stable/introduction.html) and writes to a file in a format friendly for loki. (Will be released in the future)

```python
from tradingtoolbox.utils import print

print(ohlv)

>>> [09/29/24 01:52:04]              open     high      low    close    volume    asset timeframe
                Date
                2024-09-27 19:00:00  65844.0  65953.9  65600.0  65612.8  5857.933  BTCUSDT        1h
                2024-09-27 20:00:00  65612.9  65884.3  65587.2  65770.1  3534.253  BTCUSDT        1h
                2024-09-27 21:00:00  65770.0  65854.8  65724.4  65785.1  2041.993  BTCUSDT        1h
                2024-09-27 22:00:00  65785.1  65950.0  65732.8  65839.0  3656.832  BTCUSDT        1h
                2024-09-27 23:00:00  65839.1  65885.2  65653.5  65749.6  3746.322  BTCUSDT        1h
                2024-09-28 00:00:00  65749.5  65880.0  65692.3  65876.3  2840.027  BTCUSDT        1h
                2024-09-28 01:00:00  65876.4  65980.0  65764.2  65959.2  2401.330  BTCUSDT        1h
                2024-09-28 02:00:00  65959.2  66161.7  65868.3  66131.3  5686.056  BTCUSDT        1h
                2024-09-28 03:00:00  66131.3  66237.0  65955.5  66041.0  4308.866  BTCUSDT        1h
                2024-09-28 04:00:00  66041.0  66060.1  65924.8  65982.0  2575.826  BTCUSDT        1h
                2024-09-28 05:00:00  65982.1  65997.5  65866.8  65922.2  2962.115  BTCUSDT        1h
                2024-09-28 06:00:00  65922.1  65930.1  65706.1  65778.7  4484.971  BTCUSDT        1h
                2024-09-28 07:00:00  65778.7  65870.0  65721.4  65790.0  2598.911  BTCUSDT        1h
                2024-09-28 08:00:00  65790.0  65790.1  65522.0  65606.9  6669.400  BTCUSDT        1h
                2024-09-28 09:00:00  65606.9  65617.2  65392.7  65602.3  7307.201  BTCUSDT        1h
                2024-09-28 10:00:00  65602.3  65745.0  65545.0  65730.6  3458.654  BTCUSDT        1h
                2024-09-28 11:00:00  65730.7  65775.8  65664.9  65761.5  2453.674  BTCUSDT        1h
                2024-09-28 12:00:00  65761.5  65765.3  65389.9  65508.4  7659.598  BTCUSDT        1h
                2024-09-28 13:00:00  65508.3  65574.3  65368.1  65498.2  4304.011  BTCUSDT        1h
                2024-09-28 14:00:00  65498.1  65796.8  65498.1  65689.9  5885.235  BTCUSDT        1h
                2024-09-28 15:00:00  65689.9  65689.9  65586.0  65593.7  2623.209  BTCUSDT        1h
                2024-09-28 16:00:00  65593.6  65640.7  65460.0  65485.9  3219.377  BTCUSDT        1h
                2024-09-28 17:00:00  65485.8  65696.0  65477.4  65603.0  2010.361  BTCUSDT        1h
                2024-09-28 18:00:00  65603.0  65798.7  65602.9  65736.0  1426.067  BTCUSDT        1h
```



