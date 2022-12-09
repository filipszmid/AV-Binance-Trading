import asyncio
import datetime
import time

import pandas as pd
import sqlalchemy


def get_database(currency: str) -> sqlalchemy.engine:
    return sqlalchemy.create_engine("sqlite:///database/" + currency + "-stream.db")


def set_pandas_to_print_all_values() -> None:
    pd.set_option(
        "display.width", 320, "display.max_rows", None, "display.max_columns", None
    )
    pd.options.mode.chained_assignment = None


def unix_to_date(unix_time: int) -> str:
    unix_time = unix_time / 1000
    local_time = time.localtime(unix_time)
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    # date_time = time.ctime(unix_time / 1000)
    return date_time


def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        number = 100
        if "every" in kwargs.keys():
            number = kwargs["every"]
        if "sleep" in kwargs.keys():
            time.sleep(kwargs["sleep"])
        if wrapped.calls % number == 0:
            for key in kwargs.keys():
                try:
                    temp = kwargs[key]
                    kwargs[key] = f"{temp:.5f}"
                except:
                    pass
            print(f"{wrapped.calls}:    {kwargs}")
        return f(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


@counted
def print_iter(*args, **kwargs):
    pass


def log_to_file(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        profit_report = function(*args, **kwargs)
        end_time = time.time()
        time_difference = datetime.timedelta(seconds=end_time - start_time)
        time_difference -= datetime.timedelta(microseconds=time_difference.microseconds)
        with open("reports/" + str(function.__name__) + "_report.csv", "a") as fd:
            fd.write(
                str(time_difference)
                + f",{profit_report.currency}, {profit_report.quantity}, {profit_report.buy_order_time}, {profit_report.buy_order_price}, {profit_report.sell_order_time}, {profit_report.sell_order_price}, {profit_report.difference_currency}, {profit_report.PLN}\n"
            )
        return profit_report

    return wrapper


def run_async(async_function):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_function(*args, **kwargs))

    wrapper.__name__ = async_function.__name__
    return wrapper


def round_to_full(num: float) -> float:
    num_string = str(num)
    round_num = ""

    for letter in num_string:
        if letter not in {".", "0"}:
            round_num += letter
            break
        else:
            round_num += letter
    return float(round_num)
