from __future__ import annotations

from typing import Dict, Any

import pandas as pd
import numpy as np

from .base import BaseAnalyzer, AnalysisResult


class CorrelationAnalyzer(BaseAnalyzer):

    def __init__(
        self,
        symbol: str,
        main_df: pd.DataFrame,
        bench_dfs: Dict[str, pd.DataFrame],
        window: int = 100,
        interval: str = "1h",
    ):
        super().__init__(symbol)
        self.main_df = main_df.copy()
        self.bench_dfs = bench_dfs
        self.window = window
        self.interval = interval

        self.main_df = self.main_df.sort_index()
        for k in list(self.bench_dfs.keys()):
            self.bench_dfs[k] = self.bench_dfs[k].sort_index()

    def analyze(self) -> AnalysisResult:
        if self.main_df.empty:
            return AnalysisResult(
                summary=f"Корреляции по {self.symbol}: данных нет.",
                data={},
            )

        if "close" not in self.main_df.columns:
            raise ValueError("main_df должен содержать колонку 'close'")

        main_close = self.main_df["close"].rename(self.symbol)

        effective_window = min(self.window, len(self.main_df))
        if effective_window < 2:
            return AnalysisResult(
                summary=f"Корреляции по {self.symbol}: недостаточно данных.",
                data={},
            )

        period_start = self.main_df.index[-effective_window]
        period_end = self.main_df.index[-1]

        lines = [
            f"Корреляции {self.symbol} с бенчмарками "
            f"(последние {effective_window} свечей, TF {self.interval})",
            f"Период: {period_start.strftime('%Y-%m-%d %H:%M')} → "
            f"{period_end.strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        corr_data: Dict[str, float] = {}

        for name, df in self.bench_dfs.items():
            if "close" not in df.columns:
                lines.append(f"- {name}: нет колонки 'close', пропускаю.")
                continue

            aligned = pd.concat(
                [main_close, df["close"].rename(name)],
                axis=1,
                join="inner",
            ).dropna()

            if len(aligned) < 2:
                lines.append(f"- {name}: недостаточно общих данных.")
                continue

            sub = aligned.iloc[-effective_window:]

            main_ret = sub[self.symbol].pct_change()
            bench_ret = sub[name].pct_change()

            if main_ret.isna().all() or bench_ret.isna().all():
                lines.append(f"- {name}: невозможно посчитать корреляцию (NaN).")
                continue

            corr = float(main_ret.corr(bench_ret))
            corr_data[name] = corr

            if corr >= 0.75:
                comment = "очень высокая положительная корреляция"
            elif corr >= 0.5:
                comment = "устойчивая положительная корреляция"
            elif corr >= 0.25:
                comment = "умеренная положительная корреляция"
            elif corr > -0.25:
                comment = "слабая или отсутствующая корреляция"
            elif corr > -0.5:
                comment = "умеренная отрицательная корреляция"
            else:
                comment = "сильная отрицательная корреляция"

            lines.append(f"- {name}: корреляция {corr:.2f} ({comment})")

        if not corr_data:
            lines.append("")
            lines.append("Недостаточно данных для расчёта корреляций.")

        summary = "\n".join(lines)

        return AnalysisResult(summary=summary, data=corr_data)
