from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


@dataclass
class AnalysisResult:
    summary: str
    data: Dict[str, Any]

class BaseAnalyzer(ABC):
    def __init__(self, symbol: str):
        self.symbol = symbol

    @abstractmethod
    def analyze(self) -> AnalysisResult:
        ...
