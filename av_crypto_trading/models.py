from sqlalchemy import TIMESTAMP, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .core import contants
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    profit_reports = relationship("ProfitReport", back_populates="owner")


class ProfitReport(Base):
    __tablename__ = "profit_reports"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    duration = Column(String)
    currency = Column(String, index=True)
    quantity = Column(Float, index=True)
    buy_order_time = Column(TIMESTAMP)
    buy_order_price = Column(Float, index=True)
    sell_order_time = Column(TIMESTAMP)
    sell_order_price = Column(Float, index=True)
    difference_currency = Column(Float, index=True)
    profit_usd = Column(Float, index=True)
    # ProfitPln = Column(Float, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="profit_reports")

    buy_order_id = Column(Integer, ForeignKey("transactions.id"))
    buy_orders = relationship("Transaction", back_populates="profit_report")
    sell_order_id = Column(Integer, ForeignKey("transactions.id"))
    sell_orders = relationship("Transaction", back_populates="profit_report")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    currency = Column(String)
    transaction_time = Column(TIMESTAMP)
    origin_quantity = Column(Float)
    executed_quantity = Column(Float)
    cumulative_quote_quantity = Column(Float)
    status = Column(String)
    type = Column(String)
    side = Column(String)
    price = Column(Float)
    quantity = Column(Float)
    commision = Column(Float)
    commision_asset = Column(String)
    trade_id = Column(Integer)

    # profit_report_id = Column(Integer, ForeignKey("profit_reports.id"))
    profit_report = relationship("Profit_Report", back_populates="transactions")


class Cryptocurrency(Base):
    """
    Streams documentation:
    https://binance-docs.github.io/apidocs/futures/en/#continuous-contract-kline-candlestick-streams
    Model create based on Individual Symbol Mini Ticker Stream response schema
    """

    __tablename__ = contants.Tables.cryptocurrencies

    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    timestamp = Column(TIMESTAMP)
    symbol = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    # adj_close = Column(Float)
    volume = Column(Float)
    quote = Column(Float)
    # ds = Timestamp
    # y = Close


class PositionCheck(Base):
    __tablename__ = contants.Tables.position_checks

    id = Column(Integer, primary_key=True)
    description = Column(String)
    currency = Column(String)
    position = Column(Boolean)
    quantity = Column(Float)
