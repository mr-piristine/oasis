# evidence/partitioner.py

from typing import Iterator
from ..domain.models import HistoryResultSet, Candle


class HistoryPartitioner:

    @staticmethod
    def split(result_set: HistoryResultSet, page_size: int) -> Iterator[HistoryResultSet]:

        candles = result_set.candles
        total = len(candles)

        for i in range(0, total, page_size):
            chunk = candles[i:i + page_size]

            yield HistoryResultSet(
                asset=result_set.asset,
                interval=result_set.interval,
                candles=chunk,
                source=result_set.source,
                requested_bars=result_set.requested_bars,
                retrieved_bars=total,
                acquired_at=result_set.acquired_at
            )