#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import datetime

test_mode = None

if sys.argv[1] == "dev":
    test_mode = True

if sys.argv[1] == "prod":
    test_mode = False

if test_mode is None:
    print("Wrong mode!")
    sys.exit(3)



# ~~~~~============== CONFIGURATION  ==============~~~~~
team_name="PLASTICLOVE"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!

test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== MAIN LOOP ==============~~~~~


def h_to_xlf(dic):
    return (3*dic['BOND'] +
            2*dic['GS'] +
            3*dic['MS'] +
            2*dic['WFC']) / 10

def to_xlf(buy, sell):
    return (h_to_xlf(buy), h_to_xlf(sell))

    



def main():
    print("Test mode: ", test_mode)
    exchange = connect()

    pending = {}
    wallet = {}

    cid = 3;

    valbz_theo = 0
    valbz_spread = 6
    vale_bid_price, vale_ask_price = 0, 0

    xlf_spread = 2;

    cartp_buy = {
        "XLF": -1,
        "GS": -1,
        "MS": -1,
        "WFC": -1,
        "BOND": 1000
    }

    cartp_sell = {
        "XLF": -1,
        "GS": -1,
        "MS": -1,
        "WFC": -1,
        "BOND": 1000
    }

    log_file = open('logs/trading_log_test_observer', mode='w')
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=log_file)
    print("Handshake done")

    init_buy_order = {"type": "add", "order_id": 1, "symbol": "BOND", "dir": "BUY", "price": 999, "size":10}
    init_sell_order = {"type": "add", "order_id": 2, "symbol": "BOND", "dir": "SELL", "price":  1001, "size":10}

    write_to_exchange(exchange, init_buy_order)
    print("Command sent:", init_buy_order, file=log_file)
    print("The exchange replied:", read_from_exchange(exchange), file=log_file)
    write_to_exchange(exchange, init_sell_order)
    print("Command sent:", init_buy_order, file=log_file)
    print("The exchange replied:", read_from_exchange(exchange), file=log_file)
    
    while True:

        exchange_message = read_from_exchange(exchange)
        print("The exchange messaged:", exchange_message, file=log_file)

        # refresh BOND orders

        if exchange_message['type'] == 'out':
            if exchange_message['order_id'] == 1:
                buy_order = {"type": "add", "order_id": 1, "symbol": "BOND", "dir": "BUY", "price": 999, "size":10}
                write_to_exchange(exchange, buy_order)
                print("Command sent:", buy_order, file=log_file)
                print("The exchange replied:", read_from_exchange(exchange), file=log_file)
            elif exchange_message['order_id'] == 2:
                sell_order = {"type": "add", "order_id": 2, "symbol": "BOND", "dir": "SELL", "price": 1001, "size":10}
                write_to_exchange(exchange, sell_order)
                print("Command sent:", sell_order, file=log_file)
                print("The exchange replied:", read_from_exchange(exchange), file=log_file)
            elif exchange_message['order_id'] == 3:
                buy_order = {"type": "add", "order_id": 3, "symbol": "VALE", "dir": "BUY", "price": int(vale_bid_price), "size": 5}
                write_to_exchange(exchange, buy_order)
                print("Command sent:", buy_order, file=log_file)
                print("The exchange replied:", read_from_exchange(exchange), file=log_file)
            elif exchange_message['order_id'] == 4:
                sell_order = {"type": "add", "order_id": 4, "symbol": "VALE", "dir": "SELL", "price": int(vale_ask_price), "size": 5}
                write_to_exchange(exchange, sell_order)
                print("Command sent:", sell_order, file=log_file)
                print("The exchange replied:", read_from_exchange(exchange), file=log_file)

        # check and refresh VALE orders

        if exchange_message['type'] == 'book':
            if exchange_message['symbol'] == 'VALBZ':
                if (len(exchange_message['buy']) > 0) and (len(exchange_message['sell']) > 0):

                    valbz_theo = (exchange_message['buy'][0][0] + exchange_message['sell'][0][0]) / 2

                    if (valbz_theo > vale_ask_price) or (valbz_theo < vale_bid_price):

                        cancel_order = {"type": "cancel", "order_id": 3}
                        write_to_exchange(exchange, cancel_order)
                        print("Command sent:", cancel_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)

                        cancel_order = {"type": "cancel", "order_id": 4}
                        write_to_exchange(exchange, cancel_order)
                        print("Command sent:", cancel_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)

                        vale_ask_price = round(valbz_theo + valbz_spread / 2)
                        vale_bid_price = round(valbz_theo - valbz_spread / 2)

                        buy_order = {"type": "add", "order_id": 3, "symbol": "VALE", "dir": "BUY", "price": int(vale_bid_price), "size": 5}
                        write_to_exchange(exchange, buy_order)
                        print("Command sent:", buy_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)
                        print("VALE buy order done", file=sys.stderr)

                        sell_order = {"type": "add", "order_id": 4, "symbol": "VALE", "dir": "SELL", "price": int(vale_ask_price), "size": 5}
                        write_to_exchange(exchange, sell_order)
                        print("Command sent:", sell_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)
            elif exchange_message['symbol'] in ['XLF', 'GS', 'MS', 'WFC']:
                if len(exchange_message['buy']) > 0:
                    cartp_buy[exchange_message['symbol']] = max([v[0] for v in exchange_message['buy']])

                if len(exchange_message['sell']) > 0:
                    cartp_sell[exchange_message['symbol']] = min([v[0] for v in exchange_message['sell']])

                if -1 not in [v[1] for v in cartp_buy.items()] and [v[1] for v in cartp_sell.items()]:
                    calc_buy, calc_sell = to_xlf(cartp_buy, cartp_sell)
                    xlf_theo = (calc_sell + calc_buy)/2

                    # print("XLF DEBUG calc_buy: " + str(calc_buy) + " calc_sell: " + str(calc_sell))

                    if (calc_buy > xlf_theo) or (calc_sell < xlf_theo):
                        print("DUPA")
                        cancel_order = {"type": "cancel", "order_id": 21}
                        write_to_exchange(exchange, cancel_order)
                        print("Command sent:", cancel_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)

                        cancel_order = {"type": "cancel", "order_id": 37}
                        write_to_exchange(exchange, cancel_order)
                        print("Command sent:", cancel_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)

                        xlf_ask_price = round(xlf_theo + xlf_spread / 2)
                        xlf_bid_price = round(xlf_theo - xlf_spread / 2)

                        buy_order = {"type": "add", "order_id": 21, "symbol": "XLF", "dir": "BUY", "price": int(xlf_bid_price), "size": 10}
                        write_to_exchange(exchange, buy_order)
                        print("Command sent:", buy_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)
                        print("XLF buy order done", file=sys.stderr)

                        sell_order = {"type": "add", "order_id": 37, "symbol": "XLF", "dir": "SELL", "price": int(xlf_ask_price), "size": 10}
                        write_to_exchange(exchange, sell_order)
                        print("Command sent:", sell_order, file=log_file)
                        print("The exchange replied:", read_from_exchange(exchange), file=log_file)



        # if exchange_message["type"] == "fill":





                    



if __name__ == "__main__":
    main()
