# evidence/json_adapter.py

import json
import time
from pathlib import Path
from datetime import datetime

from ..domain.models import HistoryResultSet
from ..integrity.hasher import EvidenceHasher


class JSONEvidenceAdapter:

    @staticmethod
    def to_json_evidence(result_set: HistoryResultSet, directory: str, download_params=None) -> str:

        download_params = download_params or {}

        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        row_hashes = []
        data = []

        for c in result_set.candles:
            ts = c.timestamp.isoformat()

            h = EvidenceHasher.generate_row_hash(
                ts, c.open, c.high, c.low, c.close, c.volume
            )

            row_hashes.append(h)

            data.append({
                "datetime": ts,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "row_hash": h
            })

        meta = {
            "symbol": result_set.symbol,
            "venue": result_set.venue,
            "time_period": result_set.time_period,
            "source": result_set.source
        }

        payload_base = {
            "metadata": meta,
            "download_parameters": download_params,
            "row_hashes": row_hashes
        }

        content_hash = EvidenceHasher.generate_content_hash(
            json.dumps(payload_base, sort_keys=True)
        )

        final = {
            "integrity": {
                "content_hash": content_hash
            },
            "metadata": {
                **meta,
                "exported_at": datetime.utcnow().isoformat()
            },
            "download_parameters": download_params,
            "data": data
        }

        filename = f"{result_set.symbol}_{result_set.interval.name}_{int(time.time())}.json".lower()
        file_path = path / filename

        file_path.write_text(json.dumps(final, indent=2), encoding="utf-8")

        return str(file_path)