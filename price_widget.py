from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class PriceWidget(QWidget):
    """单个交易对的价格显示组件"""
    
    def __init__(self, symbol: str, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.last_price = 0.0
        self.price_change_rate = 0.0
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 主布局改为水平布局，让所有信息显示在一行
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        
        # 合并的价格信息标签（交易对名 + 价格 + 价格变动值 + 涨跌幅 + 高低 + 开盘价）
        initial_text = f"{self.symbol}  ----.--  +0.00  0.00%  H:----  L:----  O:----"
        self.price_info_label = QLabel(initial_text)
        self.price_info_label.setObjectName("priceInfoLabel")
        self.price_info_label.setMinimumHeight(24)  # 设置最小高度，确保一致性
        self.price_info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 添加到主布局
        layout.addWidget(self.price_info_label)
        layout.addStretch()  # 添加弹性空间
        
        # 分隔线（设置高度为1像素）
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFixedHeight(1)
        
        # 创建主容器，包含分隔线
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.separator)
        main_container.setLayout(main_layout)
        
        # 将主容器设置为当前widget的布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(main_container)
        self.setLayout(container_layout)
    
    def update_price(self, data: dict):
        """更新价格数据
        
        Args:
            data: 价格数据字典，包含以下字段:
                - last_price: 最新价格
                - price_change_amount: 价格变动值
                - price_change_rate: 涨跌幅百分比
                - high: 最高价
                - low: 最低价
                - open_price: 开盘价
        """
        try:
            # 更新最新价格
            self.last_price = float(data.get('last_price', 0))
            
            # 更新价格变动值
            price_change_amount = float(data.get('price_change_amount', 0))
            change_amount_text = f"{'+' if price_change_amount > 0 else ''}{price_change_amount:.2f}"
            
            # 更新涨跌幅
            self.price_change_rate = float(data.get('price_change_rate', 0))
            change_rate_text = f"{'+' if self.price_change_rate > 0 else ''}{self.price_change_rate:.2f}%"
            
            # 更新最高价和最低价
            high = float(data.get('high', 0))
            low = float(data.get('low', 0))
            
            # 更新开盘价
            open_price = float(data.get('open_price', 0))
            
            # 合并所有信息到一个标签（交易对名 + 价格 + 价格变动值 + 涨跌幅 + 高低 + 开盘价）
            price_info = f"{self.symbol}  {self.last_price:.2f}  {change_amount_text}  {change_rate_text}  H:{high:.2f}  L:{low:.2f}  O:{open_price:.2f}"
            self.price_info_label.setText(price_info)
            
            # 更新标签颜色
            self._update_colors()
            
        except (ValueError, TypeError):
            pass
    
    def _update_colors(self):
        """根据涨跌幅更新标签颜色"""
        if self.price_change_rate > 0:
            # 涨
            self.price_info_label.setProperty("up", True)
            self.price_info_label.setProperty("down", False)
        elif self.price_change_rate < 0:
            # 跌
            self.price_info_label.setProperty("up", False)
            self.price_info_label.setProperty("down", True)
        else:
            # 平
            self.price_info_label.setProperty("up", False)
            self.price_info_label.setProperty("down", False)
        
        # 强制更新样式
        self.price_info_label.style().unpolish(self.price_info_label)
        self.price_info_label.style().polish(self.price_info_label)
