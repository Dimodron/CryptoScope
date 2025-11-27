from analytic import (
    CandleAnalyzer,
    OrderBookAnalyzer,
    VolumeAnalyzer,
    DerivativesAnalyzer,
    CorrelationAnalyzer,
    ReportBuilder,
)
from .binance_api import BinanceApi


def build_candle_report(symbol: str, interval: str, candles_limit: int) -> str:
    api = BinanceApi(symbol, interval, candles_limit)
    candles = api.load_klines()

    analyzer = CandleAnalyzer(symbol, candles, interval)
    result = analyzer.analyze()
    return result.summary


def build_orderbook_report(symbol: str) -> str:
    api = BinanceApi(symbol)
    bids, asks = api.load_orderbook()

    analyzer = OrderBookAnalyzer(symbol, bids, asks)
    result = analyzer.analyze()
    return result.summary


def build_volume_report(symbol: str) -> str:
    api = BinanceApi(symbol)
    trades = api.load_trades()

    analyzer = VolumeAnalyzer(symbol, trades)
    result = analyzer.analyze()
    return result.summary


def build_derivatives_report(symbol: str) -> str:
    api = BinanceApi(symbol)
    funding = api.load_funding()
    oi = api.load_oi()

    analyzer = DerivativesAnalyzer(symbol, funding_df=funding, oi_df=oi)
    result = analyzer.analyze()
    return result.summary


def build_correlation_report(symbol: str, interval: str, candles_limit: int) -> str:
    api_main = BinanceApi(symbol, interval, candles_limit)
    candles = api_main.load_klines()

    btc_df = BinanceApi("BTCUSDT", interval, candles_limit).load_klines()
    eth_df = BinanceApi("ETHUSDT", interval, candles_limit).load_klines()

    analyzer = CorrelationAnalyzer(
        symbol,
        candles,
        {"BTCUSDT": btc_df, "ETHUSDT": eth_df},
        window=candles_limit,
        interval=interval,
    )
    result = analyzer.analyze()
    return result.summary


def build_full_report(symbol: str, interval: str, candles_limit: int) -> str:
    api_main = BinanceApi(symbol, interval, candles_limit)
    candles = api_main.load_klines()

    bids, asks = api_main.load_orderbook()
    trades = api_main.load_trades()
    funding = api_main.load_funding()
    oi = api_main.load_oi()

    btc_df = BinanceApi("BTCUSDT", interval, candles_limit).load_klines()
    eth_df = BinanceApi("ETHUSDT", interval, candles_limit).load_klines()

    candle_analyzer = CandleAnalyzer(symbol, candles, interval)
    orderbook_analyzer = OrderBookAnalyzer(symbol, bids, asks)
    volume_analyzer = VolumeAnalyzer(symbol, trades)
    derivatives_analyzer = DerivativesAnalyzer(symbol, funding_df=funding, oi_df=oi)
    corr_analyzer = CorrelationAnalyzer(
        symbol,
        candles,
        {"BTCUSDT": btc_df, "ETHUSDT": eth_df},
        window=candles_limit,
        interval=interval,
    )

    builder = ReportBuilder(symbol)
    builder.add_candle_analysis(candle_analyzer)
    builder.add_orderbook_analysis(orderbook_analyzer)
    builder.add_volume_analysis(volume_analyzer)
    builder.add_derivatives_analysis(derivatives_analyzer)
    builder.add_correlation_analysis(corr_analyzer)

    return builder.build_text_report()
