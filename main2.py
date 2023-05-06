import sys
import random
import threading
import time
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPalette, QColor, QLinearGradient, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, \
    QScrollArea, QFrame, QListWidget, QListWidgetItem, QSizePolicy
from mt5linux import MetaTrader5

# connecto to the server
mt5 = MetaTrader5(
    # host = 'localhost' (default)
    # port = 18812       (default)
)


# Function to update the price of a currency
running_trades = []
def update_price(currency, currency_labels, currency_ticks):
    # initialize the time and tick variables
    previous_time = datetime.datetime.now().minute
    previous_tick = mt5.symbol_info_tick(currency).time
    time_tick = 0
    previous_price = None
    check_price_change = False
    while True:
        # get the current tick and time
        current_tick = mt5.symbol_info_tick(currency).time
        current_time = datetime.datetime.now().minute
        current_price = mt5.symbol_info_tick(currency).bid

        # request the tick information
        tick = mt5.symbol_info_tick(currency)
        current_currency_index = currency_labels.index(currency)
        currency_ticks[current_currency_index].append(tick.bid)
        print(currency_ticks)

        if check_price_change:
            if current_price < previous_price and "Boom" in currency:
                print("Price changed")
                trade_type = "SELL"
                thread = threading.Thread(target=open_trade, args=(trade_type,currency))
                running_trades.append(thread)
                thread.start()

            else

            check_price_change = False

        if len(currency_ticks[current_currency_index]) > 100:
            del currency_ticks[current_currency_index][0]

        # Wait for 1 second before updating again
        time.sleep(1)

