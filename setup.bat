@echo off
chcp 65001 >nul
echo ============================================
echo   文献简报 - 安装与配置
echo ============================================
echo.

:: 1. 安装 Python 依赖
echo [1/3] 安装 Python 依赖...
python -m pip install -q -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [错误] Python 依赖安装失败
    pause
    exit /b 1
)
echo       依赖安装完成。
echo.

:: 2. 初始化配置文件
if not exist "%~dp0config.json" (
    echo [2/3] 创建配置文件...
    copy "%~dp0config.template.json" "%~dp0config.json" >nul
    echo       已从模板创建 config.json，请编辑填入 API Key。
) else (
    echo [2/3] 配置文件已存在，跳过。
)
echo.

:: 3. 创建 Windows 任务计划
echo [3/3] 创建任务计划（登录后延迟20分钟执行）...
schtasks /create /tn "LiteratureBriefing" /tr "\"%~dp0run_briefing.bat\"" /sc onlogon /delay 0020:00 /f /rl limited
if errorlevel 1 (
    echo [错误] 任务计划创建失败，请尝试以管理员身份运行此脚本
    pause
    exit /b 1
)
echo       任务计划创建成功！
echo.

echo ============================================
echo   安装完成！
echo   - 每次登录后20分钟自动运行
echo   - 手动运行: run_briefing.bat
echo   - 打开设置: run_settings.bat
echo   - 日志文件: briefing.log
echo ============================================
pause
