from enum import Enum, auto
from typing import List

# DATABASE_PATH = "sqlite:///../../AV_CRYPTO_TRADING.db"


class AutoNameEnum(Enum):
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: List[str]
    ) -> str:
        return name


class Currencies(Enum):
    Bitcoin = "BTCUSDT"
    Adva = "ADVUSDT"
    Ethereum = "ETHUSDT"
    Polygon = "MATICUSDT"
    BNB = "BNBUSDT"


class Decision(AutoNameEnum):
    BUY = auto()
    SELL = auto()


class Companies(Enum):
    Tesla = "TSLA"
    Google = "GOOG"
    Bitcoin = "BTC"


class Tables:
    cryptocurrencies = "cryptocurrencies"
    profit_reports = "profit_reports"
    transactions = "transactions"
    users = "users"
    sqlite_master = "sqlite_master"
    position_checks = "position_checks"
