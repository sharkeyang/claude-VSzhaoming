@echo off
chcp 65001 >nul
title Claude Code 计划任务安装

echo ========================================
echo   Claude Code 自动备份计划任务安装
echo ========================================
echo.
echo 需要管理员权限运行！
echo 请右键 → "以管理员身份运行"
echo.
pause

:: 检查是否管理员
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 权限不足！请以管理员身份运行。
    pause
    exit /b 1
)

set SCRIPT_DIR=D:\@VSwork\VSteach

echo.
echo 正在创建计划任务...
echo.

:: ====== 任务 1：每日 OneDrive 备份（每天 18:00）======
schtasks /Create /TN "ClaudeCode\OneDrive备份" /TR "%SCRIPT_DIR%\backup-onedrive.bat" /SC DAILY /ST 18:00 /F
if %errorlevel% equ 0 (
    echo [1/2] ✅ 每日 OneDrive 备份 → 每天 18:00
) else (
    echo [1/2] ❌ 创建失败
)

:: ====== 任务 2：每周 GitHub 备份（周六 10:00）======
schtasks /Create /TN "ClaudeCode\GitHub备份" /TR "%SCRIPT_DIR%\backup-claude.bat" /SC WEEKLY /D SAT /ST 10:00 /F
if %errorlevel% equ 0 (
    echo [2/2] ✅ 每周 GitHub 备份 → 周六 10:00
) else (
    echo [2/2] ❌ 创建失败
)

echo.
echo ========================================
echo   计划任务安装完成！
echo.
echo   每日 18:00 → OneDrive 自动备份
echo   周六 10:00 → GitHub + OneDrive 全量备份
echo.
echo   在任务计划程序库中可以查看和管理：
echo     → Microsoft\Windows\ClaudeCode\
echo ========================================
echo.
pause