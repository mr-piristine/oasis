# domain/models.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class Interval(Enum):
    M1 = "1"
    M3 = "3"
    M5 = "5"
    M15 = "15"
    M30 = "30"
    M45 = "45"

    H1 = "60"
    H2 = "120"
    H3 = "180"
    H4 = "240"

    D1 = "1D"
    W1 = "1W"
    MN1 = "1M"

    @classmethod
    def from_str(cls, value: str) -> "Interval":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unsupported interval: {value}")


@dataclass(frozen=True)
class Asset:
    symbol: str
    exchange: str

    @property
    def tv_ticker(self) -> str:
        return f"{self.exchange.upper()}:{self.symbol.upper()}"


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class HistoryResultSet:
    asset: Asset
    interval: Interval
    candles: List[Candle] = field(default_factory=list)

    source: str = "TradingView"

    # acquisition metadata (important for evidence lineage)
    requested_bars: int = 0
    retrieved_bars: int = 0
    acquired_at: datetime | None = None

    @property
    def symbol(self) -> str:
        return self.asset.symbol

    @property
    def venue(self) -> str:
        return self.asset.exchange

    @property
    def time_period(self) -> str:
        return self.interval.name