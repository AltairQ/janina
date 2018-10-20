#!/usr/bin/python3
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

s = None
sfile = None

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    global s
    global sfile
    if s is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((exchange_hostname, port))
        sfile = s.makefile("rw", 1)

    return sfile

def reset_connect():
    global s
    s = None

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== SIMPLE COMMANDS ==============~~~~~

def _handshake(ex):
    write_to_exchange(ex, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(ex)
    return hello_from_exchange

def hello():
    ex = connect()
    return _handshake(ex)
    

def add(order_id, symbol, dir, price, size):
    ex = connect()
    
    params = {
        "type": "add",
        "order_id": order_id,
        "symbol": symbol,
        "dir": dir,
        "price": price,
        "size": size,
    }

    write_to_exchange(ex, params)

    response = read_from_exchange(ex)

    if response["type"] == "reject":
        pass
        #TODO: HANDLE REJECT MESSAGE
    elif response["type"] == "ack":
        pass
        #TODO: HANDLE ACK MESSAGE
    else:
        pass
        #TODO: HANDLE MALFORMED MESSAGE


def convert(order_id, symbol, dir, size):
    ex = connect()

    params = {
        "type": "convert",
        "order_id": order_id,
        "symbol": symbol,
        "dir": dir,
        "size": size,
    }

    write_to_exchange(ex, params)