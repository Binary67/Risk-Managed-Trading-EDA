import numpy as np
np.NaN = np.nan
import pandas as pd
import pandas_ta as ta


def GenerateEmaSignal(TradingDataframe: pd.DataFrame) -> pd.DataFrame:
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
    LengthList = [20, 60, 120]
    EmaDataframe = pd.concat(
        [ta.ema(ResultDataframe["Close"], length=Length) for Length in LengthList],
        axis=1,
    )
    EmaDataframe.columns = [f"EMA{Length}" for Length in LengthList]
    ResultDataframe[["EMA20", "EMA60", "EMA120"]] = EmaDataframe

    ConditionLong = (
        (ResultDataframe["EMA20"] > ResultDataframe["EMA60"])
        & (ResultDataframe["EMA60"] > ResultDataframe["EMA120"])
        & (ResultDataframe["Close"] > ResultDataframe["EMA20"])
    )

    ResultDataframe["Signal"] = 0
    ResultDataframe.loc[ConditionLong, "Signal"] = 1
    return ResultDataframe
