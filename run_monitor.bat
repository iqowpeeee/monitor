@echo off
cd /d "C:\Users\Имя пользователя\Desktop\monitor"

if exist monitor.log (
    for %%A in (monitor.log) do if %%~zA GTR 1000000 (
        move /y monitor.log monitor.log.old
    )
)

"C:\Users\Имя пользователя\AppData\Local\Python\pythoncore-3.14-64\python.exe" monitor.py >> monitor.log 2>&1
