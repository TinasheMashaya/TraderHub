import matplotlib.pyplot as plt

import threading
from mt5linux import MetaTrader5
# connecto to the server
mt5 = MetaTrader5(
    # host = 'localhost' (default)
    # port = 18812       (default)
)

class ChartThread(threading.Thread):
    def __init__(self, symbol):
        threading.Thread.__init__(self)
        self.symbol = symbol
        self.running = False
        self.stop_event = threading.Event()
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Bid Price')
        self.line, = self.ax.plot([], [], label=symbol)
        self.ax.legend()

    def run(self):
        self.running = True
        while self.running:
            if not mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
                print(f"initialize() failed { mt5.initialize()}")
                mt5.shutdown()
                self.running = False
                continue

            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                continue

            self.line.set_xdata(range(len(self.line.get_ydata()) + 1))
            self.line.set_ydata(list(self.line.get_ydata()) + [tick.bid])
            self.ax.relim()
            self.ax.autoscale_view(True, True, True)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            mt5.shutdown()
            self.stop_event.wait(timeout=1)

        plt.close(self.fig)

    def stop(self):
        self.running = False
        self.stop_event.set()


if __name__ == '__main__':
    symbol = 'Crash 1000 Index'

    chart_thread = ChartThread(symbol)
    chart_thread.start()

    # wait for user input to stop the chart
    input("Press any key to stop the chart\n")

    chart_thread.stop()
    chart_thread.join()