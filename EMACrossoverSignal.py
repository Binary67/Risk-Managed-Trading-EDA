import pandas as pd
import pandas_ta as ta


def generate_ema_signal(TradingDataframe: pd.DataFrame) -> pd.DataFrame:
    """Generate trading signals using EMA crossover.

    A long signal is generated when:
    - EMA 20 > EMA 60
    - EMA 60 > EMA 120
    - Close > EMA 20

    Parameters
    ----------
    TradingDataframe : pd.DataFrame
        DataFrame containing columns: 'Open', 'High', 'Low', 'Close', 'Volume'.

    Returns
    -------
    pd.DataFrame
        DataFrame with added EMA columns and a 'Signal' column where 1
        represents a long position.
    """
    ResultDataframe = TradingDataframe.copy()
    ResultDataframe["EMA20"] = ta.ema(ResultDataframe["Close"], length=20)
    ResultDataframe["EMA60"] = ta.ema(ResultDataframe["Close"], length=60)
    ResultDataframe["EMA120"] = ta.ema(ResultDataframe["Close"], length=120)

    ConditionLong = (
        (ResultDataframe["EMA20"] > ResultDataframe["EMA60"])
        & (ResultDataframe["EMA60"] > ResultDataframe["EMA120"])
        & (ResultDataframe["Close"] > ResultDataframe["EMA20"])
    )

    ResultDataframe["Signal"] = 0
    ResultDataframe.loc[ConditionLong, "Signal"] = 1
    return ResultDataframe
