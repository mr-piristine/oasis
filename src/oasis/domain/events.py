# events.py

from dataclasses import dataclass
from datetime import datetime
from typing import List

from .models import Candle, HistoryResultSet


@dataclass(frozen=True)
class CandleEvent:
    candle: Candle


@dataclass(frozen=True)
class PageEvent:
    result_set: HistoryResultSet
    page_index: int
    candles: List[Candle]
    record_count: int


@dataclass(frozen=True)
class EvidenceEvent:
    file_path: str
    content_hash: str
    page_index: int
    record_count: int


@dataclass(frozen=True)
class DownloadCompletedEvent:
    result_set: HistoryResultSet
    total_bars: int
    pages: int
    completed_at: datetime