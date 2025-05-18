from typing import Callable, Optional
from backtesting import Strategy


class BaseTradingStrategy(Strategy):
    """Base Strategy accepting callbacks for trading logic."""

    EntryCallback: Optional[Callable] = None
    ExitCallback: Optional[Callable] = None
    StopCallback: Optional[Callable] = None
    InitCallback: Optional[Callable] = None

    def init(self) -> None:
        if self.InitCallback:
            # Call init callback bound to this instance
            self.InitCallback()

    def next(self) -> None:
        if self.StopCallback:
            self.StopCallback()
        if self.EntryCallback:
            self.EntryCallback()
        if self.ExitCallback:
            self.ExitCallback()
