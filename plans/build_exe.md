# Gate Price Tracker - EXE 打包方案

## 概述

本文档描述了如何将 Gate Price Tracker 项目打包成单个可执行的 EXE 文件，便于分发和使用。

## 打包方案

### 选择的工具：PyInstaller

**选择理由：**
- 成熟稳定，社区活跃
- 支持单文件打包 (--onefile)
- 对 PyQt6 支持良好
- 配置灵活，可自定义性强

### 打包策略

- **单文件模式**：所有依赖打包到一个 EXE 文件中
- **无控制台窗口**：GUI 应用，不显示命令行
- **UPX 压缩**：减小文件体积
- **排除不需要的模块**：进一步优化体积

## 文件准备

### 1. PyInstaller 配置文件 (gate_tracker.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for Gate Price Tracker
# 使用方法: pyinstaller gate_tracker.spec

import sys
from pathlib import Path

block_cipher = None

# 收集所有 PyQt6 相关插件和资源
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 如果有其他资源文件需要打包，可以在这里添加
        # ('资源文件路径', '目标路径'),
    ],
    hiddenimports=[
        # PyQt6 相关隐藏导入
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # PyWin32 相关
        'pywin32',
        'win32gui',
        'win32con',
        'win32api',
        'win32clipboard',
        # WebSocket 客户端
        'websocket',
        'websocket-client',
        # 其他可能需要的模块
        'json',
        'threading',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GatePriceTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # 打包成单个文件
    icon=None,  # 可以在这里指定图标文件路径，如: 'icon.ico'
)
```

### 2. 更新的 requirements.txt

```
PyQt6>=6.5.0
websocket-client>=1.6.0
pywin32>=306
pyinstaller>=6.0.0
```

### 3. 打包脚本 (build.bat)

```batch
@echo off
REM Gate Price Tracker 打包脚本
REM 使用方法: 双击运行 build.bat

echo ========================================
echo   Gate Price Tracker - EXE 打包工具
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo [信息] 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo [信息] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

REM 清理旧的构建文件
echo [信息] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 执行打包
echo [信息] 开始打包...
echo.
pyinstaller gate_tracker.spec
if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请查看上方错误信息
    pause
    exit /b 1
)

REM 检查结果
echo.
if exist "dist\GatePriceTracker.exe" (
    echo ========================================
    echo [成功] 打包完成！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\GatePriceTracker.exe
    echo.
    
    REM 显示文件大小
    for %%I in (dist\GatePriceTracker.exe) do echo 文件大小: %%~zI 字节
    echo.
    echo 您可以直接运行 dist\GatePriceTracker.exe 进行测试
) else (
    echo [错误] 未找到生成的 exe 文件
    pause
    exit /b 1
)

echo.
pause
```

### 4. 清理脚本 (clean.bat)

```batch
@echo off
REM 清理打包生成的文件

echo 正在清理打包文件...

if exist "build" (
    echo 删除 build 目录...
    rmdir /s /q build
)

if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q dist
)

if exist "*.spec" (
    echo 删除 spec 文件...
    del /q *.spec
)

## 打包流程图

```mermaid
graph TD
    A[开始打包] --> B[检查 Python 环境]
    B --> C[创建/激活虚拟环境]
    C --> D[安装依赖包]
    D --> E[清理旧构建文件]
    E --> F[运行 PyInstaller]
)
```

**简单命令行方式：**

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 执行打包
pyinstaller gate_tracker.spec

# 3. 生成的 exe 文件在 dist 目录下
dist\GatePriceTracker.exe
```

## 生成的文件结构

```
gateTracker/
├── main.py
├── window.py
├── ws_client.py
├── price_widget.py
├── theme_manager.py
├── system_tray.py
├── taskbar_display.py
├── requirements.txt
├── gate_tracker.spec      # PyInstaller 配置文件
├── build.bat              # 打包脚本
├── clean.bat              # 清理脚本
├── build/                 # 构建临时文件（可删除）
│   └── GatePriceTracker/
└── dist/                  # 最终输出目录
    └── GatePriceTracker.exe  # 最终的 exe 文件
```

## 预估文件大小

- **不使用 UPX 压缩**：约 60-80 MB
- **使用 UPX 压缩**：约 40-60 MB
- **因素**：PyQt6 本身较大，包含所有必要的 Qt 库和插件

## 可选优化

### 1. 添加自定义图标

准备一个 `.ico` 格式的图标文件，然后修改 `gate_tracker.spec`：

```python
exe = EXE(
    # ... 其他参数 ...
    icon='icon.ico',  # 指定图标文件
    # ...
)
```

### 2. 添加版本信息

创建 `version_info.txt` 文件：

```text
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'GateTracker'),
        StringStruct(u'FileDescription', u'Gate Price Tracker - Real-time Price Display'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'GatePriceTracker'),
        StringStruct(u'LegalCopyright', u'Copyright 2024'),
        StringStruct(u'OriginalFilename', u'GatePriceTracker.exe'),
        StringStruct(u'ProductName', u'Gate Price Tracker'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

然后在 spec 文件中使用：

```python
exe = EXE(
    # ... 其他参数 ...
    version='version_info.txt',
    # ...
)
```

## 常见问题

### 问题 1：打包后运行闪退

**原因**：缺少某些隐藏导入或资源文件

**解决方法**：
1. 在 spec 文件的 `hiddenimports` 中添加缺失的模块
2. 使用 `--debug` 参数重新打包查看详细日志
3. 检查是否有资源文件未正确打包

### 问题 2：PyQt6 相关错误

**解决方法**：
```bash
# 使用 PyQt6 官方 hooks
pip install pyinstaller-hooks-contrib
```

然后在 spec 文件中添加：
```python
hookspath=['path/to/pyinstaller_hooks_contrib'],
```

### 问题 3：WebSocket 连接失败

**原因**：可能是防火墙或网络相关

**解决方法**：
- 检查网络连接
- 确认防火墙允许程序访问网络
- 测试时可以使用 console=True 查看错误信息

### 问题 4：文件太大

**优化方法**：
1. 确保启用了 UPX 压缩
2. 排除不需要的模块（已在 spec 中配置）
3. 考虑使用 --onedir 模式生成文件夹，再手动压缩

## 测试清单

打包完成后，请进行以下测试：

- [ ] EXE 文件可以正常启动
- [ ] 主窗口正常显示
- [ ] 系统托盘图标正常显示
- [ ] WebSocket 连接成功，价格更新正常
- [ ] 深色/浅色主题切换正常
- [ ] 窗口拖动和大小调整正常
- [ ] 配置保存和加载正常
- [ ] 任务栏显示器功能正常（如果启用）
- [ ] 关闭按钮正常隐藏到托盘
- [ ] 托盘菜单退出功能正常
- [ ] 在没有 Python 环境的电脑上运行正常

## 分发说明

生成的 `GatePriceTracker.exe` 是一个独立的可执行文件，可以直接分发：

1. 将 `dist/GatePriceTracker.exe` 复制到目标电脑
2. 双击运行即可，无需安装 Python 或其他依赖
3. 首次运行会生成 `user_config.json` 配置文件

## 参考资源

- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)
- [PyQt6 打包指南](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyInstaller spec 文件格式](https://pyinstaller.org/en/stable/spec-files.html)
