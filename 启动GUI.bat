@echo off
chcp 65001 >nul
title 小红书爬虫GUI

echo ========================================
echo   小红书爬虫GUI启动器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] Python版本:
python --version
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [信息] 检测到虚拟环境，正在激活...
    call .venv\Scripts\activate.bat
    echo.
)

REM 检查依赖
echo [信息] 检查依赖包...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [警告] tkinter未安装，GUI可能无法运行
    echo.
)

REM 启动GUI
echo [信息] 启动GUI...
echo.
python gui_main.py

if errorlevel 1 (
    echo.
    echo [错误] GUI启动失败
    echo.
    pause
)
