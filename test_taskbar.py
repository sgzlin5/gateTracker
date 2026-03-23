"""测试任务栏显示功能

这个脚本用于测试任务栏嵌入式价格显示器的功能。
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from taskbar_display import TaskbarDisplayController


class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("任务栏显示测试")
        self.setGeometry(100, 100, 300, 200)
        
        # 创建任务栏显示器
        self.taskbar_display = TaskbarDisplayController(["XAUUSD", "NAS100"])
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 显示任务栏显示器按钮
        show_button = QPushButton("显示任务栏显示器")
        show_button.clicked.connect(self.taskbar_display.show)
        layout.addWidget(show_button)
        
        # 隐藏任务栏显示器按钮
        hide_button = QPushButton("隐藏任务栏显示器")
        hide_button.clicked.connect(self.taskbar_display.hide)
        layout.addWidget(hide_button)
        
        # 切换按钮
        toggle_button = QPushButton("切换任务栏显示器")
        toggle_button.clicked.connect(self.taskbar_display.toggle)
        layout.addWidget(toggle_button)
        
        # 更新价格按钮
        update_button = QPushButton("更新价格数据")
        update_button.clicked.connect(self._update_prices)
        layout.addWidget(update_button)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def _update_prices(self):
        """更新测试价格数据"""
        # 模拟XAUUSD价格更新
        import random
        gold_price = 2300 + random.random() * 100
        gold_change = (random.random() - 0.5) * 10
        
        self.taskbar_display.update_price("XAUUSD", {
            'last_price': gold_price,
            'price_change_rate': gold_change,
            'price_change_amount': gold_change * 100
        })
        
        # 模拟NAS100价格更新
        nas_price = 18900 + random.random() * 500
        nas_change = (random.random() - 0.5) * 50
        
        self.taskbar_display.update_price("NAS100", {
            'last_price': nas_price,
            'price_change_rate': nas_change,
            'price_change_amount': nas_change * 1000
        })
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.taskbar_display.cleanup()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
