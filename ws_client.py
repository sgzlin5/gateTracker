import time
import json
from threading import Thread
from PyQt6.QtCore import QObject, pyqtSignal
from websocket import create_connection, WebSocketConnectionClosedException

class WSClient(QObject):
    """WebSocket客户端，负责连接Gate.io并接收价格数据"""
    
    # 定义信号
    price_updated = pyqtSignal(str, dict)  # 更新价格信号: (symbol, data)
    connection_lost = pyqtSignal()          # 连接丢失信号
    
    def __init__(self, url: str = "wss://fx-ws.gateio.ws/v4/ws/tradfi", markets: list = None):
        super().__init__()
        self.url = url
        self.markets = markets if markets is not None else ["XAUUSD", "NAS100"]
        self.ws = None
        self.is_connected = False
        self.receive_thread = None
        self.should_stop = False
    
    def connect(self):
        """连接WebSocket服务器"""
        try:
            self.ws = create_connection(self.url)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            self.is_connected = False
            return False
    
    def subscribe(self, markets: list):
        """订阅市场数据
        
        Args:
            markets: 交易对列表，如 ["XAUUSD", "NAS100"]
        """
        if not self.is_connected or not self.ws:
            print("WebSocket未连接，无法订阅")
            return False
        
        try:
            message = {
                "time": int(time.time()),
                "channel": "tradfi.tickers",
                "event": "subscribe",
                "payload": {
                    "markets": markets
                }
            }
            self.ws.send(json.dumps(message))
            print(f"已订阅市场: {markets}")
            return True
        except Exception as e:
            print(f"订阅失败: {e}")
            return False
    
    def start_receiving(self):
        """启动接收消息线程"""
        if self.receive_thread and self.receive_thread.is_alive():
            return
        
        self.should_stop = False
        self.receive_thread = Thread(target=self._receive_messages_loop, daemon=True)
        self.receive_thread.start()
    
    def stop_receiving(self):
        """停止接收消息"""
        self.should_stop = True
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
    
    def _receive_messages_loop(self):
        """接收消息循环（在独立线程中运行）"""
        while not self.should_stop and self.is_connected:
            try:
                message_str = self.ws.recv()
                # 跳过空消息
                if message_str and message_str.strip():
                    self._parse_message(message_str)
            except WebSocketConnectionClosedException:
                print("WebSocket连接已断开")
                self.is_connected = False
                self.connection_lost.emit()
                break
            except Exception as e:
                # 只在严重错误时退出，空消息或其他小错误继续
                if "empty" not in str(e).lower():
                    print(f"接收消息错误: {e}")
                if not self.should_stop and "WebSocket" not in str(type(e)):
                    continue
                break
    
    def _parse_message(self, message_str: str):
        """解析WebSocket消息
        
        Args:
            message_str: 接收到的JSON格式消息字符串
        """
        try:
            message = json.loads(message_str)
            event = message.get("event", "")
            channel = message.get("channel", "")
            
            if event == "update" and channel == "tradfi.tickers":
                result = message.get("result", [])
                for item in result:
                    symbol = item.get("symbol", "")
                    if symbol in self.markets:
                        # 发射价格更新信号
                        self.price_updated.emit(symbol, item)
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
        except Exception as e:
            print(f"消息处理错误: {e}")
    
    def close(self):
        """关闭WebSocket连接"""
        self.should_stop = True
        self.stop_receiving()
        
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                print(f"关闭WebSocket连接时出错: {e}")
            self.ws = None
        
        self.is_connected = False
    
    def is_alive(self):
        """检查连接是否存活"""
        return self.is_connected and self.ws is not None
