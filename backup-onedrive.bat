@echo off
chcp 65001 >nul
title Claude Code OneDrive 每日备份
setlocal enabledelayedexpansion

set ONEDRIVE=%USERPROFILE%\OneDrive
set BACKUP_DIR=%ONEDRIVE%\ClaudeBackup
set TODAY=%date:~0,10%

echo ========================================
echo   Claude Code OneDrive 每日备份
echo   日期: %TODAY% %time%
echo ========================================
echo.

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: 1. ~/.claude 全局配置
echo [1/4] 全局配置...
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\CLAUDE.md" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\settings.json" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\settings.local.json" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\memory" "%BACKUP_DIR%\全局配置\memory\" >nul
echo       完成 ✅

:: 2. VSteach CLAUDE 配置
echo [2/4] VSteach...
if not exist "%BACKUP_DIR%\VSteach" mkdir "%BACKUP_DIR%\VSteach"
for /r "D:\@VSwork\VSteach" %%f in (CLAUDE.md) do (
    set SRC=%%~dpf
    set REL=!SRC:D:\@VSwork\VSteach=!
    if not exist "%BACKUP_DIR%\VSteach\!REL!" mkdir "%BACKUP_DIR%\VSteach\!REL!"
    copy /Y "%%f" "%BACKUP_DIR%\VSteach\!REL!\" >nul
)

:: 3. VS昭明计划 .claude 配置
echo [3/4] 昭明计划...
xcopy /E /I /Q /Y "D:\@VSwork\VS昭明计划VBA优化\.claude" "%BACKUP_DIR%\昭明计划\.claude\" >nul
copy /Y "D:\@VSwork\VS昭明计划VBA优化\CLAUDE.md" "%BACKUP_DIR%\昭明计划\" >nul

:: 4. Obsidian 学习方法笔记
echo [4/4] Obsidian 笔记...
xcopy /E /I /Q /Y "D:\zdata\MyObsidian\学习方法" "%BACKUP_DIR%\学习方法\" >nul

:: 日志
echo %TODAY% %time% OneDrive 备份完成 >> "%BACKUP_DIR%\backup-log.txt"

echo.
echo ========================================
echo   OneDrive 备份完成！
echo   位置: %BACKUP_DIR%
echo   OneDrive 自动同步到云端 ☁️
echo ========================================