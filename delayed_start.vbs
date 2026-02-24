' 文献简报启动器 - 等待20分钟后运行
' 放置在 Windows 启动文件夹中

Set WshShell = CreateObject("WScript.Shell")

' 等待20分钟（1200秒），确认用户在工作状态
WScript.Sleep 1200000

' 运行文献简报脚本（隐藏窗口）
WshShell.Run """C:\Users\24377\literature_briefing\run_briefing.bat""", 0, True
