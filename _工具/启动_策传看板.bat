@echo off
title 昭明计划 · 策传看板
chcp 936 >nul
cd /d "%~dp0\.."
echo ==========================================
echo   昭明计划 · 策传看板 启动器
echo ==========================================
echo.
echo 启动条件：
echo   1. Excel 已打开昭明计划VS优化.xlsm
echo   2. 已安装 pywin32（pip install pywin32）
echo.
echo VBA数据源：IQQQ乾坤分布调程花天sSCC_仓宝合
echo   从花天源头获取持仓 - 写入Z sheet - 追加核心指数
echo.
echo 每60秒刷新HTML | 每180秒调用VBA源头刷新
echo 浏览器打开 http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 停止刷新
echo.
pause
python "_产出物\MC3_策传_看板.py"
pause