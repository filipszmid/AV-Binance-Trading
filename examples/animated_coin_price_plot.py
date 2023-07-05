# %matplotlib inline
import matplotlib

matplotlib.use("Tkagg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from av_crypto_trading.core.binance_api import get_minute_data, init_client
from av_crypto_trading.core.contants import Currencies

plt.interactive(False)

plt.style.use("ggplot")
client = init_client()
currency = Currencies.Bitcoin


def animate(i):
    data = get_minute_data(currency=currency, client=client)
    plt.cla()
    plt.plot(data.index, data.close)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title(currency)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, 1000)
plt.tight_layout()
plt.show()
