import datetime as dt
import os
from sqlite3 import Timestamp

import pandas as pd

from av_crypto_trading import database, schemas
from av_crypto_trading.core import contants

# engine = create_engine(contants.DATABASE_PATH)
def fix_paths():
    """
    There are problems with working dirs, when invoking function from other place,
    Working dir is set to function working dir.
    This fix_paths set the current working directory to current file directory.
    """

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


class WrongOrderDecisionException(Exception):
    """Error raise when wrong decision is provided."""


def save_dict_to_db(data: dict, table: contants.Tables) -> int:
    """Saves a dict to database and returns its id."""
    conn = database.engine.connect()
    transaction = conn.begin()
    df = pd.DataFrame.from_dict([data])
    df.to_sql(table, conn, index=False, if_exists="append")
    result = conn.execute(f"SELECT max(id) FROM {table}")
    transaction.commit()
    return result.one()[0]


def save_df_to_db(df: pd.DataFrame, table: contants.Tables) -> int:
    """Saves a pd.DataFrame to database and returns its id."""
    conn = database.engine.connect()
    transaction = conn.begin()
    df.to_sql(table, database.engine, index=False, if_exists="append")
    result = conn.execute(f"SELECT max(id) FROM {table}")
    transaction.commit()
    return result.one()[0]


def reloads_position_checks() -> None:
    """
    Drops position_checks data and loads position checks seed from file.

    # reloads_position_checks()
    # read_position_checks()
    # set_position("BTCUSDT", 0.001)
    # read_position_checks()
    """
    with database.engine.connect() as conn:
        transaction = conn.begin()
        conn.execute(f"DELETE FROM {contants.Tables.position_checks}")
        transaction.commit()

    with database.engine.connect() as conn:
        transaction = conn.begin()
        df = pd.read_csv("../../tests/test_data_position_checks_basic.csv")
        df.position = df.position.astype(int)
        df.quantity = df.quantity.astype(float)
        df.to_sql(
            contants.Tables.position_checks, conn, index=False, if_exists="append"
        )
        transaction.commit()

# TODO: during api run up load position checks to db
# fix_paths()
# reloads_position_checks()


def read_position_checks() -> pd.DataFrame:
    """Returns position checks values for all trading currencies."""
    df = pd.read_sql(
        f"""SELECT * FROM {contants.Tables.position_checks}""",
        database.engine,
    )
    print(df)
    return df


def update_position(
    currency: str, position: int, quantity: float
) -> None:
    """Update the position and quantity invested while trading."""
    with database.engine.connect() as con:
        con.execute(
            f"""
                    UPDATE 
                      {contants.Tables.position_checks} 
                    SET 
                      position = position + {position}, 
                      quantity = quantity + {quantity} 
                    WHERE 
                      currency = '{currency}'
                    """
        )


def change_position(
    currency: str, order: dict, decision: contants.Decision
):
    """Updates positions data in positions_check table."""
    if decision.value is contants.Decision.BUY.value:
        update_position(currency, 1, order["executed_quantity"])
    elif decision.value is contants.Decision.SELL.value:
        update_position(currency, -1, -order["executed_quantity"])
    else:
        raise WrongOrderDecisionException("Decision should be BUY or SELL.")


def get_profit_report(
    buy_order: dict, sell_order: dict, currency: str, quantity: float
) -> schemas.ProfitReportDataclass:
    """Returns profit report based on buy and sell orders, prints necessary information."""

    buy_price = float(buy_order["price"]) * 1.075  # 7.5 % to broker
    sell_price = float(sell_order["price"]) * 0.925

    difference = (sell_order["price"] - buy_order["price"]) / buy_order["price"]
    profit_usd = (sell_price - buy_price) * quantity

    if profit_usd > 0:
        print(f"You made {profit_usd:.5f} profit on {currency}! :)")
    else:
        print(f"You made {profit_usd:.5f} loss on {currency}! :(")
    return schemas.ProfitReportDataclass(
        currency=currency,
        quantity=quantity,
        buy_order_time=buy_order["transaction_time"],
        buy_order_price=buy_order["price"],
        sell_order_time=sell_order["transaction_time"],
        sell_order_price=sell_order["price"],
        difference_currency=difference,
        profit_usd=profit_usd,
        buy_order_id=buy_order["id"],
        sell_order_id=sell_order["id"],
    )


def get_all_currencies() -> list:
    """Returns all distinct symbols from database."""
    symbols = pd.read_sql(
        f"SELECT DISTINCT symbol FROM {contants.Tables.cryptocurrencies}", database.engine
    ).symbol.to_list()
    return symbols


def get_currency_price_from_lookback(
    currency: str, lookback: int
) -> pd.DataFrame:
    """Returns dataframe with data for a given crypto and lookback time."""
    now = dt.datetime.utcnow()
    before = now - dt.timedelta(minutes=lookback)
    qry_str = f"""
                SELECT * FROM {contants.Tables.cryptocurrencies}
                WHERE symbol = '{currency}' AND timestamp>= '{before}'
               """
    df = pd.read_sql(qry_str, database.engine)
    return df


def get_crypto_from_starting_time(
    currency: str, starting_time: Timestamp
) -> pd.DataFrame:
    df = pd.read_sql(
        f"""
            SELECT * FROM {contants.Tables.cryptocurrencies}
            WHERE symbol = '{currency}' AND timestamp>= '{starting_time}'""",
        database.engine,
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
