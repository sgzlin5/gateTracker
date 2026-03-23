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
