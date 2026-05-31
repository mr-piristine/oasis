from oasis.domain.models import Asset, Interval
from oasis.provider.tradingview.session import TVSession
from oasis.pipeline.orchestrator import DownloadOrchestrator

if __name__ == "__main__":
    #
    session =  TVSession(None, None)
    period_d1 = Interval.D1
    gold = Asset("XAUUSD","OANDA")
    max_bars = 100
    # tv =  TradingViewHistoryProvider(session=session)
    # hrs= tv.fetch( gold, period_d1, bars=max_bars)
    #
    # print(hrs.source)
    # print(hrs.requested_bars, hrs.retrieved_bars)
    # print(hrs.asset)
    # print(hrs.interval)
    # print(hrs.candles)

    orc = DownloadOrchestrator(page_size=100,evidence_dir="C:/acme/oasis/demo/evidence")
    result = orc.run(asset=gold, interval=Interval.D1,bars=max_bars)
    print(result)
    