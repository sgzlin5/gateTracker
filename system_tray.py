"""系统托盘控制器

提供系统托盘图标功能，支持通过托盘图标控制主窗口的显示/隐藏，
并提供完整的右键菜单功能。
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QIcon
import sys
import os


class SystemTrayController(QObject):
    """系统托盘控制器
    
    管理系统托盘图标的创建、更新和交互
    """
    
    # 信号定义
    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    toggle_taskbar_display_requested = pyqtSignal()
    toggle_theme_requested = pyqtSignal()
    show_settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        
        self.main_window = main_window
        self.tray_icon = None
        
        # 创建托盘图标
        self._create_tray_icon()
    
    def _create_tray_icon(self):
        """创建系统托盘图标"""
        # 检查系统是否支持托盘图标
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持托盘图标")
            return
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 设置图标（使用应用程序图标或默认图标）
        icon = self._get_app_icon()
        self.tray_icon.setIcon(icon)
        
        # 设置工具提示
        self.tray_icon.setToolTip("Gate Price Tracker")
        
        # 创建托盘菜单
        self._create_tray_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        print("系统托盘图标已创建")
    
    def _get_app_icon(self):
        """获取应用程序图标
        
        Returns:
            QIcon: 应用程序图标
        """
        # 尝试加载自定义图标
        icon_paths = [
            "icon.ico",
            "icon.png",
            "assets/icon.ico",
            "assets/icon.png",
            "resources/icon.ico",
            "resources/icon.png"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        
        # 使用Qt内置图标（信息图标）
        return QIcon.fromTheme("application-x-executable", 
                             QIcon.fromTheme("help-about"))
    
    def _create_tray_menu(self):
        """创建托盘右键菜单"""
        if not self.tray_icon:
            return
        
        menu = QMenu()
        
        # 显示/隐藏主窗口
        self.show_hide_action = QAction("显示主窗口", self)
        self.show_hide_action.triggered.connect(self._on_show_hide_window)
        menu.addAction(self.show_hide_action)
        
        menu.addSeparator()
        
        # 任务栏显示器
        self.taskbar_display_action = QAction("显示任务栏显示器", self)
        self.taskbar_display_action.setCheckable(True)
        self.taskbar_display_action.triggered.connect(self._on_toggle_taskbar_display)
        menu.addAction(self.taskbar_display_action)
        
        menu.addSeparator()
        
        # 切换主题
        theme_action = QAction("切换主题", self)
        theme_action.triggered.connect(self._on_toggle_theme)
        menu.addAction(theme_action)
        
        # 设置窗口大小
        settings_action = QAction("设置窗口大小...", self)
        settings_action.triggered.connect(self._on_show_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)
        
        # 设置菜单
        self.tray_icon.setContextMenu(menu)
    
    def _on_tray_icon_activated(self, reason):
        """托盘图标激活事件处理
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左键单击：切换主窗口显示/隐藏
            self._on_show_hide_window()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击：显示主窗口
            self.show_window_requested.emit()
    
    def _on_show_hide_window(self):
        """显示/隐藏主窗口"""
        if self.main_window and self.main_window.isVisible():
            self.hide_window_requested.emit()
        else:
            self.show_window_requested.emit()
    
    def _on_toggle_taskbar_display(self):
        """切换任务栏显示器"""
        self.toggle_taskbar_display_requested.emit()
    
    def _on_toggle_theme(self):
        """切换主题"""
        self.toggle_theme_requested.emit()
    
    def _on_show_settings(self):
        """显示设置对话框"""
        self.show_settings_requested.emit()
    
    def _on_exit(self):
        """退出程序"""
        self.exit_requested.emit()
    
    def update_show_hide_action(self, window_visible: bool):
        """更新显示/隐藏按钮文本
        
        Args:
            window_visible: 主窗口是否可见
        """
        if hasattr(self, 'show_hide_action'):
            self.show_hide_action.setText("隐藏主窗口" if window_visible else "显示主窗口")
    
    def update_taskbar_display_action(self, is_showing: bool):
        """更新任务栏显示器按钮状态
        
        Args:
            is_showing: 任务栏显示器是否正在显示
        """
        if hasattr(self, 'taskbar_display_action'):
            self.taskbar_display_action.setChecked(is_showing)
    
    def update_tooltip(self, tooltip: str):
        """更新托盘图标的工具提示
        
        Args:
            tooltip: 工具提示文本
        """
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
    
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """显示托盘消息
        
        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标类型
        """
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)
    
    def cleanup(self):
        """清理资源"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
    
    def is_available(self) -> bool:
        """检查系统托盘是否可用
        
        Returns:
            bool: 托盘图标是否可用
        """
        return QSystemTrayIcon.isSystemTrayAvailable() and self.tray_icon is not None
