from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd

from .base import BaseAnalyzer, AnalysisResult


@dataclass
class TechnicalLevels:
    support: float
    resistance: float
    recent_low: float
    recent_high: float


@dataclass
class TrendInfo:
    trend: str       
    description: str


@dataclass
class VolatilityInfo:
    atr: float
    atr_pct: float
    description: str


class CandleAnalyzer(BaseAnalyzer):
    def __init__(self, symbol: str, df: pd.DataFrame, interval: str):
        super().__init__(symbol)
        self.df = df.copy()
        self.interval = interval
        self._ensure_sorted()
        self._add_indicators()

    def _ensure_sorted(self) -> None:
        self.df = self.df.sort_index()

    def _add_indicators(self) -> None:
        close = self.df["close"]

        self.df["ma20"] = close.rolling(window=20).mean()
        self.df["ma50"] = close.rolling(window=50).mean()
        self.df["ma200"] = close.rolling(window=200).mean()

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df["rsi14"] = 100 - (100 / (1 + rs))

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        self.df["macd"] = ema12 - ema26
        self.df["macd_signal"] = self.df["macd"].ewm(span=9, adjust=False).mean()
        self.df["macd_hist"] = self.df["macd"] - self.df["macd_signal"]

        high = self.df["high"]
        low = self.df["low"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.df["atr14"] = tr.rolling(window=14).mean()

    def get_levels(self, lookback: int = 50) -> Optional[TechnicalLevels]:
        if len(self.df) < lookback:
            return None

        recent = self.df.iloc[-lookback:]
        support = recent["low"].min()
        resistance = recent["high"].max()
        recent_low = recent["low"].iloc[-1]
        recent_high = recent["high"].iloc[-1]

        return TechnicalLevels(
            support=float(support),
            resistance=float(resistance),
            recent_low=float(recent_low),
            recent_high=float(recent_high),
        )

    def get_trend(self) -> TrendInfo:
        last = self.df.iloc[-1]
        close = last["close"]
        ma50 = last["ma50"]
        ma200 = last["ma200"]

        if pd.isna(ma50) or pd.isna(ma200):
            return TrendInfo(
                trend="unknown",
                description="Недостаточно данных для оценки долгосрочного тренда (MA50/MA200).",
            )

        if close > ma50 > ma200:
            trend = "bullish"
            desc = (
                "Цена выше MA50, а MA50 выше MA200 — преобладает среднесрочный бычий тренд."
            )
        elif close < ma50 < ma200:
            trend = "bearish"
            desc = (
                "Цена ниже MA50, а MA50 ниже MA200 — преобладает среднесрочный медвежий тренд."
            )
        else:
            trend = "sideways"
            desc = (
                "Цена и скользящие средние переплетены — вероятен боковик или фаза смены тренда."
            )

        return TrendInfo(trend=trend, description=desc)

    def get_volatility(self) -> VolatilityInfo:
        last = self.df.iloc[-1]
        close = last["close"]
        atr = last["atr14"]

        if pd.isna(atr):
            return VolatilityInfo(
                atr=float("nan"),
                atr_pct=float("nan"),
                description="Недостаточно данных для оценки волатильности (ATR14).",
            )

        atr_pct = atr / close * 100

        if atr_pct < 1:
            desc = "Волатильность низкая, движение цены относительно спокойное."
        elif atr_pct < 3:
            desc = "Волатильность умеренная, движение в нормальных пределах."
        else:
            desc = "Волатильность высокая, движение резкое — повышенные риски."

        return VolatilityInfo(atr=float(atr), atr_pct=float(atr_pct), description=desc)

    def _interpret_rsi(self, rsi: float) -> str:
        if np.isnan(rsi):
            return "RSI: недостаточно данных."
        if rsi > 70:
            return f"RSI ~ {rsi:.1f} — зона перекупленности, риск отката повышен."
        elif rsi < 30:
            return f"RSI ~ {rsi:.1f} — зона перепроданности, возможен отскок."
        else:
            return f"RSI ~ {rsi:.1f} — нейтральная зона, явного перекупа/перепроданности нет."

    def _interpret_macd(self, macd: float, signal: float, hist: float) -> str:
        if any(np.isnan(x) for x in [macd, signal, hist]):
            return "MACD: недостаточно данных."

        if hist > 0 and macd > signal:
            return "MACD выше сигнальной линии, гистограмма положительная — бычий импульс."
        elif hist < 0 and macd < signal:
            return "MACD ниже сигнальной линии, гистограмма отрицательная — медвежий импульс."
        else:
            return "MACD около сигнальной линии — явного импульса нет, возможна консолидация."

    def analyze(self) -> AnalysisResult:
        if self.df.empty:
            return AnalysisResult(
                summary=f"Аналитика по {self.symbol}: данных нет.",
                data={},
            )

        last = self.df.iloc[-1]
        start_time = self.df.index[0]
        end_time = self.df.index[-1]
        candles_count = len(self.df)

        trend_info = self.get_trend()
        vol_info = self.get_volatility()
        levels = self.get_levels(lookback=50)

        close = last["close"]
        ma20 = last["ma20"]
        ma50 = last["ma50"]
        ma200 = last["ma200"]
        rsi = last["rsi14"]
        macd = last["macd"]
        macd_signal = last["macd_signal"]
        macd_hist = last["macd_hist"]

        rsi_text = self._interpret_rsi(rsi)
        macd_text = self._interpret_macd(macd, macd_signal, macd_hist)

        if levels is not None:
            levels_text = (
                f"Поддержка ~{levels.support:.2f}, сопротивление ~{levels.resistance:.2f}."
            )
        else:
            levels_text = "Недостаточно данных для уверенного определения уровней."

        header = (
            f"Аналитика по {self.symbol} (TF {self.interval}, свечей: {candles_count})\n"
            f"Период: {start_time.strftime('%Y-%m-%d %H:%M')} → "
            f"{end_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        )

        body = f"""
- Цена закрытия: {close:.2f} USDT
- {trend_info.description}
- MA20: {ma20:.2f}, MA50: {ma50:.2f}, MA200: {ma200:.2f}
- {rsi_text}
- {macd_text}
- Уровни: {levels_text}
- Волатильность (ATR14): {vol_info.atr:.3f} (~{vol_info.atr_pct:.2f}% от цены). {vol_info.description}
""".strip()

        summary = header + body

        data: Dict[str, Any] = {
            "period_start": start_time,
            "period_end": end_time,
            "candles_count": candles_count,
            "close": float(close),
            "ma20": float(ma20) if not np.isnan(ma20) else None,
            "ma50": float(ma50) if not np.isnan(ma50) else None,
            "ma200": float(ma200) if not np.isnan(ma200) else None,
            "rsi14": float(rsi) if not np.isnan(rsi) else None,
            "macd": float(macd) if not np.isnan(macd) else None,
            "macd_signal": float(macd_signal) if not np.isnan(macd_signal) else None,
            "macd_hist": float(macd_hist) if not np.isnan(macd_hist) else None,
            "trend": trend_info.trend,
            "volatility_atr": vol_info.atr,
            "volatility_atr_pct": vol_info.atr_pct,
            "levels": levels,
            "interval": self.interval,
        }

        return AnalysisResult(summary=summary, data=data)
