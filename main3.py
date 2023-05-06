import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QTimer, QDateTime, QRectF
from PyQt5.QtGui import QPalette, QColor, QLinearGradient, QPixmap, QIcon, QPainter, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem, QSizePolicy

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
        self.trade_list.setStyleSheet('color: white; font-size: 16px; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.trade_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        history_layout.addWidget(self.trade_list)

        # Add the time frame selector and lot size selector
        time_lot_layout = QHBoxLayout()
        time_frame_label = QLabel('Time Frame:')
        time_frame_label.setStyleSheet('color: white; font-size: 16px;')
        self.time_frame_selector = QComboBox()
        self.time_frame_selector.addItems(['1m', '5m', '15m', '30m', '1h', '4h', '1d'])
        self.time_frame_selector.setStyleSheet('font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.time_frame_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_lot_layout.addWidget(time_frame_label)
        time_lot_layout.addWidget(self.time_frame_selector)

        lot_size_label = QLabel('Lot Size:')
        lot_size_label.setStyleSheet('color: white; font-size: 16px;')
        self.lot_size_selector = QComboBox()
        self.lot_size_selector.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1.0', '2.0', '5.0', '10.0'])
        self.lot_size_selector.setStyleSheet('font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.lot_size_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_lot_layout.addWidget(lot_size_label)
        time_lot_layout.addWidget(self.lot_size_selector)

        history_layout.addLayout(time_lot_layout)

        # Create a horizontal layout for the currency label and selector
        currency_layout = QHBoxLayout()
        currency_label = QLabel('Currency:')
        currency_label.setStyleSheet('color: white; font-size: 16px;')
        self.currency_selector = QComboBox()
        self.currency_selector.addItems(['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD'])
        self.currency_selector.setStyleSheet('font-size: 16px; color: white; background-color: #2c3e50; border-radius: 5px; padding: 5px;')
        self.currency_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.currency_selector)
        history_layout.addLayout(currency_layout)

        # Add the buy and sell buttons
        self.buy_button = QPushButton('Buy')
        self.buy_button.setStyleSheet('font-size: 16px; color: white; background-color: #2ecc71; border-radius: 5px; padding: 5px;')
        self.buy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        history_layout.addWidget(self.buy_button)

        self.sell_button = QPushButton('Sell')
        self.sell_button.setStyleSheet('font-size: 16px; color: white; background-color: #e74c3c; border-radius: 5px; padding: 5px;')
        self.sell_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        history_layout.addWidget(self.sell_button)

        # Add the history layout to the main layout
        main_layout.addLayout(history_layout)

        # Add the chart to the right
        self.chart_running = False
        self.figure = plt.Figure()
        self.canvas = RoundedFigureCanvas(self.figure)
        self.canvas.setStyleSheet('background-color: transparent;')
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = None

        # Add a scroll area to contain the chart
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('background-color: transparent; border: none;')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setWidget(self.canvas)

        main_layout.addWidget(scroll_area)

        # Connect signals and slots
        self.buy_button.clicked.connect(self.add_buy_trade)
        self.sell_button.clicked.connect(self.add_sell_trade)

        # Set the window properties
        self.setWindowTitle('Forex Trading Simulator')
        self.setWindowIcon(QIcon('icon.png'))
        self.setMinimumSize(800, 600)

        # Start the chart update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(1000)

    def add_buy_trade(self):
        currency = self.currency_selector.currentText()
        lot_size = float(self.lot_size_selector.currentText())
        price = round(random.uniform(1.0, 2.0), 5)
        time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        trade_info = f'BUY {lot_size} {currency} @ {price} [{time}]'

        item = QListWidgetItem(trade_info)
        item.setForeground(QColor(46, 204, 113))
        self.trade_list.addItem(item)

    def add_sell_trade(self):
        currency = self.currency_selector.currentText()
        lot_size = float(self.lot_size_selector.currentText())
        price = round(random.uniform(1.0, 2.0), 5)
        time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        trade_info = f'SELL {lot_size} {currency} @ {price} [{time}]'

        item = QListWidgetItem(trade_info)
        item.setForeground(QColor(231, 76, 60))
        self.trade_list.addItem(item)

    def update_chart(self):
        if not self.chart_running:
            self.chart_running = True

            if self.ax is None:
                self.ax = self.figure.add_subplot(111)

            # Clear the chart
            self.ax.clear()

            # Generate some random data for the chart
            data = [random.randint(1, 100) for i in range(20)]

            # Plot the data
            self.ax.plot(data)

            # Update the chart
            self.canvas.draw()

            self.chart_running = False

class RoundedFigureCanvas(FigureCanvas):
    def __init__(self, figure):
        super().__init__(figure)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Create a rounded rectangle for the chart area
        rect = QRectF(self.rect())
        chart_rect = QRectF(rect.x() + 10, rect.y() + 10, rect.width() - 20, rect.height() - 20)
        path = QPainterPath()
        path.addRoundedRect(chart_rect, 20, 20)
        painter.setClipPath(path)

        # Draw the chart background
        painter.setBrush(QColor(44, 62, 80))
        painter.drawRoundedRect(chart_rect, 20, 20)

        # Draw the chart
        super().paintEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())