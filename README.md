# Gate Price Tracker

一个实时显示 XAUUSD 和 NAS100 价格的 Windows 桌面浮窗工具。

## 功能特性

- ✅ 实时价格显示（XAUUSD 和 NAS100）
- ✅ 窗口可拖动
- ✅ 支持自定义窗口大小
- ✅ 深色/浅色主题切换
- ✅ 涨跌颜色标识（绿色涨、红色跌）
- ✅ 窗口位置和大小自动保存
- ✅ 主题偏好自动保存
- ✅ 始终置顶选项（可开关）
- ✅ 横向布局显示（单行显示所有信息）
- ✅ 系统托盘图标支持
- ✅ 关闭窗口后隐藏到托盘而非退出
- ✅ 任务栏嵌入式显示器

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install PyQt6 websocket-client
```

### 2. 运行程序

```bash
python main.py
```

## 使用窗口操作

### 窗口操作

- **拖动窗口**: 鼠标左键按住窗口任意位置拖动
- **右键菜单**: 右键点击窗口显示菜单
- **设置窗口大小**: 右键菜单 → 设置窗口大小...
- **切换主题**: 右键菜单 → 切换主题 (或按 Ctrl+T)
- **退出程序**: 右键菜单 → 退出 (或按 Ctrl+Q)
- **关闭窗口**: 点击关闭按钮（X）会将窗口隐藏到系统托盘

### 系统托盘操作

程序启动后会在系统托盘区域显示图标，提供便捷的操作方式：

- **左键单击**: 显示/隐藏主窗口
- **双击**: 显示主窗口并激活
- **右键菜单**: 访问所有程序功能
  - 显示/隐藏主窗口
  - 显示任务栏显示器
  - 切换主题
  - 设置窗口大小...
  - 退出（完全退出程序）

**重要提示**: 关闭主窗口时程序不会退出，而是隐藏到系统托盘。要完全退出程序，请使用托盘右键菜单的"退出"选项。

### 任务栏嵌入式显示器

通过右键菜单（主窗口或托盘图标）可以启用任务栏嵌入式显示器：

- **启用**: 右键菜单 → 勾选"显示任务栏显示器"
- **禁用**: 右键菜单 → 取消勾选"显示任务栏显示器"

启用后，价格信息会以紧凑形式显示在系统任务栏附近，主窗口会自动最小化。

详细信息请查看 [TASKBAR_DISPLAY_README.md](TASKBAR_DISPLAY_README.md)
~~### 快捷键~~

~~| 快捷键 | 功能 |~~
~~|--------|------|~~
~~| Ctrl+T | 切换深色/浅色主题 |~~
~~| Ctrl+Q | 退出程序 |~~

### 主题

- **深色主题**: 黑色背景，适合夜间使用
- **浅色主题**: 白色背景，适合白天使用

主题选择会自动保存，下次启动时自动应用。

## 配置文件

程序会在运行目录生成 `user_config.json` 配置文件：

```json
{
    "window": {
        "width": 300,
        "height": 250,
        "always_on_top": true,
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
```

## 文件结构

```
gateTracker/
├── main.py                 # 程序启动入口
├── window.py               # 主窗口类
├── ws_client.py            # WebSocket客户端
├── price_widget.py         # 价格显示组件
├── theme_manager.py        # 主题管理器
├── system_tray.py          # 系统托盘控制器
├── taskbar_display.py      # 任务栏嵌入式显示器
├── requirements.txt        # 依赖包列表
├── demo.py                 # 原始WebSocket demo
├── user_config.json        # 用户配置（自动生成）
├── README.md               # 本文档
├── SYSTEM_TRAY_README.md   # 系统托盘功能说明
├── TASKBAR_DISPLAY_README.md # 任务栏显示器功能说明
└── plans/
    └── architecture.md     # 架构设计文档
```

## 技术栈

- **GUI框架**: PyQt6
- **WebSocket**: websocket-client
- **主题管理**: QSS样式表

## 系统要求

- Python 3.8+
- Windows 10/11
- 网络连接（用于接收实时价格数据）

## 注意事项

1. 确保网络连接正常，否则无法获取实时价格
2. 首次运行会使用默认设置，可根据需要调整
3. 窗口始终保持在最上层，不会被其他窗口遮挡

## 故障排除

### 程序无法启动

- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 确保Python版本 >= 3.8

### 无法连接WebSocket

- 检查网络连接
- 检查防火墙设置
- 确认Gate.io服务是否正常运行

### 窗口显示异常

- 尝试删除 `user_config.json` 后重新运行
- 检查系统主题和语言设置

## 开发

查看架构设计文档了解详细设计：

```bash
cat plans/architecture.md
```

## 许可证

本项目仅供学习和个人使用。
