@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 运行文献简报
python -m literature_briefing.main %*

:: 如果出错，暂停显示错误信息
if errorlevel 1 (
    echo.
    echo [错误] 脚本运行失败，请检查 briefing.log
    pause
)
