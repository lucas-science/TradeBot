import websocket
import json
import pprint
import numpy
import talib

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05

Closes = []
global in_position
in_position = False
position = {
    "buyValue":0
}
global benefice
benefice = 0

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

def on_open(ws):
    print("opnened connection")

def on_close(ws):
    print("closed connection")

def on_message(ws,message):
    global in_position
    global benefice
    print("received message")
    json_message = json.loads(message)

    candle = json_message['k']
    isCandleClosed = candle['x']
    close = candle['c']
    if isCandleClosed:
        print("close at {}".format(close)) 
        Closes.append(float(close))
        print(Closes)

        if len(Closes) > RSI_PERIOD:
            np_closes = numpy.array(Closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD) # default period is 14
            print("RSI : ",rsi)
            last_rsi = rsi[-1]
            print("the current RSI is {}".format(last_rsi))
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("SELL")
                    benefice = TRADE_QUANTITY * close - TRADE_QUANTITY * position["buyValue"]
                    print("benefice", benefice)
                    in_position = False 
                else:
                    print("it s overbought but you own nothing")
                    #put binance order here
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("Oversold but you already own it")
                else:
                    position['buyValue'] = close
                    print("BUY",position)
                    in_position = True
                    #put binance order here



ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message)  
ws.run_forever()