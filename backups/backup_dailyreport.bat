@echo off
setlocal
set "BASE=H:\python note\nippou-project"
set "BACK=%BASE%\backups"
set "DATE=%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2%"

cd /d "%BASE%"
if not exist "%BACK%" mkdir "%BACK%"

REM ここにフルパスを書いて固定
set "PY=C:\Users\pocop\AppData\Local\Programs\Python\Python312\python.exe"

echo Using: %PY% > "%BACK%\last_python.txt" 2>&1
"%PY%" --version >> "%BACK%\last_python.txt" 2>&1

"%PY%" manage.py dumpdata main.DailyReport --indent 2 > "%BACK%\dailyreport_%DATE%.json" 2>> "%BACK%\backup_error.log"
endlocal
