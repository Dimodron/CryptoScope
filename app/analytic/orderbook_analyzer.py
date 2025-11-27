from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class OrderBookSummary:
    bid_liquidity: float
    ask_liquidity: float
    imbalance: float
    top_bid: float
    top_ask: float


class OrderBookAnalyzer(BaseAnalyzer):
    def __init__(self, symbol: str, bids: pd.DataFrame, asks: pd.DataFrame):
        super().__init__(symbol)
        self.bids = bids.copy()
        self.asks = asks.copy()

        self.bids.sort_values("price", ascending=False, inplace=True)
        self.asks.sort_values("price", ascending=True, inplace=True)

    def _summarize(self, depth: int = 20) -> OrderBookSummary:
        bids_slice = self.bids.head(depth)
        asks_slice = self.asks.head(depth)

        bid_liq = float((bids_slice["price"] * bids_slice["qty"]).sum())
        ask_liq = float((asks_slice["price"] * asks_slice["qty"]).sum())

        denom = bid_liq + ask_liq
        if denom == 0:
            imbalance = 0.0
        else:
            imbalance = (bid_liq - ask_liq) / denom

        top_bid = float(bids_slice["price"].iloc[0]) if not bids_slice.empty else float("nan")
        top_ask = float(asks_slice["price"].iloc[0]) if not asks_slice.empty else float("nan")

        return OrderBookSummary(
            bid_liquidity=bid_liq,
            ask_liquidity=ask_liq,
            imbalance=imbalance,
            top_bid=top_bid,
            top_ask=top_ask,
        )

    def analyze(self) -> AnalysisResult:
        summary_struct = self._summarize(depth=20)
        imb = summary_struct.imbalance

        if np.isnan(summary_struct.top_bid) or np.isnan(summary_struct.top_ask):
            text = f"Стакан по {self.symbol}: недостаточно данных."
        else:
            side = (
                "покупателей (bid)"
                if imb > 0.1
                else "продавцов (ask)"
                if imb < -0.1
                else "балансирован"
            )
            text = (
                f"Стакан по {self.symbol}:\n"
                f"- Лучший бид: {summary_struct.top_bid:.4f}\n"
                f"- Лучший аск: {summary_struct.top_ask:.4f}\n"
                f"- Ликвидность BID (top20): {summary_struct.bid_liquidity:,.0f}\n"
                f"- Ликвидность ASK (top20): {summary_struct.ask_liquidity:,.0f}\n"
                f"- Дисбаланс: {imb:.2%} — преимущество у {side}."
            )

        data: Dict[str, Any] = {
            "bid_liquidity": summary_struct.bid_liquidity,
            "ask_liquidity": summary_struct.ask_liquidity,
            "imbalance": summary_struct.imbalance,
            "top_bid": summary_struct.top_bid,
            "top_ask": summary_struct.top_ask,
        }

        return AnalysisResult(summary=text, data=data)
