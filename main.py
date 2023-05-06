import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPalette, QColor, QLinearGradient, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem, QSizePolicy

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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

        # Add the currency layout to the history layout
        history_layout.addLayout(currency_layout)

        # Create a layout for the stop and initialize chart buttons
        chart_buttons_layout = QHBoxLayout()
        self.stop_chart_button = QPushButton('Stop Chart')
        self.stop_chart_button.setStyleSheet('font-size: 16px; color: white; background-color: #e74c3c; border-radius: 5px; padding: 5px;')
        self.stop_chart_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chart_buttons_layout.addWidget(self.stop_chart_button)

        # Add a stretchable space to the chart buttons layout
        chart_buttons_layout.addStretch(1)

        self.init_chart_button = QPushButton('Initialize Chart')
        self.init_chart_button.setStyleSheet('font-size: 16px; color: white; background-color: #2ecc71; border-radius: 5px; padding: 5px;')
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
        self.canvas.setStyleSheet('background-color: white;')
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
        self.init_chart_button.clicked.connect(self.init_chart)

        # Update the chart every second
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_chart)

        # Set the chart running flag to false
        self.chart_running = False

    def init_chart(self):
        # Start the chart if it is not already running
        if not self.chart_running:
            self.timer.start()
            self.chart_running = True

    def stop_chart(self):
        # Stop the chart if it is running
        if self.chart_running:
            self.timer.stop()
            self.chart_running = False

    def update_chart(self):
        # Generate some random data to plot
        data = [random.random() for i in range(10)]

        # Clear the previous plot
        self.figure.clear()

        # Create a new plot with the random data
        ax = self.figure.add_subplot(111)
        ax.plot(data)

        # Update the canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())