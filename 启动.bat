@echo off
chcp 65001 >nul
title 霖蛋 AI助手

echo.
echo ╔════════════════════════════╗
echo ║     🥚 霖蛋 AI 助手       ║
echo ╚════════════════════════════╝
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 没有找到 Python，请先安装 Python
    echo    下载地址: https://www.python.org/downloads/
    echo    安装时记得勾选 "Add Python to PATH"
    pause
    exit /b
)

:: 防火墙放行（需要管理员权限）
echo 🔓 正在配置防火墙...
netsh advfirewall firewall add rule name="霖蛋助手" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo    防火墙 ✓
) else (
    echo    防火墙未配置（可能需要管理员运行）
)

:: 安装依赖
echo 📦 正在检查依赖...
pip install flask requests -q 2>&1

:: 获取本机 IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set IP=%%a
set IP=%IP: =%

:: 启动
echo.
echo ════════════════════════════════════
echo   🚀 霖蛋已启动！
echo.
echo   电脑浏览器打开:
echo   → http://localhost:5000
echo.
echo   手机浏览器打开:
echo   → http://%IP%:5000
echo.
echo   按 Ctrl+C 可以关闭
echo ════════════════════════════════════
echo.

python app.py
pause
