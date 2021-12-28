import websocket
import json
import numpy as np
import pandas as pd
import config
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import matplotlib.pyplot as plt

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05


closes = []
rsi = []

client = Client(API_KEY, API_SECRET, tld='us')

def get_RSI(closes,rsi_period):
    df = pd.DataFrame({"Close":closes})
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up/ema_down

    df['RSI'] = 100 - (100/(1 + rs))
    return df['RSI']

def plot_view(closes, rsi):
    figure, axis = plt.subplots(2)
    X1 = [i for i in range(len(closes))]
    Y1 = closes

    X2 = [i for i in range(len(rsi))]
    Y2 = rsi
    # For Sine Function
    axis[0].plot(X1, Y1)
    axis[0].set_title("PRICE")
  
    # For Cosine Function
    axis[1].plot(X2, Y2)
    axis[1].set_title("RSI")
    axis[1].axhline(30, color='r', linestyle='--')
    axis[1].axhline(70, color='r', linestyle='--')
    plt.show()

def on_open(ws):
    print('opened connection')

def on_close(ws):
    global closes, rsi
    print('closed connection')
    plot_view(closes, rsi)

def on_message(ws, message):
    global closes, in_position
    print('received message')
    json_message = json.loads(message)
    closes.append(float(json_message['k']['c']))
    if len(closes) > RSI_PERIOD:
        print('here')
        _rsi = get_RSI(closes,RSI_PERIOD)
        last_rsi = _rsi.iloc[-1]
        rsi.append(last_rsi)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
