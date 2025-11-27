from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class DerivativesSummary:
    funding_rate: Optional[float]
    oi: Optional[float]
    oi_change_24h: Optional[float]


class DerivativesAnalyzer(BaseAnalyzer):

    def __init__(
        self,
        symbol: str,
        funding_df: Optional[pd.DataFrame] = None,
        oi_df: Optional[pd.DataFrame] = None,
    ):
        super().__init__(symbol)
        self.funding_df = funding_df
        self.oi_df = oi_df

    def _last_funding(self) -> Optional[float]:
        if self.funding_df is None or self.funding_df.empty:
            return None
        df = self.funding_df.sort_values("time")
        return float(df["funding_rate"].iloc[-1])

    def _oi_info(self) -> tuple[Optional[float], Optional[float]]:
        if self.oi_df is None or len(self.oi_df) < 2:
            return None, None

        df = self.oi_df.sort_values("time")
        last = float(df["oi"].iloc[-1])
        first = float(df["oi"].iloc[0])

        if first <= 0:
            change_pct: Optional[float] = None
        else:
            change_pct = (last - first) / first * 100.0

        return last, change_pct

    def analyze(self) -> AnalysisResult:
        funding = self._last_funding()
        oi, oi_change = self._oi_info()

        parts = [f"Анализ деривативов по {self.symbol}:"]

        if funding is None:
            parts.append("- Funding rate: данных нет.")
        else:
            parts.append(f"- Funding rate (посл.): {funding:.4%}.")
            if funding > 0.0005:
                parts.append("  Высокий положительный funding — рынок перекошен в сторону лонгов, лонгерам дороже держать позицию.")
            elif funding < -0.0005:
                parts.append("  Сильно отрицательный funding — перекос в сторону шортов, шортерам дороже держать позицию.")
            else:
                parts.append("  Funding около нуля — сильного перекоса по сторонам нет.")

        if oi is None:
            parts.append("- Open interest: данных недостаточно.")
        else:
            line = f"- Open interest (посл.): {oi:,.0f} контрактов."
            if oi_change is not None:
                line += f" Изменение за период: {oi_change:.2f}%."
                if oi_change > 5:
                    line += " Рост OI — в рынок входит новый капитал, движение укрепляется."
                elif oi_change < -5:
                    line += " Снижение OI — часть позиций закрывается, движение может выдыхаться."
            parts.append(line)

        summary_text = "\n".join(parts)

        data: Dict[str, Any] = {
            "funding_rate": funding,
            "oi": oi,
            "oi_change_pct": oi_change,
        }

        return AnalysisResult(summary=summary_text, data=data)
