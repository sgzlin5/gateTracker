import time
import json

# pip install websocket_client
from websocket import create_connection

ws = create_connection("wss://fx-ws.gateio.ws/v4/ws/tradfi")
ws.send(json.dumps({
    "time": int(time.time()),
    "channel": "tradfi.tickers",
    "event": "subscribe",  # "unsubscribe" for unsubscription
    "payload": {
       "markets": ["XAUUSD","NAS100"]
    }
}))
print(ws.recv())