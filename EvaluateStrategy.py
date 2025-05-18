import pandas as pd
import pandas_ta as ta
from backtesting import Backtest
import math
from BaseTradingStrategy import BaseTradingStrategy

def AtrIndicator(HighSeries: pd.Series, LowSeries: pd.Series, CloseSeries: pd.Series, Length: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)."""
    return ta.atr(high=HighSeries, low=LowSeries, close=CloseSeries, length=Length)


def EvaluateFullCapitalStrategy(TradingDataframe: pd.DataFrame, InitialCash: float = 10000) -> tuple:
    """Evaluate strategy without any risk management."""

    def EntryLogic(Self) -> None:
        if Self.data.Signal[-1] == 1 and not Self.position:
            Self.buy()

    def ExitLogic(Self) -> None:
        if Self.data.Signal[-1] == 0 and Self.position:
            Self.position.close()

    class FullCapitalStrategy(BaseTradingStrategy):
        EntryCallback = EntryLogic
        ExitCallback = ExitLogic

    BacktestInstance = Backtest(TradingDataframe, FullCapitalStrategy, cash=InitialCash, commission=0.0)
    Output = BacktestInstance.run()
    return Output['Return [%]'], Output['Sharpe Ratio']


def EvaluateFixedStopStrategy(
    TradingDataframe: pd.DataFrame,
    AtrMultiplier: float = 2.0,
    RiskPercent: float = 1.0,
    InitialCash: float = 10000,
    AtrPeriod: int = 14,
) -> tuple:
    """Evaluate strategy with fixed stop-loss using ATR."""

    def SetupLogic(Self) -> None:
        Self.Atr = Self.I(AtrIndicator, Self.data.High, Self.data.Low, Self.data.Close, AtrPeriod)

    def EntryLogic(Self) -> None:
        if Self.data.Signal[-1] == 1 and not Self.position:
            CurrentAtr = Self.Atr[-1]
            EntryPrice = Self.data.Close[-1]
            StopPrice = EntryPrice - AtrMultiplier * CurrentAtr
            RiskPerUnit = EntryPrice - StopPrice
            EquityRisk = Self.equity * (RiskPercent / 100)
            Size = min(EquityRisk / RiskPerUnit, Self.equity / EntryPrice)
            if Size > 0:
                Self.buy(size=Size, sl=StopPrice)

    def ExitLogic(Self) -> None:
        if Self.data.Signal[-1] == 0 and Self.position:
            Self.position.close()

    class FixedStopStrategy(BaseTradingStrategy):
        InitCallback = SetupLogic
        EntryCallback = EntryLogic
        ExitCallback = ExitLogic

    BacktestInstance = Backtest(TradingDataframe, FixedStopStrategy, cash=InitialCash, commission=0.0)
    Output = BacktestInstance.run()
    return Output['Return [%]'], Output['Sharpe Ratio']


def EvaluateTrailingStopStrategy(
    TradingDataframe: pd.DataFrame,
    AtrMultiplier: float = 3.0,
    VolatilityCap: float = 0.02,
    InitialCash: float = 10000,
    AtrPeriod: int = 14,
) -> tuple:
    """Evaluate strategy with trailing stop and daily volatility cap."""

    def SetupLogic(Self) -> None:
        Self.Atr = Self.I(AtrIndicator, Self.data.High, Self.data.Low, Self.data.Close, AtrPeriod)

    def StopLogic(Self) -> None:
        if Self.position:
            CurrentAtr = Self.Atr[-1]
            NewStop = Self.data.Close[-1] - AtrMultiplier * CurrentAtr
            for Trade in Self.trades:
                if Trade.sl is None or NewStop > Trade.sl:
                    Trade.sl = NewStop

    def EntryLogic(Self) -> None:
        CurrentAtr = Self.Atr[-1]
        RangePct = (Self.data.High[-1] - Self.data.Low[-1]) / Self.data.Close[-1]
        if Self.data.Signal[-1] == 1 and not Self.position and RangePct <= VolatilityCap:
            EntryPrice = Self.data.Close[-1]
            StopPrice = EntryPrice - AtrMultiplier * CurrentAtr
            Size = math.floor(Self.equity / EntryPrice)
            Self.buy(size=Size, sl=StopPrice)

    def ExitLogic(Self) -> None:
        if Self.data.Signal[-1] == 0 and Self.position:
            Self.position.close()

    class TrailingStopStrategy(BaseTradingStrategy):
        InitCallback = SetupLogic
        EntryCallback = EntryLogic
        ExitCallback = ExitLogic
        StopCallback = StopLogic

    BacktestInstance = Backtest(TradingDataframe, TrailingStopStrategy, cash=InitialCash, commission=0.0)
    Output = BacktestInstance.run()
    return Output['Return [%]'], Output['Sharpe Ratio']
