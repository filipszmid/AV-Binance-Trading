from enum import Enum, auto
from typing import List


class AutoNameEnum(Enum):
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[str]
    ) -> str:
        return name


class Currencies:
    Bitcoin = "BTCUSDT"
    Adva = "ADVUSDT"


class Decision(AutoNameEnum):
    BUY = auto()
    SELL = auto()


class Companies:
    Tesla = "TSLA"
    Google = "GOOG"
    Bitcoin = "BTC"
