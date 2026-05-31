# pipeline/download_orchestrator.py

from datetime import datetime

from ..domain.models import HistoryResultSet
from ..provider.tradingview.provider import TradingViewStreamProvider
from .paginator import PageAggregator
from ..evidence.publisher import EvidencePublisher
from ..domain.events import DownloadCompletedEvent


class DownloadOrchestrator:

    def __init__(self, page_size: int, evidence_dir: str):
        self.provider = TradingViewStreamProvider()
        self.aggregator = PageAggregator(page_size)
        self.publisher = EvidencePublisher(evidence_dir)

    def run(self, asset, interval, bars: int):

        base = HistoryResultSet(
            asset=asset,
            interval=interval,
            candles=[]
        )

        stream = self.provider.stream(asset, interval, bars)

        pages = 0
        total = 0

        for page_event in self.aggregator.aggregate(stream, base):

            evidence = self.publisher.publish(page_event)

            pages += 1
            total += page_event.record_count

            # optional: emit event bus here
            # event_bus.publish(evidence)

        return DownloadCompletedEvent(
            result_set=base,
            total_bars=total,
            pages=pages,
            completed_at=datetime.utcnow()
        )