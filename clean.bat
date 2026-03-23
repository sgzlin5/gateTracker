@echo off
REM 清理打包生成的文件

echo ========================================
echo   Gate Price Tracker - 清理构建文件
echo ========================================
echo.

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

echo.
echo ========================================
echo [完成] 清理完成！
echo ========================================
echo.

pause
