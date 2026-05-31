# provider/tradingview_provider.py

from typing import Iterator, Union
from datetime import datetime
import websocket, ssl, time

from ..models import Asset, Interval, Candle
from ..protocol import TVProtocol
from ..session import TVSession


class TradingViewStreamProvider:

    WS_URL = "wss://data.tradingview.com/socket.io/websocket"

    def __init__(self, session: TVSession | None = None):
        self.session = session or TVSession()

    def stream(
        self,
        asset: Asset,
        interval: Union[str, Interval],
        bars: int
    ) -> Iterator[Candle]:

        if isinstance(interval, str):
            interval = Interval.from_str(interval)

        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})

        cookie = "; ".join(f"{k}={v}" for k, v in self.session.cookies.items())

        ws.connect(
            self.WS_URL,
            header=[f"User-Agent: {self.session.headers['User-Agent']}"],
            cookie=cookie
        )

        ws.settimeout(2.0)

        session_id = TVSession.generate_random_string()

        symbol_id = "sds_sym_1"
        series_id = "sds_ser_1"

        try:
            _ = ws.recv()

            ws.send(TVProtocol.create_auth_packet())
            ws.send(TVProtocol.create_session_packet(session_id))
            ws.send(TVProtocol.create_resolve_packet(session_id, symbol_id, asset.tv_ticker))
            ws.send(TVProtocol.create_series_packet(session_id, symbol_id, series_id, interval.value, bars))

            start = time.time()
            collected = 0

            while time.time() - start < 12 and collected < bars:
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    continue

                if "~h~" in raw:
                    ws.send(raw)
                    continue

                for msg in TVProtocol.decode(raw):
                    params = msg.get("p", [])
                    for p in params:
                        if isinstance(p, dict):
                            target = p.get(series_id, p)

                            if isinstance(target, dict) and "s" in target:
                                for pt in target["s"]:
                                    v = pt.get("v")
                                    if isinstance(v, list) and len(v) >= 6:
                                        try:
                                            yield Candle(
                                                timestamp=datetime.fromtimestamp(int(v[0])),
                                                open=float(v[1]),
                                                high=float(v[2]),
                                                low=float(v[3]),
                                                close=float(v[4]),
                                                volume=float(v[5])
                                            )
                                            collected += 1
                                        except Exception:
                                            pass
        finally:
            ws.close()