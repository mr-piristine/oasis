# pipeline/evidence_publisher.py

from pathlib import Path
import json
import time

from ..integrity.hasher import EvidenceHasher
from ..domain.events import PageEvent, EvidenceEvent
# from ..domain.models import HistoryResultSet
from .json_adapter import JSONEvidenceAdapter


class EvidencePublisher:

    def __init__(self, directory: str):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def publish(self, event: PageEvent) -> EvidenceEvent:

        file_path = JSONEvidenceAdapter.to_json_evidence(
            result_set=event.result_set.__class__(
                asset=event.result_set.asset,
                interval=event.result_set.interval,
                candles=event.candles,
                source=event.result_set.source
            ),
            directory=str(self.dir),
            download_params={
                "page_index": event.page_index,
                "record_count": event.record_count
            }
        )

        content_hash = EvidenceHasher.generate_content_hash(file_path)

        return EvidenceEvent(
            file_path=file_path,
            content_hash=content_hash,
            page_index=event.page_index,
            record_count=event.record_count
        )