def open_trade(trade_type,currency):
    # initialize the time and tick variables
    previous_time = datetime.datetime.now().minute
    previous_tick = mt5.symbol_info_tick(currency).time
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": currency,
        "volume": 3.0,
        "type": mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(currency).bid,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # send a trading request
    result = mt5.order_send(request)
    print(result)


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.currency_labels = []
        self.price_labels = []
        # self.thread_outputs = []
        self.running_labels = []
        # self.start_buttons = []
        # self.stop_buttons = []
        self.stop_events = []
        self.threads = {}
        self.get_currencies()
        self.currency_ticks = []
        self.running_label = "Not Running"


        for currency in self.currency_labels:
            self.currency_ticks.append([])
            self.running_labels.append('Not Running')

        # Set the background color and gradient
        pal = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(26, 33, 62))
        gradient.setColorAt(1, QColor(22, 33, 62))
        pal.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(pal)

        # Set the layout
        main_layout = QHBoxLayout(self)

        # Add the history window to the left
        history_layout = QVBoxLayout()
        history_layout.setSpacing(10)
        history_label = QLabel('Trade History')
        history_label.setStyleSheet('color: white; font-size: 20px;')
        history_layout.addWidget(history_label)

        # Add the list of trades
        self.trade_list = QListWidget()
        self.trade_list.setStyleSheet(
            'color: white; font-size: 16px; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.trade_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        history_layout.addWidget(self.trade_list)

        # Add the time frame selector and lot size selector
        time_lot_layout = QHBoxLayout()
        time_frame_label = QLabel('Time Frame:')
        time_frame_label.setStyleSheet('color: white; font-size: 16px;')
        self.time_frame_selector = QComboBox()
        self.time_frame_selector.addItems(['1m', '5m', '15m', '30m', '1h', '4h', '1d'])
        self.time_frame_selector.setStyleSheet(
            'font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.time_frame_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_lot_layout.addWidget(time_frame_label)
        time_lot_layout.addWidget(self.time_frame_selector)

        lot_size_label = QLabel('Lot Size:')
        lot_size_label.setStyleSheet('color: white; font-size: 16px;')
        self.lot_size_selector = QComboBox()
        self.lot_size_selector.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1.0', '2.0', '5.0', '10.0'])
        self.lot_size_selector.setStyleSheet(
            'font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.lot_size_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_lot_layout.addWidget(lot_size_label)
        time_lot_layout.addWidget(self.lot_size_selector)

        history_layout.addLayout(time_lot_layout)

        # Create a horizontal layout for the currency label and selector
        currency_layout = QHBoxLayout()
        currency_label = QLabel('Currency:')
        currency_label.setStyleSheet('color: white; font-size: 16px;')
        self.currency_selector = QComboBox()
        self.currency_selector.addItems(self.currency_labels)
        self.currency_selector.setStyleSheet(
            'font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.currency_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.currency_selector)

        # Add the currency layout to the history layout
        history_layout.addLayout(currency_layout)

        # Create a layout for the stop and initialize chart buttons
        chart_buttons_layout = QHBoxLayout()
        self.stop_chart_button = QPushButton('Stop Chart')
        self.stop_chart_button.setStyleSheet(
            'font-size: 16px; color: white; background-color: #e74c3c; border-radius: 5px; padding: 5px;')
        self.stop_chart_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chart_buttons_layout.addWidget(self.stop_chart_button)

        # Add a stretchable space to the chart buttons layout
        chart_buttons_layout.addStretch(1)

        self.init_chart_button = QPushButton('Initialize Chart')
        self.init_chart_button.setStyleSheet(
            'font-size: 16px; color: white; background-color: #2ecc71; border-radius: 5px; padding: 5px;')
        self.init_chart_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chart_buttons_layout.addWidget(self.init_chart_button)

        # Add the chart buttons layout to the history layout
        history_layout.addLayout(chart_buttons_layout)

        # Add the history layout to the main layout
        main_layout.addLayout(history_layout)

        # Add the chart to the right
        chart_layout = QVBoxLayout()
        chart_layout.setSpacing(10)
        chart_label = QLabel('Chart')
        chart_label.setStyleSheet('color: white; font-size: 20px;')
        chart_layout.addWidget(chart_label)

        # Add the chart
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet('background-color: blue;')
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self.canvas)

        # Add the chart layout to the main layout
        main_layout.addLayout(chart_layout)

        # Set the main layout properties
        main_layout.setSpacing(20)

        # Set the window properties
        self.setWindowTitle('Trading Bot')
        self.setWindowIcon(QIcon('icon.png'))
        self.setMinimumSize(800, 600)
        self.show()

        # Connect the stop and initialize chart buttons to their respective functions
        self.stop_chart_button.clicked.connect(self.stop_chart)
        self.init_chart_button.clicked.connect(self.start_thread)

        # Update the chart every second
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_chart)

        # Set the chart running flag to false
        self.chart_running = False
        self.init_chart()

        # Connect the currency selector to its update function
        self.currency_selector.currentIndexChanged.connect(self.update_chart)

    def stop_chart(self):
        """
        Stops the chart from updating.
        """
        if self.chart_running:
            self.timer.stop()
            self.chart_running = False

    def get_currencies(self):

        """
        Get available currencies
        """
        if not mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # get the list of all available symbols
        symbols = mt5.symbols_get()
        for symbol in symbols:
            self.currency_labels.append(symbol.name)

    def init_chart(self):
        """
        Initializes the chart and starts updating it.
        """
        currency_index = self.currency_labels.index(self.currency_selector.currentText())
        if not self.chart_running:
            # self.currency_ticks = []
            # for i in range(3600):
            #     self.data.append(random.uniform(1.0, 1.1))
            self.ax = self.figure.add_subplot(111)
            self.ax.plot(self.currency_ticks[currency_index])
            # self.ax.set_ylim([min(self.data), max(self.data)])
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Price')

            self.ax.set_title(self.currency_selector.currentText(), color="red")
            self.chart_running = True
            self.timer.start()

    def update_chart(self):
        """
        Updates the chart by adding a new data point and redrawing the line.
        """
        color = 'red'
        current_currency_index = self.currency_labels.index(self.currency_selector.currentText())
        if(self.running_labels[current_currency_index] == "Running"):
            color = "green"

        if self.chart_running:
            # self.data.append(tick.bid)
            self.ax.clear()
            self.ax.plot(self.currency_ticks[current_currency_index])
            # self.ax.set_ylim([min(self.currency_ticks[current_currency_index]), max(self.currency_ticks[current_currency_index])])
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Price')
            self.ax.set_title(f"{self.currency_selector.currentText()} is {self.running_labels[current_currency_index]}",color=color)

            # Add a text annotation for the currency label
            currency_label = self.currency_selector.currentText()
            self.ax.text(0.5, 0.9, currency_label, transform=self.ax.transAxes, fontsize=16, color='white', ha='center',
                         va='center', bbox=dict(facecolor='black', alpha=0.5))

            self.canvas.draw()


    def start_thread(self):
        currency = self.currency_selector.currentText()
        # Start the thread corresponding to the selected currency
        if currency in self.threads and not self.threads[currency].is_alive():
            # The thread exists but is not running; start it
            stop_event = threading.Event()
            # self.stop_events[currencies.index(currency)] = stop_event
            # t = threading.Thread(target=update_price, args=(currency, self.thread_outputs[currencies.index(currency)], stop_event), name=currency)
            # self.threads[currency] = t
            # t.start()
            # self.running_labels[currencies.index(currency)].setText('Running')
        elif currency in self.threads and self.threads[currency].is_alive():
            # The thread exists and is running; do nothing
            pass
        else:
            # The thread doesn't exist; create it and start it
            current_currency_index = self.currency_labels.index(currency)
            # output = self.thread_outputs[currencies.index(currency)]
            stop_event = threading.Event()
            # self.stop_events[currencies.index(currency)] = stop_event
            t = threading.Thread(target=update_price, args=(currency, self.currency_labels, self.currency_ticks),
                                 name=currency)
            self.threads[currency] = t
            t.start()
            self.running_labels[current_currency_index] = "Running"
            trade_info = f'{self.currency_selector.currentText()} is Running'

            item = QListWidgetItem(trade_info)
            item.setForeground(QColor(46, 204, 113))
            self.trade_list.addItem(item)
            # self.running_labels[current_currency_index].setText('Running')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
