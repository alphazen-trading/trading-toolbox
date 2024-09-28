agg = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def resample(df, tf="1H", agg=agg, on="date"):
    """
    Create the docs for this
    """
    return df.resample(tf, on=on).agg(agg).dropna(how="all").fillna(method="ffill")
