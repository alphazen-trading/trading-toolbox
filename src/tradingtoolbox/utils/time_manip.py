import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import *


class TimeManip:
    def __init__(self):
        pass

    # ================================================================================= #
    #                        PD Time Manipulation Methods                               #
    # ================================================================================= #
    def convert_ms_to_datetime(self, df: pd.DataFrame):
        return pd.to_datetime(df, unit="ms")

    def convert_s_to_datetime(self, df: pd.DataFrame):
        return pd.to_datetime(df, unit="s")

    def convert_datetime_to_s(self, df: pd.DataFrame):
        return pd.to_datetime(df).astype(np.int64) // 10**9

    def convert_datetime_to_ms(self, df: pd.DataFrame):
        return pd.to_datetime(df).astype(np.int64) // 10**6

    def convert_duration_to_timestamp(self, df: pd.DataFrame, unit="ms"):
        return pd.to_timedelta(df, unit=unit)

    # ============================================================================= #
    #                             PD TIME AGO                                       #
    # ============================================================================= #
    def pd_hours_ago(self, df: pd.DataFrame, hours=0):
        today = df.index.values[-1]
        hours_ago = today - pd.DateOffset(hours=hours)

        return df[df.index >= hours_ago]

    def pd_days_ago(self, df: pd.DataFrame, days=0):
        today = df.index.values[-1]
        months_ago = today - pd.DateOffset(days=days)

        return df[df.index >= months_ago]

    def pd_months_ago(self, df: pd.DataFrame, months=0):
        today = df.index.values[-1]
        months_ago = today - pd.DateOffset(months=months)

        return df[df.index >= months_ago]

    # ========================================================================== #
    #                             TIME AGO                                       #
    # ========================================================================== #
    def hours_ago(self, hours=0, to_timestamp=False):
        today = datetime.now()
        date = today - timedelta(hours=hours)
        if to_timestamp:
            return date.timestamp()
        return date

    def days_ago(self, days=0, to_timestamp=False):
        today = datetime.now()
        date = today - timedelta(days=days)
        if to_timestamp:
            return date.timestamp()
        return date

    def months_ago(self, months=0, to_timestamp=False):
        today = datetime.now()
        date = today - relativedelta(months=months)
        if to_timestamp:
            return date.timestamp()
        return date


time_manip = TimeManip()
