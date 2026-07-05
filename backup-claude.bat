@echo off
chcp 65001 >nul
title Claude Code 全自动备份
setlocal enabledelayedexpansion

set ONEDRIVE=%USERPROFILE%\OneDrive
set BACKUP_DIR=%ONEDRIVE%\ClaudeBackup
set TODAY=%date:~0,10%
set LOG=%BACKUP_DIR%\backup-log.txt

echo ========================================
echo   Claude Code 全自动备份
echo   日期: %TODAY% %time%
echo   模式: 全部备份
echo ========================================
echo.

:: 创建备份目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: ==========================================
:: 第一部分：GitHub 备份
:: ==========================================
echo [GitHub 备份]
echo ---------------

:: 1. ~/.claude 全局配置 → sharkeyang/claude-config
echo  ① 全局配置     (claude-config)...
cd /d "%USERPROFILE%\.claude"
git add -A >nul 2>&1
git commit -m "auto-backup %TODAY%" >nul 2>&1
git push 2>&1 | findstr /V "Everything up-to-date"
if %errorlevel%==0 (echo       完成 ✅) else (echo       无变更 ⏭️)

:: 2. VSteach → claude-VSteach
echo  ② VSteach      (claude-VSteach)...
cd /d "D:\@VSwork\VSteach"
git add -A >nul 2>&1
git commit -m "auto-backup %TODAY%" >nul 2>&1
git push 2>&1 | findstr /V "Everything up-to-date"
if %errorlevel%==0 (echo       完成 ✅) else (echo       无变更 ⏭️)

:: 3. VS昭明计划 → claude-VSzhaoming
echo  ③ 昭明计划     (claude-VSzhaoming)...
cd /d "D:\@VSwork\VS昭明计划VBA优化"
git add -A >nul 2>&1
git commit -m "auto-backup %TODAY%" >nul 2>&1
git push 2>&1 | findstr /V "Everything up-to-date"
if %errorlevel%==0 (echo       完成 ✅) else (echo       无变更 ⏭️)

echo.

:: ==========================================
:: 第二部分：OneDrive 本地备份
:: ==========================================
echo [OneDrive 本地备份]
echo -------------------

:: 1. ~/.claude 全局配置
echo  ① 全局配置...
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\CLAUDE.md" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\settings.json" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\settings.local.json" "%BACKUP_DIR%\全局配置\" >nul
xcopy /E /I /Q /Y "%USERPROFILE%\.claude\memory" "%BACKUP_DIR%\全局配置\memory\" >nul
echo       完成 ✅

:: 2. VSteach CLAUDE 配置
echo  ② VSteach...
if not exist "%BACKUP_DIR%\VSteach" mkdir "%BACKUP_DIR%\VSteach"
for /r "D:\@VSwork\VSteach" %%f in (CLAUDE.md) do (
    set SRC=%%~dpf
    set REL=!SRC:D:\@VSwork\VSteach=!
    if not exist "%BACKUP_DIR%\VSteach\!REL!" mkdir "%BACKUP_DIR%\VSteach\!REL!"
    copy /Y "%%f" "%BACKUP_DIR%\VSteach\!REL!\" >nul
)
copy /Y "D:\@VSwork\VSteach\.gitignore" "%BACKUP_DIR%\VSteach\" >nul
copy /Y "D:\@VSwork\VSteach\skills-lock.json" "%BACKUP_DIR%\VSteach\" >nul
copy /Y "D:\@VSwork\VSteach\学习方法skill.md" "%BACKUP_DIR%\VSteach\" >nul
copy /Y "D:\@VSwork\VSteach\backup-claude.bat" "%BACKUP_DIR%\VSteach\" >nul
echo       完成 ✅

:: 3. VS昭明计划 .claude 配置
echo  ③ 昭明计划...
xcopy /E /I /Q /Y "D:\@VSwork\VS昭明计划VBA优化\.claude" "%BACKUP_DIR%\昭明计划\.claude\" >nul
copy /Y "D:\@VSwork\VS昭明计划VBA优化\CLAUDE.md" "%BACKUP_DIR%\昭明计划\" >nul
copy /Y "D:\@VSwork\VS昭明计划VBA优化\.gitignore" "%BACKUP_DIR%\昭明计划\" >nul
copy /Y "D:\@VSwork\VSteach\backup-claude.bat" "%BACKUP_DIR%\昭明计划\" >nul
echo       完成 ✅

:: 4. Obsidian 学习笔记
echo  ④ Obsidian 学习方法笔记...
xcopy /E /I /Q /Y "D:\zdata\MyObsidian\学习方法" "%BACKUP_DIR%\学习方法\" >nul
echo       完成 ✅

:: 写入日志
echo %TODAY% %time% 备份完成 >> "%LOG%"

echo.
echo ========================================
echo   全部备份完成！
echo   备份位置: %BACKUP_DIR%
echo   OneDrive 自动同步到云端 ☁️
echo ========================================
echo.
pause