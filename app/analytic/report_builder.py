from typing import List, Dict, Any, Optional

from .base import AnalysisResult
from .candle_analyzer import CandleAnalyzer
from .orderbook_analyzer import OrderBookAnalyzer
from .volume_analyzer import VolumeAnalyzer
from .derivatives_analyzer import DerivativesAnalyzer
from .correlation_analyzer import CorrelationAnalyzer


class ReportBuilder:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._sections: List[AnalysisResult] = []

    def add_candle_analysis(self, analyzer: CandleAnalyzer) -> "ReportBuilder":
        self._sections.append(analyzer.analyze())
        return self

    def add_orderbook_analysis(self, analyzer: OrderBookAnalyzer) -> "ReportBuilder":
        self._sections.append(analyzer.analyze())
        return self

    def add_volume_analysis(self, analyzer: VolumeAnalyzer) -> "ReportBuilder":
        self._sections.append(analyzer.analyze())
        return self

    def add_derivatives_analysis(self, analyzer: DerivativesAnalyzer) -> "ReportBuilder":
        self._sections.append(analyzer.analyze())
        return self

    def add_correlation_analysis(self, analyzer: CorrelationAnalyzer) -> "ReportBuilder":
        self._sections.append(analyzer.analyze())
        return self

    def build_text_report(self) -> str:
        parts = [f"Сводный отчёт по {self.symbol}:"]
        for section in self._sections:
            parts.append("")
            parts.append(section.summary)
        parts.append("")
        parts.append("⚠️ Всё выше — не инвестиционная рекомендация, а технический обзор.")
        return "\n".join(parts)

    def build_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"symbol": self.symbol, "sections": []}
        for section in self._sections:
            result["sections"].append(
                {
                    "summary": section.summary,
                    "data": section.data,
                }
            )
        return result
