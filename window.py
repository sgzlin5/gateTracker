import json
import os
import sys
import copy
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QMenu,
                                QDialog, QSpinBox, QDialogButtonBox, QLabel,
                                QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor, QAction
from price_widget import PriceWidget
from ws_client import WSClient
from theme_manager import ThemeManager
from taskbar_display import TaskbarDisplayController
from system_tray import SystemTrayController

class PriceWindow(QMainWindow):
    """价格浮窗主窗口"""
    
    CONFIG_FILE = "user_config.json"
    
    def __init__(self):
        super().__init__()
        
        # 初始化拖动状态
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # 初始化配置
        self.config = self._load_config()
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager()
        
        # 初始化UI
        self._init_ui()
        
        # 应用主题
        self._apply_theme()
        
        # 初始化WebSocket客户端
        self.ws_client = None
        
        # 初始化任务栏显示控制器
        markets = self.config.get("markets", ["XAUUSD", "NAS100"])
        self.taskbar_display = TaskbarDisplayController(markets)
        
        # 连接任务栏显示器关闭信号，自动恢复主窗口
        if hasattr(self.taskbar_display, 'closed'):
            self.taskbar_display.closed.connect(self._on_taskbar_display_closed)
        
        # 初始化系统托盘控制器
        self.system_tray = SystemTrayController(self)
        self._connect_system_tray_signals()
        
        # 连接WebSocket
        self._connect_websocket()
        
        # 初始化任务栏标题
        self._update_taskbar_title()
        
        # 加载窗口位置和大小保存
        self._load_window_state()
        
        # 更新托盘图标状态
        self._update_tray_status()
    
    def _load_config(self):
        """加载配置文件"""
        default_config = {
            "window": {
                "width": 370,
                "height": 100,
                "always_on_top": True,
                "position": {
                    "x": 100,
                    "y": 100
                }
            },
            "theme": {
                "current": "dark"
            },
            "markets": ["XAUUSD", "NAS100"],
            "websocket": {
                "url": "wss://fx-ws.gateio.ws/v4/ws/tradfi"
            }
        }
        
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 深拷贝默认配置以避免修改
                    merged_config = copy.deepcopy(default_config)
                    # 递归合并配置
                    self._deep_merge(merged_config, loaded_config)
                    return merged_config
        except Exception as e:
            print(f"配置加载错误: {e}")
        
        return default_config
    
    def _deep_merge(self, base: dict, override: dict):
        """递归合并字典配置
        
        Args:
            base: 基础配置字典（会被修改）
            override: 覆盖配置字典
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _init_ui(self):
        """初始化UI"""
        # 初始化价格组件字典
        self.price_widgets = {}
        
        # 设置窗口无边框、置顶显示（根据配置）
        window_config = self.config.get("window", {})
        always_on_top = window_config.get("always_on_top", True)
        
        window_flags = Qt.WindowType.FramelessWindowHint
        if always_on_top:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        
        self.setWindowFlags(window_flags)
        
        # 设置窗口大小
        width = window_config.get("width", 370)
        height = window_config.get("height", 100)
        self.resize(width, height)
        self.setMinimumSize(340, 80)  # 设置最小尺寸约束
        
        # 设置窗口背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建主widget和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_layout)
        
        # 创建内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 5, 0, 5)
        self.content_layout.setSpacing(0)
        self.content_widget.setLayout(self.content_layout)
        
        # 添加价格显示组件
        markets = self.config.get("markets", ["XAUUSD", "NAS100"])
        for market in markets:
            price_widget = PriceWidget(market)
            self.price_widgets[market] = price_widget
            self.content_layout.addWidget(price_widget)
        
        # 移除最后一个分隔线
        if markets:
            last_widget = self.price_widgets[markets[-1]]
            if hasattr(last_widget, 'separator'):
                last_widget.separator.hide()
        
        self.main_layout.addWidget(self.content_widget)
    
    def _apply_theme(self):
        """应用主题样式"""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def _connect_websocket(self):
        """连接WebSocket并订阅市场数据"""
        try:
            ws_url = self.config.get("websocket", {}).get("url", "wss://fx-ws.gateio.ws/v4/ws/tradfi")
            markets = self.config.get("markets", ["XAUUSD", "NAS100"])
            
            # 创建WebSocket客户端（传入市场列表）
            self.ws_client = WSClient(ws_url, markets)
            
            # 连接信号
            self.ws_client.price_updated.connect(self._on_price_updated)
            self.ws_client.connection_lost.connect(self._on_connection_lost)
            
            # 连接服务器
            if self.ws_client.connect():
                # 订阅市场数据
                self.ws_client.subscribe(markets)
                # 启动接收线程
                self.ws_client.start_receiving()
                print("WebSocket连接成功")
            else:
                print("WebSocket连接失败")
                
        except Exception as e:
            print(f"WebSocket初始化错误: {e}")
    
    def _on_price_updated(self, symbol: str, data: dict):
        """价格更新回调"""
        if symbol in self.price_widgets:
            self.price_widgets[symbol].update_price(data)
            # 更新任务栏标题
            self._update_taskbar_title()
            # 更新任务栏显示器
            self.taskbar_display.update_price(symbol, data)
    
    def _update_taskbar_title(self):
        """更新任务栏标题显示价格信息"""
        title_parts = []
        for symbol, widget in self.price_widgets.items():
            # 获取最新价格和涨跌幅
            last_price = widget.last_price
            price_change_rate = widget.price_change_rate
            change_symbol = "↑" if price_change_rate > 0 else ("↓" if price_change_rate < 0 else "→")
            title_parts.append(f"{symbol} {last_price:.2f} {change_symbol}")
        
        self.setWindowTitle(" | ".join(title_parts))
        
        # 更新托盘图标的工具提示
        if hasattr(self, 'system_tray') and self.system_tray.is_available():
            self.system_tray.update_tooltip(
                f"Gate Price Tracker - {self.windowTitle()}"
            )
    
    def _on_connection_lost(self):
        """连接丢失回调"""
        print("WebSocket连接丢失")
        # 可以在这里实现重连逻辑
    
    def _load_window_state(self):
        """加载窗口位置和大小"""
        window_config = self.config.get("window", {})
        position = window_config.get("position", {})
        
        x = position.get("x", 100)
        y = position.get("y", 100)
        self.move(x, y)
    
    def _save_window_state(self):
        """保存窗口位置和大小"""
        position = self.pos()
        size = self.size()
        
        self.config.setdefault("window", {})
        self.config["window"]["position"] = {
            "x": position.x(),
            "y": position.y()
        }
        self.config["window"]["width"] = size.width()
        self.config["window"]["height"] = size.height()
        
        self._save_config()
    
    def set_window_size(self, width: int, height: int):
        """设置窗口大小
        
        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.resize(width, height)
        
        # 更新配置
        self.config.setdefault("window", {})
        self.config["window"]["width"] = width
        self.config["window"]["height"] = height
        self._save_config()
    
    def _connect_system_tray_signals(self):
        """连接系统托盘信号"""
        if not self.system_tray.is_available():
            print("系统托盘不可用")
            return
        
        # 显示/隐藏主窗口
        self.system_tray.show_window_requested.connect(self._on_show_window)
        self.system_tray.hide_window_requested.connect(self._on_hide_window)
        
        # 切换任务栏显示器
        self.system_tray.toggle_taskbar_display_requested.connect(self.toggle_taskbar_display)
        
        # 切换主题
        self.system_tray.toggle_theme_requested.connect(self.toggle_theme)
        
        # 显示设置
        self.system_tray.show_settings_requested.connect(self.show_size_dialog)
        
        # 退出程序
        self.system_tray.exit_requested.connect(self._on_force_exit)
    
    def _on_show_window(self):
        """显示主窗口"""
        self.showNormal()
        self.activateWindow()
        self._update_tray_status()
    
    def _on_hide_window(self):
        """隐藏主窗口"""
        self.hide()
        self._update_tray_status()
    
    def _update_tray_status(self):
        """更新托盘图标状态"""
        if self.system_tray.is_available():
            # 更新显示/隐藏按钮文本
            self.system_tray.update_show_hide_action(self.isVisible())
            
            # 更新任务栏显示器状态
            self.system_tray.update_taskbar_display_action(
                self.taskbar_display.display_window is not None
            )
            
            # 更新工具提示
            self.system_tray.update_tooltip(
                f"Gate Price Tracker - {self.windowTitle()}"
            )
    
    def toggle_theme(self):
        """切换主题"""
        new_theme = self.theme_manager.toggle()
        self._apply_theme()
        print(f"已切换到{new_theme}主题")
    
    def toggle_taskbar_display(self):
        """切换任务栏显示器的显示状态"""
        self.taskbar_display.toggle()
        
        # 更新托盘状态
        self._update_tray_status()
        
        # 如果任务栏显示器正在显示，则最小化主窗口
        if self.taskbar_display.display_window is not None:
            self.showMinimized()
        else:
            # 任务栏显示器已隐藏，恢复主窗口
            self.showNormal()
    
    def _on_taskbar_display_closed(self):
        """任务栏显示器关闭时自动恢复主窗口"""
        self.showNormal()
    
    def set_always_on_top(self, always_on_top: bool):
        """设置窗口是否始终置顶
        
        Args:
            always_on_top: True表示始终置顶，False表示不置顶
        """
        # 获取当前窗口标志
        current_flags = self.windowFlags()
        
        # 清除置顶标志
        current_flags &= ~Qt.WindowType.WindowStaysOnTopHint
        
        # 如果需要置顶，则添加置顶标志
        if always_on_top:
            current_flags |= Qt.WindowType.WindowStaysOnTopHint
        
        # 应用新的窗口标志
        self.setWindowFlags(current_flags)
        self.show()  # 设置窗口标志后需要重新显示窗口
        
        # 更新配置
        self.config.setdefault("window", {})
        self.config["window"]["always_on_top"] = always_on_top
        self._save_config()
        
        print(f"已{'启用' if always_on_top else '禁用'}窗口置顶")
    
    def show_size_dialog(self):
        """显示窗口大小设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("窗口设置")
        dialog.setFixedSize(280, 180)
        
        layout = QVBoxLayout()
        
        # 宽度设置
        width_label = QLabel("宽度:")
        width_spin = QSpinBox()
        width_spin.setRange(200, 800)
        width_spin.setValue(self.width())
        
        # 高度设置
        height_label = QLabel("高度:")
        height_spin = QSpinBox()
        height_spin.setRange(80, 600)
        height_spin.setValue(self.height())
        
        # 始终置顶设置
        always_on_top_label = QLabel("始终置顶:")
        always_on_top_checkbox = QCheckBox()
        window_config = self.config.get("window", {})
        always_on_top_checkbox.setChecked(window_config.get("always_on_top", True))
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        # 布局
        width_layout = QVBoxLayout()
        width_layout.addWidget(width_label)
        width_layout.addWidget(width_spin)
        
        height_layout = QVBoxLayout()
        height_layout.addWidget(height_label)
        height_layout.addWidget(height_spin)
        
        top_layout = QVBoxLayout()
        top_layout.addWidget(always_on_top_label)
        top_layout.addWidget(always_on_top_checkbox)
        
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        layout.addLayout(top_layout)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_width = width_spin.value()
            new_height = height_spin.value()
            always_on_top = always_on_top_checkbox.isChecked()
            
            self.set_window_size(new_width, new_height)
            self.set_always_on_top(always_on_top)
    
    def contextMenuEvent(self, event):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 切换任务栏显示
        taskbar_action = QAction("显示任务栏显示器", self)
        taskbar_action.setCheckable(True)
        taskbar_action.setChecked(self.taskbar_display.display_window is not None)
        taskbar_action.triggered.connect(self.toggle_taskbar_display)
        menu.addAction(taskbar_action)
        
        menu.addSeparator()
        
        # 切换主题
        theme_action = QAction("切换主题", self)
        theme_action.triggered.connect(self.toggle_theme)
        menu.addAction(theme_action)
        
        # 设置窗口大小
        size_action = QAction("设置窗口大小...", self)
        size_action.triggered.connect(self.show_size_dialog)
        menu.addAction(size_action)
        
        menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        # 显示菜单
        menu.exec(QCursor.pos())
    
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
            event.accept()
            # 保存窗口位置
            self._save_window_state()
    
    def activateEvent(self, event):
        """窗口激活事件"""
        super().activateEvent(event)
        # 窗口激活时确保置顶属性生效
        window_config = self.config.get("window", {})
        always_on_top = window_config.get("always_on_top", True)
        if always_on_top:
            # 检查当前是否有置顶标志，如果没有则添加
            current_flags = self.windowFlags()
            if not (current_flags & Qt.WindowType.WindowStaysOnTopHint):
                current_flags |= Qt.WindowType.WindowStaysOnTopHint
                self.setWindowFlags(current_flags)
                self.show()
    
    def _on_force_exit(self):
        """强制退出程序"""
        # 保存窗口状态
        self._save_window_state()
        
        # 关闭任务栏显示器
        self.taskbar_display.cleanup()
        
        # 关闭系统托盘
        if hasattr(self, 'system_tray'):
            self.system_tray.cleanup()
        
        # 关闭WebSocket连接
        if self.ws_client:
            self.ws_client.close()
        
        # 退出应用程序
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果系统托盘可用，则隐藏到托盘而不是退出
        if self.system_tray.is_available():
            self.hide()
            self._update_tray_status()
            event.ignore()
            return
        
        # 保存窗口状态
        self._save_window_state()
        
        # 关闭任务栏显示器
        self.taskbar_display.cleanup()
        
        # 关闭系统托盘
        if hasattr(self, 'system_tray'):
            self.system_tray.cleanup()
        
        # 关闭WebSocket连接
        if self.ws_client:
            self.ws_client.close()
        
        event.accept()
    

