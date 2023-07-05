import logging

import click

from av_crypto_trading.core import binance_api, contants, strategies

client = binance_api.init_client()

logger = logging.getLogger(__name__)


@click.group()
def main():
    """packagename cli"""


@main.command()
def trend():
    strategies.strategy_trend(client, contants.Currencies.Bitcoin, 0.001, 60, 0.001)


@main.command()
def strategy_FastSMA_SlowSMA_long_interval():
    strategies.strategy_FastSMA_SlowSMA_long_interval(
        client, contants.Currencies.Bitcoin, 0.001
    )
