from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

import dataclasses_json
from pydantic import BaseModel

from av_crypto_trading.core import contants


class ProfitReportBase(BaseModel):
    currency: str
    description: Union[str, None] = None
    duration: str
    quantity: float
    buy_order_time: datetime
    buy_order_price: float
    sell_order_time: datetime
    sell_order_price: float
    difference_currency: float
    profit_usd: float


class ProfitReportCreate(ProfitReportBase):
    pass


class ProfitReport(ProfitReportBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    id: int
    description: Union[str, None] = None
    currency: str
    transaction_time: datetime
    origin_quantity: float
    executed_quantity: float
    cumulative_quote_quantity: float
    status: str
    type: str
    side: str
    price: float
    quantity: float
    commision: float
    commision_asset: str
    trade_id: int


class Transaction(TransactionBase):
    id: int
    profit_report_id: int

    class Config:
        orm_mode = True


class CryptocurrencyBase(BaseModel):
    id: int
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    # adj_close: float
    volume: float
    quote: int


class Cryptocurrency(CryptocurrencyBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    first_name: str
    surname: str
    profit_reports: List[ProfitReport] = []

    class Config:
        orm_mode = True


class PositionCheckBase(BaseModel):
    description: str
    currency: str
    position: bool
    quantity: float


class PositionCheck(PositionCheckBase):
    id: int

    class Config:
        orm_mode = True


@dataclass
class ProfitReportDataclass(dataclasses_json.DataClassJsonMixin):
    currency: str #contants.Currencies
    quantity: float
    buy_order_time: str
    buy_order_price: float
    sell_order_time: str
    sell_order_price: float
    difference_currency: float
    profit_usd: float
    buy_order_id: int
    sell_order_id: int
