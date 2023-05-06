import sys
import threading
import time
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser

# List of currencies to update
currencies = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'HKD']

# Simulated bid prices
prices = {currency: random.uniform(1, 100) for currency in currencies}

# Function to update the price of a currency
def update_price(currency, output, stop_event):
    while not stop_event.is_set():
        # Simulate a new bid price
        new_price = random.uniform(1, 100)
        prices[currency] = new_price
        output.append(f"{currency}: {new_price}")

        # Wait for 1 second before updating again
        time.sleep(1)

    # Clean up resources before exiting
    output.append(f"{currency}: Thread stopped")

class CurrencyUpdater(QWidget):
    def __init__(self):
        super().__init__()

        # Create the UI
        self.setWindowTitle('Currency Updater')
        self.resize(300, 400)

        self.currency_labels = []
        self.price_labels = []
        self.thread_outputs = []
        self.running_labels = []
        self.start_buttons = []
        self.stop_buttons = []
        self.stop_events = []
        self.threads = {}

        layout = QVBoxLayout()

        for currency in currencies:
            # Create a label, price label, output widget, running label, start button, and stop button for each currency
            label_layout = QHBoxLayout()
            currency_label = QLabel(currency)
            price_label = QLabel(str(prices[currency]))
            running_label = QLabel('Not Running')
            start_button = QPushButton('Start Thread')
            stop_button = QPushButton('Stop Thread')
            label_layout.addWidget(currency_label)
            label_layout.addWidget(price_label)
            label_layout.addWidget(running_label)
            label_layout.addWidget(start_button)
            label_layout.addWidget(stop_button)
            self.currency_labels.append(currency_label)
            self.price_labels.append(price_label)
            self.running_labels.append(running_label)
            self.start_buttons.append(start_button)
            self.stop_buttons.append(stop_button)

            output = QTextBrowser()
            self.thread_outputs.append(output)

            # Create an event and a thread for each currency
            stop_event = threading.Event()
            self.stop_events.append(stop_event)
            t = threading.Thread(target=update_price, args=(currency, output, stop_event), name=currency)
            self.threads[currency] = t

            # Connect the start button to a method that starts the corresponding thread
            start_button.clicked.connect(lambda _, curr=currency: self.start_thread(curr))

            # Connect the stop button to a method that stops the corresponding thread
            stop_button.clicked.connect(lambda _, curr=currency: self.stop_thread(curr))

            # Add the widgets to the layout
            layout.addLayout(label_layout)
            layout.addWidget(output)

        self.setLayout(layout)

        # Set up the timer to update the UI every 100ms
        self.timer = self.startTimer(100)

    def timemrEvent(self, event):
        # Update the UI with the latest prices and thread output
        for i in range(len(currencies)):
            self.price_labels[i].setText(str(prices[currencies[i]]))
            self.thread_outputs[i].setPlainText('\n'.join(self.thread_outputs[i].toPlainText().splitlines()[-10:]))

    def start_thread(self, currency):
        # Start the thread corresponding to the selected currency
        if currency in self.threads and not self.threads[currency].is_alive():
            # The thread exists but is not running; start it
            stop_event = threading.Event()
            self.stop_events[currencies.index(currency)] = stop_event
            t = threading.Thread(target=update_price, args=(currency, self.thread_outputs[currencies.index(currency)], stop_event), name=currency)
            self.threads[currency] = t
            t.start()
            self.running_labels[currencies.index(currency)].setText('Running')
        elif currency in self.threads and self.threads[currency].is_alive():
            # The thread exists and is running; do nothing
            pass
        else:
            # The thread doesn't exist; create it and start it
            output = self.thread_outputs[currencies.index(currency)]
            stop_event = threading.Event()
            self.stop_events[currencies.index(currency)] = stop_event
            t = threading.Thread(target=update_price, args=(currency, output, stop_event), name=currency)
            self.threads[currency] = t
            t.start()
            self.running_labels[currencies.index(currency)].setText('Running')

    def stop_thread(self, currency):
        # Stop the thread corresponding to the selected currency
        if currency in self.threads and self.threads[currency].is_alive():
            # The thread exists and is running; stop it
            self.stop_events[currencies.index(currency)].set()
            self.running_labels[currencies.index(currency)].setText('Not Running')
        else:
            # The thread doesn't exist or isn't running; do nothing
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    updater = CurrencyUpdater()
    updater.show()
    sys.exit(app.exec_())