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
# replace REPLACEME with your team name!
team_name="PLASTICLOVE"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True
# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
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
    exchange = connect()

    log_file = open('logs/trading_log_test', mode='w')
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=log_file)

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

if __name__ == "__main__":
    main()
