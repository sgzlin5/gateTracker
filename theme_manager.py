import json
import os
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    """主题管理器，负责主题样式管理和切换"""
    
    CONFIG_FILE = "user_config.json"
    
    def __init__(self):
        self.current_theme = self._load_user_preference()
        self.stylesheets = {
            "dark": self._get_dark_stylesheet(),
            "light": self._get_light_stylesheet()
        }
    
    def _load_user_preference(self):
        """加载用户主题偏好"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('theme', {}).get('current', 'dark')
        except Exception as e:
            print(f"加载主题偏好失败: {e}")
        return 'dark'
    
    def _save_user_preference(self):
        """保存用户主题偏好"""
        try:
            config = {}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['theme'] = config.get('theme', {})
            config['theme']['current'] = self.current_theme
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存主题偏好失败: {e}")
    
    def get_stylesheet(self, theme=None):
        """获取指定主题的样式表"""
        if theme is None:
            theme = self.current_theme
        return self.stylesheets.get(theme, self.stylesheets['dark'])
    
    def toggle(self):
        """切换主题并返回新主题"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self._save_user_preference()
        return self.current_theme
    
    def get_current_theme(self):
        """获取当前主题名称"""
        return self.current_theme
    
    def _get_dark_stylesheet(self):
        """获取深色主题样式表"""
        return """
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 12px;
            }
            
            QMainWindow {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            
            QLabel#symbolLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#symbolLabel[up="true"] {
                color: #00ff00;
            }
            QLabel#symbolLabel[down="true"] {
                color: #ff4444;
            }
            
            QLabel#priceLabel {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#priceLabel[up="true"] {
                color: #00ff00;
            }
            QLabel#priceLabel[down="true"] {
                color: #ff4444;
            }
            
            QLabel#changeLabel {
                font-size: 12px;
                color: #aaaaaa;
            }
            QLabel#changeLabel[up="true"] {
                color: #00ff00;
                font-weight: bold;
            }
            QLabel#changeLabel[down="true"] {
                color: #ff4444;
                font-weight: bold;
            }
            
            QLabel#infoLabel {
                font-size: 10px;
                color: #888888;
            }
            
            QFrame#separator {
                background-color: #333333;
                max-height: 1px;
            }
            
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #444444;
            }
            
            QMenu::item {
                background-color: transparent;
                color: #e0e0e0;
                padding: 5px 20px;
            }
            
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            
            QMenu::separator {
                background-color: #444444;
                height: 1px;
            }
        """
    
    def _get_light_stylesheet(self):
        """获取浅色主题样式表"""
        return """
            QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 12px;
            }
            
            QMainWindow {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }
            
            QLabel {
                color: #333333;
                background-color: transparent;
            }
            
            QLabel#symbolLabel {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
            }
            QLabel#symbolLabel[up="true"] {
                color: #00aa00;
            }
            QLabel#symbolLabel[down="true"] {
                color: #cc0000;
            }
            
            QLabel#priceLabel {
                font-size: 20px;
                font-weight: bold;
                color: #000000;
            }
            QLabel#priceLabel[up="true"] {
                color: #00aa00;
            }
            QLabel#priceLabel[down="true"] {
                color: #cc0000;
            }
            
            QLabel#changeLabel {
                font-size: 12px;
                color: #666666;
            }
            QLabel#changeLabel[up="true"] {
                color: #00aa00;
                font-weight: bold;
            }
            QLabel#changeLabel[down="true"] {
                color: #cc0000;
                font-weight: bold;
            }
            
            QLabel#infoLabel {
                font-size: 10px;
                color: #999999;
            }
            
            QFrame#separator {
                background-color: #eeeeee;
                max-height: 1px;
            }
            
            QMenu {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
            }
            
            QMenu::item {
                background-color: transparent;
                color: #333333;
                padding: 5px 20px;
            }
            
            QMenu::item:selected {
                background-color: #e8e8e8;
            }
            
            QMenu::separator {
                background-color: #e0e0e0;
                height: 1px;
            }
        """
