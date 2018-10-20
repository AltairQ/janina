#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
team_name="PLASTICLOVE"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

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

def main():
    print("Test mode: ", test_mode)
    exchange = connect()

    valbz_theo = 0
    valbz_spread = 6
    vale_bid_price, vale_ask_price = 0, 0

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

if __name__ == "__main__":
    main()
