import asyncio
import datetime
import inspect
import multiprocessing
import time
import traceback

import pandas as pd

from av_crypto_trading.core import contants, database_api


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
    """Black magic print reporter."""

    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        number = 100
        if "every" in kwargs.keys():
            number = kwargs["every"]
        if "sleep" in kwargs.keys():
            time.sleep(kwargs["sleep"])
        if wrapped.calls % number == 0:
            print("-----------------------------")
            if "frame" in kwargs.keys():
                process = multiprocessing.current_process()
                frame = kwargs["frame"]
                args, _, _, values = inspect.getargvalues(frame)
                print(f"strategy: {frame.f_code.co_name} PID: {process.pid}")
                print(f"parameters: {[(i, values[i]) for i in args]}")
                kwargs.pop("frame")
            for key in kwargs.keys():
                try:
                    temp = kwargs[key]
                    kwargs[key] = f"{temp:.5f}"
                except Exception:
                    pass
            print(f"{wrapped.calls}:    {kwargs}")
            print("-----------------------------")
        return f(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


@counted
def print_iter(*args, **kwargs):
    pass


def report_strategy(function):
    """Saves to database strategy reports decorator."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            profit_report = function(*args, **kwargs)
            full_report = profit_report.to_dict()
            full_report["description"] = str(function.__name__)
        except Exception as e:
            traceback.print_exc()
            full_report = {
                "currency": "error",
                "quantity": None,
                "buy_order_time": None,
                "buy_order_price": None,
                "sell_order_time": None,
                "sell_order_price": None,
                "difference_currency": None,
                "profit_usd": None,
                "buy_order_id": None,
                "sell_order_id": None,
                "description": str(function.__name__) + " ERROR: " + str(e),
            }

        end_time = time.time()
        time_difference = datetime.timedelta(seconds=end_time - start_time)
        time_difference -= datetime.timedelta(microseconds=time_difference.microseconds)
        full_report["duration"] = str(time_difference)
        database_api.save_dict_to_db(full_report, contants.Tables.profit_reports)
        return full_report

    return wrapper


def run_async(async_function):
    """Runs async function decorator."""

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
