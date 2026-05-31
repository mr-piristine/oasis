# provider/tradingview_provider.py

import ssl
import time
import websocket
from datetime import datetime
from typing import List, Union

from ...domain.models import Asset, Interval, Candle, HistoryResultSet
from .session import TVSession
from .protocol import TVProtocol


class TradingViewHistoryProvider:

    WS_URL = "wss://data.tradingview.com/socket.io/websocket"

    def __init__(self, session: TVSession | None = None):
        self.session = session or TVSession()

    def fetch(
        self,
        asset: Asset,
        interval: Union[Interval, str],
        bars: int = 100
    ) -> HistoryResultSet:

        if isinstance(interval, str):
            interval = Interval.from_str(interval)

        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})

        headers = {
            "User-Agent": self.session.headers["User-Agent"],
            "Origin": "https://www.tradingview.com"
        }

        cookie = "; ".join(
            f"{k}={v}" for k, v in self.session.cookies.items()
        ) if self.session.cookies else None

        ws.connect(
            self.WS_URL,
            header=[f"{k}: {v}" for k, v in headers.items()],
            cookie=cookie
        )

        ws.settimeout(2.0)

        chart_session = TVSession.generate_random_string()
        symbol_id = "sds_sym_1"
        series_id = "sds_ser_1"

        candles: List[Candle] = []

        try:
            _ = ws.recv()

            ws.send(TVProtocol.create_auth_packet())
            ws.send(TVProtocol.create_session_packet(chart_session))
            ws.send(TVProtocol.create_resolve_packet(chart_session, symbol_id, asset.tv_ticker))
            ws.send(TVProtocol.create_series_packet(chart_session, symbol_id, series_id, interval.value, bars))

            start = time.time()

            while time.time() - start < 12:
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    continue

                if "~h~" in raw:
                    ws.send(raw)
                    continue

                messages = TVProtocol.decode(raw)

                for msg in messages:
                    if not isinstance(msg, dict):
                        continue

                    params = msg.get("p", [])
                    if not isinstance(params, list):
                        continue

                    for p in params:
                        if isinstance(p, dict):
                            target = p.get(series_id, p)

                            if isinstance(target, dict) and "s" in target:
                                for pt in target["s"]:
                                    v = pt.get("v") if isinstance(pt, dict) else None
                                    if isinstance(v, list) and len(v) >= 6:
                                        try:
                                            candles.append(
                                                Candle(
                                                    timestamp=datetime.fromtimestamp(int(v[0])),
                                                    open=float(v[1]),
                                                    high=float(v[2]),
                                                    low=float(v[3]),
                                                    close=float(v[4]),
                                                    volume=float(v[5])
                                                )
                                            )
                                        except Exception:
                                            pass

            ws.close()

        finally:
            ws.close()

        # deduplicate
        seen = set()
        unique = []
        for c in candles:
            if c.timestamp not in seen:
                seen.add(c.timestamp)
                unique.append(c)

        unique.sort(key=lambda x: x.timestamp)

        return HistoryResultSet(
            asset=asset,
            interval=interval,
            candles=unique,
            requested_bars=bars,
            retrieved_bars=len(unique),
            acquired_at=datetime.utcnow()
        )