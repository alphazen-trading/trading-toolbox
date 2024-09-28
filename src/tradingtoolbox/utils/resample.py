import pandas as pd
from pydantic import BaseModel, Field


class Aggregation(BaseModel):
    open: str = Field(default="first")
    """"""
    high: str = Field(default="max")
    """"""
    low: str = Field(default="min")
    """"""
    close: str = Field(default="last")
    """"""
    volume: str = Field(default="sum")
    """"""


def resample(
    df: pd.DataFrame, tf: str = "1H", agg: Aggregation = Aggregation(), on: str = "date"
) -> pd.DataFrame:
    """
    Resamples a DataFrame over a specified time frequency and applies aggregation functions.

    This function resamples the input DataFrame `df` using the time frequency provided by `tf`.
    It then applies the specified aggregation functions on the relevant columns and fills any
    missing values via forward fill.

    Parameters:
        df: The DataFrame to be resampled. It must contain a time-based column that can be used
            for resampling.
        tf: The time frequency for resampling, default is "1H" (one hour). It should be in a format
            accepted by pandas' `resample()` function, such as "1D" for daily, "1T" for minute, etc.
        agg: A dictionary defining the aggregation method for each relevant column. The default value
            aggregates the "open" column by the first value, "high" by the max, "low" by the min,
            "close" by the last value, and "volume" by the sum.
        on: The name of the column to be used for resampling, typically a date or timestamp column.
            The default is "date".

    Returns:
        A resampled DataFrame with the aggregation applied, missing values dropped, and any remaining missing values forward-filled.

    Examples:

    ```py
    import pandas as pd

    df = pd.DataFrame({
         "date": pd.date_range(start="2023-01-01", periods=5, freq="1H"),
         "open": [100, 101, 102, 103, 104],
         "high": [110, 111, 112, 113, 114],
         "low": [90, 91, 92, 93, 94],
         "close": [105, 106, 107, 108, 109],
         "volume": [1000, 1500, 1200, 1100, 1400]
     })
     resample(df, tf="2H", on="date")
    ```
    """
    return df.resample(tf, on=on).agg(agg).dropna(how="all").fillna(method="ffill")  # type: ignore
