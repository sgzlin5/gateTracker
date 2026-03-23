import sys
from PyQt6.QtWidgets import QApplication
from window import PriceWindow

def main():
    """主函数，应用程序入口"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序名称
    app.setApplicationName("Gate Price Tracker")
    app.setOrganizationName("GateTracker")
    
    # 创建并显示主窗口
    window = PriceWindow()
    window.show()
    
    # 启动事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
