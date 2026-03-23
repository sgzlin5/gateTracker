# Gate Price Tracker - EXE 打包指南

本指南说明如何将 Gate Price Tracker 项目打包成独立的可执行文件（EXE）。

## 快速开始

### 方法一：使用快速打包脚本（推荐）

如果您已经安装了 Python 和项目依赖：

```bash
# 双击运行或在命令行执行：
quick_build.bat
```

这个脚本会：
- 检查并安装 PyInstaller
- 清理旧的构建文件
- 执行打包
- 显示生成的 exe 文件信息

### 方法二：使用完整打包脚本

如果您想要创建独立的虚拟环境：

```bash
# 双击运行或在命令行执行：
build.bat
```

这个脚本会：
- 创建独立的 Python 虚拟环境
- 安装所有依赖
- 执行打包
- 显示生成的 exe 文件信息

### 方法三：命令行手动打包

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 执行打包
pyinstaller gate_tracker.spec

# 3. 生成的 exe 文件在 dist 目录
dist\GatePriceTracker.exe
```

## 打包文件说明

| 文件 | 说明 |
|------|------|
| [`gate_tracker.spec`](gate_tracker.spec:1) | PyInstaller 配置文件，定义打包参数 |
| [`build.bat`](build.bat:1) | 完整打包脚本（创建虚拟环境） |
| [`quick_build.bat`](quick_build.bat:1) | 快速打包脚本（使用当前环境） |
| [`clean.bat`](clean.bat:1) | 清理构建文件的脚本 |

## 生成的文件

打包成功后，会生成以下目录和文件：

```
gateTracker/
├── build/              # 构建临时文件（可删除）
│   └── GatePriceTracker/
└── dist/               # 最终输出目录
    └── GatePriceTracker.exe  # 最终的 exe 文件（（约 40-60 MB）
```

## 清理构建文件

如果需要清理打包生成的临时文件：

```bash
# 双击运行或在命令行执行：
clean.bat
```

或手动删除 `build` 和 `dist` 目录。

## 打包配置说明

### 主要配置参数

在 [`gate_tracker.spec`](gate_tracker.spec:1) 中：

- **onefile=True**：打包成单个 exe 文件
- **console=False**：不显示控制台窗口（纯 GUI 应用）
- **upx=True**：启用 UPX 压缩以减小文件大小
- **name='GatePriceTracker'**：生成的 exe 文件名

### 隐藏导入

配置中包含了以下隐藏导入，确保所有依赖正确打包：

- PyQt6 模块（QtCore, QtGui, QtWidgets）
- PyWin32 模块（win32gui, win32con 等）
- WebSocket 客户端

### 排除模块

为了减小文件大小，排除了不需要的模块：
- tkinter
- matplotlib
- pandas
- numpy
- scipy

## 自定义配置

### 添加自定义图标

准备一个 `.ico` 格式的图标文件，然后修改 [`gate_tracker.spec`](gate_tracker.spec:1)：

```python
exe = EXE(
    # ... 其他参数 ...
    icon='icon.ico',  # 指定图标文件
    # ...
)
```

### 添加版本信息

创建 `version_info.txt` 文件（详细格式请参考 [`plans/build_exe.md`](plans/build_exe.md:1)），然后在 spec 文件中使用：

```python
exe = EXE(
    # ... 其他参数 ...
    version='version_info.txt',
    # ...
)
```

## 测试打包结果

打包完成后，请进行以下测试：

1. **基本功能**
   - [ ] EXE 文件可以正常启动
   - [ ] 主窗口正常显示
   - [ ] 系统托盘图标正常显示

2. **价格功能**
   - [ ] WebSocket 连接成功
   - [ ] 价格数据实时更新
   - [ ] 涨跌颜色正确显示

3. **界面功能**
   - [ ] 深色/浅色主题切换正常
   - [ ] 窗口拖动和大小调整正常
   - [ ] 窗口位置和大小保存正常

4. **系统托盘**
   - [ ] 点击关闭按钮隐藏到托盘
   - [ ] 托盘菜单功能正常
   - [ ] 托盘退出功能正常

5. **任务栏显示器**（如果启用）
   - [ ] 任务栏显示器正常显示
   - [ ] 价格信息正确更新

## 分发说明

生成的 `GatePriceTracker.exe` 是一个独立的可执行文件，可以：

1. 直接复制到任何 Windows 10/11 电脑
2. 双击运行，无需安装 Python 或其他依赖
3. 首次运行会自动生成 `user_config.json` 配置文件

## 故障排除

### 问题 1：打包后运行闪退

**可能原因**：缺少某些隐藏导入或资源文件

**解决方法**：
```bash
# 使用 console=True 查看错误信息
# 修改 gate_tracker.spec 中的 console=False 为 console=True
# 重新打包并运行，查看控制台输出
```

### 问题 2：PyQt6 相关错误

**解决方法**：
```bash
pip install pyinstaller-hooks-contrib
```

然后在 [`gate_tracker.spec`](gate_tracker.spec:1) 中添加 hooks 路径。

### 问题 3：文件过大

**优化方法**：
1. 确保 UPX 压缩已启用
2. 排除不需要的模块
3. 检查是否有重复的依赖

### 问题 4：网络连接失败

**解决方法**：
- 检查防火墙设置
- 确认网络连接正常
- 使用 console=True 查看详细错误

## 技术文档

详细的技术文档、架构设计和高级配置选项，请参考：

- [`plans/build_exe.md`](plans/build_exe.md:1) - 完整打包方案文档
- [`README.md`](README.md:1) - 项目使用说明
- [`plans/architecture.md`](plans/architecture.md:1) - 架构设计文档

## 打包参数对比

| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| onefile (当前) | 单个 exe 文文件 | 分发方便，一个文件 | 启动稍慢，运行时解压 |
| onedir | exe + 依赖文件夹 | 启动快，无需解压 | 需要整个文件夹 |

当前配置使用 onefile 模式，适合分发。

## 性能参考

- **文件大小**：约 40-60 MB
- **首次启动时间**：3-5 秒（解压时间）
- **内存占用**：约 50-80 MB
- **CPU 占用**：空闲时 < 1%

## 许可证

打包生成的 EXE 文件仅供学习和个人使用。

---

如有问题或需要帮助，请查看完整文档或联系开发者。
