how = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def resample(df, tf="1H", agg=how, on="date"):
    return df.resample(tf, on=on).agg(agg=agg).dropna(how="all").fillna(method="ffill")
