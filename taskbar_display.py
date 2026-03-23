"""任务栏嵌入式价格显示器

使用pywin32获取Windows任务栏位置，创建一个紧凑的价格显示窗口，
自动停靠在任务栏上方，看起来像是任务栏的一部分。
"""

import win32gui
import win32api
import win32con
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint


class TaskbarPositionHelper:
    """Windows任务栏位置助手类"""
    
    @staticmethod
    def get_taskbar_position():
        """获取Windows任务栏的位置和大小
        
        Returns:
            dict: 包含任务栏的x, y, width, height和位置的字典
        """
        try:
            # 查找任务栏窗口
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            
            # 获取任务栏窗口矩形
            rect = win32gui.GetWindowRect(taskbar_hwnd)
            
            taskbar_info = {
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
            
            # 判断任务栏位置
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # 判断任务栏在哪个边
            if taskbar_info['bottom'] == screen_height and taskbar_info['top'] < screen_height - 50:
                # 底部
                taskbar_info['position'] = 'bottom'
            elif taskbar_info['top'] == 0 and taskbar_info['height'] < 100:
                # 顶部
                taskbar_info['position'] = 'top'
            elif taskbar_info['left'] == 0 and taskbar_info['width'] < 100:
                # 左侧
                taskbar_info['position'] = 'left'
            elif taskbar_info['right'] == screen_width and taskbar_info['width'] < 100:
                # 右侧
                taskbar_info['position'] = 'right'
            else:
                # 默认底部
                taskbar_info['position'] = 'bottom'
            
            return taskbar_info
            
        except Exception as e:
            print(f"获取任务栏位置失败: {e}")
            # 返回默认值（底部）
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            return {
                'left': 0,
                'top': screen_height - 40,
                'right': screen_width,
                'bottom': screen_height,
                'width': screen_width,
                'height': 40,
                'position': 'bottom'
            }


class TaskbarPriceDisplay(QWidget):
    """任务栏嵌入式价格显示器窗口
    
    创建一个紧凑的价格显示窗口，自动定位到任务栏附近
    """
    
    # 信号：窗口关闭时发出
    closed = pyqtSignal()
    
    def __init__(self, markets=None, parent=None):
        super().__init__(parent)
        
        self.markets = markets or []
        self.price_data = {}
        
        # 初始化拖动状态
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # 标记用户是否手动拖动过窗口
        self.user_dragged = False
        
        # 设置窗口属性
        self._init_window()
        
        # 初始化UI
        self._init_ui()
        
        # 初始化位置
        self.position_on_taskbar()
        
        # 设置定时器定期检查任务栏位置（应对任务栏位置变化）
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.position_on_taskbar)
        self.position_timer.start(3000)  # 每3秒检查一次位置
        
        # 初始化价格数据
        for market in self.markets:
            self.price_data[market] = {
                'last_price': 0.0,
                'price_change_rate': 0.0,
                'price_change_amount': 0.0
            }
        
        # 更新显示
        self._update_display()
    
    def _init_window(self):
        """初始化窗口属性"""
        # 无边框、置顶、始终在任务栏上方
        window_flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # Tool窗口不在任务栏显示单独图标
        )
        
        self.setWindowFlags(window_flags)
        
        # 设置窗口背景为半透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口大小（紧凑型）
        self.setFixedHeight(36)  # 与任务栏高度相近
        self.setMinimumWidth(200)
    
    def _init_ui(self):
        """初始化UI组件"""
        # 主布局
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # 价格标签
        self.price_label = QLabel()
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.price_label.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 200);
                color: #ffffff;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.price_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def position_on_taskbar(self):
        """定位到任务栏附近"""
        # 如果用户已经手动拖动过窗口，则不再自动定位
        if self.user_dragged:
            return
            
        try:
            taskbar_info = TaskbarPositionHelper.get_taskbar_position()
            
            # 根据任务栏位置定位窗口
            window_width = self.width()
            window_height = self.height()
            
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            if taskbar_info['position'] == 'bottom':
                # 任务栏在底部，窗口显示在任务栏上方，靠右对齐
                x = screen_width - window_width - 10
                y = taskbar_info['top'] - window_height
            elif taskbar_info['position'] == 'top':
                # 任务栏在顶部，窗口显示在任务栏下方，靠右对齐
                x = screen_width - window_width - 10
                y = taskbar_info['bottom']
            elif taskbar_info['position'] == 'right':
                # 任务栏在右侧，窗口显示在任务栏左侧，底部对齐
                x = taskbar_info['left'] - window_width
                y = screen_height - window_height - 10
            elif taskbar_info['position'] == 'left':
                # 任务栏在左侧，窗口显示在任务栏右侧，底部对齐
                x = taskbar_info['right']
                y = screen_height - window_height - 10
            else:
                # 默认右下角
                x = screen_width - window_width - 10
                y = screen_height - window_height - 10
            
            self.move(x, y)
            
        except Exception as e:
            print(f"定位失败: {e}")
    
    def update_price(self, symbol: str, data: dict):
        """更新价格数据
        
        Args:
            symbol: 交易对符号
            data: 价格数据字典
        """
        if symbol in self.price_data:
            self.price_data[symbol]['last_price'] = float(data.get('last_price', 0))
            self.price_data[symbol]['price_change_rate'] = float(data.get('price_change_rate', 0))
            self.price_data[symbol]['price_change_amount'] = float(data.get('price_change_amount', 0))
            
            # 更新显示
            self._update_display()
    
    def _update_display(self):
        """更新价格显示"""
        price_parts = []
        
        for symbol, data in self.price_data.items():
            last_price = data['last_price']
            price_change_rate = data['price_change_rate']
            
            # 确定涨跌符号和颜色
            if price_change_rate > 0:
                change_symbol = "↑"
                color = "#4CAF50"  # 绿色
            elif price_change_rate < 0:
                change_symbol = "↓"
                color = "#F44336"  # 红色
            else:
                change_symbol = "→"
                color = "#ffffff"  # 白色
            
            # 格式化价格
            price_text = f"{symbol}:{last_price:.2f}{change_symbol}"
            price_parts.append(f'<span style="color:{color}">{price_text}</span>')
        
        # 更新标签文本
        text = "  |  ".join(price_parts)
        self.price_label.setText(text)
        
        # 调整窗口宽度以适应内容
        self.setMinimumWidth(self.price_label.sizeHint().width() + 40)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.position_timer.stop()
        self.closed.emit()
        event.accept()
    
    def mousePressEvent(self, event):
        """鼠标按下事件（开始拖动）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件（拖动窗口）"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_position = event.globalPosition().toPoint() - self.drag_position
            self.move(new_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件（结束拖动）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.user_dragged = True  # 标记用户已手动拖动
            event.accept()


class TaskbarDisplayController(QObject):
    """任务栏显示控制器
    
    管理任务栏显示器的创建、更新和销毁
    """
    
    # 信号：任务栏显示器关闭时发出
    closed = pyqtSignal()
    
    def __init__(self, markets=None):
        super().__init__()
        self.markets = markets or []
        self.display_window = None
    
    def show(self):
        """显示任务栏显示器"""
        if self.display_window is None:
            self.display_window = TaskbarPriceDisplay(self.markets)
            self.display_window.closed.connect(self._on_display_closed)
            self.display_window.show()
    
    def hide(self):
        """隐藏任务栏显示器"""
        if self.display_window:
            self.display_window.close()
            self.display_window = None
    
    def toggle(self):
        """切换显示/隐藏状态"""
        if self.display_window:
            self.hide()
        else:
            self.show()
    
    def update_price(self, symbol: str, data: dict):
        """更新价格数据
        
        Args:
            symbol: 交易对符号
            data: 价格数据字典
        """
        if self.display_window:
            self.display_window.update_price(symbol, data)
    
    def _on_display_closed(self):
        """显示器关闭回调"""
        self.display_window = None
        # 发出关闭信号，通知主窗口恢复
        self.closed.emit()
    
    def cleanup(self):
        """清理资源"""
        if self.display_window:
            self.display_window.close()
            self.display_window = None
