import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy


def AtrIndicator(HighSeries: pd.Series, LowSeries: pd.Series, CloseSeries: pd.Series, Length: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)."""
    return ta.atr(high=HighSeries, low=LowSeries, close=CloseSeries, length=Length)


def EvaluateFullCapitalStrategy(TradingDataframe: pd.DataFrame, InitialCash: float = 10000) -> tuple:
    """Evaluate strategy without any risk management."""

    class FullCapitalStrategy(Strategy):
        def init(self):
            pass
        def next(self):
            if self.data.Signal[-1] == 1:
                if not self.position:
                    self.buy()
            else:
                if self.position:
                    self.position.close()

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

    class FixedStopStrategy(Strategy):
        def init(self):
            self.Atr = self.I(AtrIndicator, self.data.High, self.data.Low, self.data.Close, AtrPeriod)

        def next(self):
            if self.data.Signal[-1] == 1:
                if not self.position:
                    CurrentAtr = self.Atr[-1]
                    EntryPrice = self.data.Close[-1]
                    StopPrice = EntryPrice - AtrMultiplier * CurrentAtr
                    RiskPerUnit = EntryPrice - StopPrice
                    EquityRisk = self.equity * (RiskPercent / 100)
                    Size = min(EquityRisk / RiskPerUnit, self.equity / EntryPrice)
                    if Size > 0:
                        self.buy(size=Size, sl=StopPrice)
            else:
                if self.position:
                    self.position.close()

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

    class TrailingStopStrategy(Strategy):
        def init(self):
            self.Atr = self.I(AtrIndicator, self.data.High, self.data.Low, self.data.Close, AtrPeriod)

        def next(self):
            CurrentAtr = self.Atr[-1]
            RangePct = (self.data.High[-1] - self.data.Low[-1]) / self.data.Close[-1]
            if self.position:
                NewStop = self.data.Close[-1] - AtrMultiplier * CurrentAtr
                for Trade in self.trades:
                    if Trade.sl is None or NewStop > Trade.sl:
                        Trade.sl = NewStop
                if self.data.Signal[-1] == 0:
                    self.position.close()
            else:
                if self.data.Signal[-1] == 1 and RangePct <= VolatilityCap:
                    EntryPrice = self.data.Close[-1]
                    StopPrice = EntryPrice - AtrMultiplier * CurrentAtr
                    Size = self.equity / EntryPrice
                    self.buy(size=Size, sl=StopPrice)

    BacktestInstance = Backtest(TradingDataframe, TrailingStopStrategy, cash=InitialCash, commission=0.0)
    Output = BacktestInstance.run()
    return Output['Return [%]'], Output['Sharpe Ratio']
