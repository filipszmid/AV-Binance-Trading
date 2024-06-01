import multiprocessing

from av_crypto_trading.core import (
    binance_api,
    contants,
    database_api,
    strategies,
    streams,
    utils,
)


class Bot:
    def __init__(
        self,
    ):
        """
        Orchestrate different strategies as subprocesses
        invoked on different coins specified in
        position_checks table in the following way:
            currency,position,quantity
            BTCUSDT,0,0
            ETHUSDT,0,0

        """

        self.client = binance_api.init_client()
        s = multiprocessing.Process(
            target=streams.ubwa_stream_all_crypto_to_master_db, args=()
        )
        s.start()
        self.processes = [s]

    def shut_down(self):
        print(f"Shutting down the stream process: {self.processes[0].pid}")
        self.processes[0].terminate()

    def run_strategy_on_multiple_coins(self, quantity: float):
        positions = database_api.read_position_checks()
        for currency in positions.currency:
            print(f"Starting strategy for currency {currency}")
            # p = multiprocessing.Process(
            #     target=strategies.strategy_trend,
            #     args=(currency, 0.001, 60, 0.001),
            # )
            # TODO: remember you input quantity coin, it can have different value for different coins
            p = multiprocessing.Process(
                target=strategies.strategy_MACD,
                args=(currency, quantity),
            )
            p.start()
            self.processes.append(p)
        self._join_processes()

    def _join_processes(self):
        for p in self.processes:
            p.join()

    def run_forever(self, quantity: float):
        while True:
            try:
                self.run_strategy_on_multiple_coins(quantity)
            except Exception as e:
                print(f"The following exception occures: {e}\n" "Continuing...")
                continue

    def run_on_one_coin(self, currency: contants.Currencies, quantity: float):
        p = multiprocessing.Process(
            target=strategies.strategy_MACD,
            args=(currency, quantity),
        )
        p.start()
        self.processes.append(p)
        self._join_processes()


# a=subprocess.run(["binance_trading", "trend"], capture_output=True)

# print(a.stderr)
