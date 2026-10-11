' Task Scheduler launcher: runs order_watch.py without a console window (same log file as before)
Set sh = CreateObject("WScript.Shell")
dir = "C:\path\to\homelivingclub-automation"
sh.CurrentDirectory = dir
cmd = "cmd.exe /c """"C:\path\to\python.exe"" -X utf8 """ & dir & "\order_watch.py"" >> """ & dir & "\output\order_watch_task.log"" 2>&1"""
WScript.Quit sh.Run(cmd, 0, True)
