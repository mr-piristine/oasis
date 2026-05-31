# pipeline/paginator.py

from typing import Iterator, List
from ..domain.models import Candle, HistoryResultSet
from ..domain.events import PageEvent


class PageAggregator:

    def __init__(self, page_size: int):
        self.page_size = page_size

    def aggregate(
        self,
        stream,
        base_result_set: HistoryResultSet
    ) -> Iterator[PageEvent]:

        buffer: List[Candle] = []
        page_index = 0

        for candle in stream:

            buffer.append(candle)

            if len(buffer) >= self.page_size:
                yield PageEvent(
                    result_set=base_result_set,
                    page_index=page_index,
                    candles=buffer,
                    record_count=len(buffer)
                )
                buffer = []
                page_index += 1

        # flush remainder
        if buffer:
            yield PageEvent(
                result_set=base_result_set,
                page_index=page_index,
                candles=buffer,
                record_count=len(buffer)
            )