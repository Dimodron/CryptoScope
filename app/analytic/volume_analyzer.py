from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class VolumeFlowSummary:
    buy_volume: float
    sell_volume: float
    delta: float
    delta_pct: float


class VolumeAnalyzer(BaseAnalyzer):
    def __init__(self, symbol: str, trades: pd.DataFrame):
        super().__init__(symbol)
        self.trades = trades.copy()

    def _calc(self, lookback: int = 1000) -> VolumeFlowSummary:
        df = self.trades.tail(lookback)

        buy_vol = float(df.loc[df["side"] == "buy", "qty"].sum())
        sell_vol = float(df.loc[df["side"] == "sell", "qty"].sum())
        delta = buy_vol - sell_vol
        total = buy_vol + sell_vol
        delta_pct = (delta / total * 100) if total > 0 else 0.0

        return VolumeFlowSummary(
            buy_volume=buy_vol,
            sell_volume=sell_vol,
            delta=delta,
            delta_pct=delta_pct,
        )

    def analyze(self) -> AnalysisResult:
        s = self._calc(lookback=1000)
        if s.delta > 0:
            side = "покупателей"
        elif s.delta < 0:
            side = "продавцов"
        else:
            side = "баланс"

        text = (
            f"Поток объёма по {self.symbol} (последние сделки):\n"
            f"- Объём покупок: {s.buy_volume:.2f}\n"
            f"- Объём продаж: {s.sell_volume:.2f}\n"
            f"- Дельта: {s.delta:.2f} ({s.delta_pct:.2f}%) — перевес у {side}."
        )

        data: Dict[str, Any] = {
            "buy_volume": s.buy_volume,
            "sell_volume": s.sell_volume,
            "delta": s.delta,
            "delta_pct": s.delta_pct,
        }

        return AnalysisResult(summary=text, data=data)
