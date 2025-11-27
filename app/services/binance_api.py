
from typing import Literal, Tuple
import requests
import pandas as pd
from os import environ

class BinanceApi():

    def __init__(self, symbol:str, interval: str = "1h", limit: int = 500):
        self.interval = interval
        self.symbol = symbol
        self.limit = limit
        self.binanc_api = environ.get('BINANCE_API')
        self.binanc_fapi= environ.get('BINANCE_FAPI')

    def load_klines(self) -> pd.DataFrame:
        url = f'{self.binanc_api}/klines?symbol={self.symbol}&interval={self.interval}&limit={self.limit}'
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ])

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["time"] = pd.to_datetime(df["open_time"], unit="ms")

        df = df[["time", "open", "high", "low", "close", "volume"]]
        df.set_index("time", inplace=True)
        return df

    def load_orderbook(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        url = f'{self.binanc_api}/depth?symbol={self.symbol}&limit={self.limit}'
        resp = requests.get(url)
        data = resp.json()

        bids = pd.DataFrame(data["bids"], columns=["price", "qty"])
        asks = pd.DataFrame(data["asks"], columns=["price", "qty"])

        bids["price"] = bids["price"].astype(float)
        bids["qty"] = bids["qty"].astype(float)

        asks["price"] = asks["price"].astype(float)
        asks["qty"] = asks["qty"].astype(float)

        return bids, asks

    def load_trades(self):
        url = f'{self.binanc_api}/aggTrades?symbol={self.symbol}&limit={self.limit}'
        data = requests.get(url).json()

        df = pd.DataFrame(data)
        df.rename(columns={"q": "qty", "p": "price", "m": "is_sell"}, inplace=True)

        df["price"] = df["price"].astype(float)
        df["qty"] = df["qty"].astype(float)

        df["side"] = df["is_sell"].map(lambda x: "sell" if x else "buy")

        return df

    def load_funding(self)-> pd.DataFrame:
        url = f'{self.binanc_fapi}/fundingRate?symbol={self.symbol}&limit={self.limit}'
        df = pd.DataFrame(requests.get(url).json())
        df["funding_rate"] = df["fundingRate"].astype(float)
        df["time"] = pd.to_datetime(df["fundingTime"], unit="ms")
        return df[["time", "funding_rate"]]

    def load_oi(self)->pd.DataFrame:
        url = f"{self.binanc_fapi}/openInterest?symbol={self.symbol}"
        data = requests.get(url).json()
        df = pd.DataFrame([data])
        df["oi"] = df["openInterest"].astype(float)
        df["time"] = pd.Timestamp.utcnow()
        return df[["time", "oi"]]
