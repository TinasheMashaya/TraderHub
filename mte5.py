import time

from mt5linux import MetaTrader5

# connecto to the server
mt5 = MetaTrader5(
    # host = 'localhost' (default)
    # port = 18812       (default)
)

# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
    print("initialize() failed, error code =", mt5.last_error())
    quit()

import datetime

# connect to MetaTrader 5
mt5.initialize()

# subscribe to the symbol of interest
symbol = "Boom 500 Index"
mt5.symbol_select(symbol)

# initialize the time and tick variables
previous_time = datetime.datetime.now().minute
previous_tick = mt5.symbol_info_tick(symbol).time
time_tick = 0
previous_price = None
check_price_change = False
open_trade = False
while True:
    # get the current tick and time
    current_tick = mt5.symbol_info_tick(symbol).time
    current_time = datetime.datetime.now().minute
    current_price = mt5.symbol_info_tick(symbol).bid

    if check_price_change:
        if current_price < previous_price:
            print("Price changed")
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": 3.0,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid,
                "magic": 234000,
                "comment": "python script open",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # send a trading request
            result = mt5.order_send(request)
            print(result)
            open_trade = True
        check_price_change = False

    # check if a new minute has started
    if previous_price is not None:
        if current_time != previous_time and current_tick != previous_tick:
            # convert the epoch to datetime
            dt_object = datetime.datetime.fromtimestamp(current_tick)

            # print the datetime object
            print("Datetime object:", dt_object)

            # format the datetime object as a string
            dt_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            print("New minute started")
            print("New tick:", dt_string)
            previous_time = current_time
            time_tick = 0
            check_price_change = True
    previous_price = current_price


    # # check for spikes and avoid them
    # price_change = abs(mt5.symbol_info_tick(symbol).last - mt5.symbol_info_tick(symbol).prev_last)
    # if price_change < 5.0:  # adjust this threshold to your needs
    #     # do something with the tick
    #     if current_tick != previous_tick:
    #         print("New tick:", current_tick)
    #         previous_tick = current_tick
    # else:
    #     print("Ignoring spike with price change:", price_change)

    time_tick = time_tick + 1
    print(time_tick)
    if time_tick == 30 and open_trade:
        print("Get out of the trade")

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 3.0,
            "type": mt5.ORDER_TYPE_BUY,
            "position": result.order,
            "price": mt5.symbol_info_tick(symbol).ask,

            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        # send a trading request
        result = mt5.order_send(request)
        print(result)
        open_trade = False
    # wait for a short time before checking again
    time.sleep(1)
