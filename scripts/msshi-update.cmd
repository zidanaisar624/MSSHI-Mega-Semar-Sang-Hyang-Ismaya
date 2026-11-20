@echo off
setlocal
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -B -X utf8 "%~dp0msshi_update.py" %*
    exit /b %errorlevel%
)
python -B -X utf8 "%~dp0msshi_update.py" %*
exit /b %errorlevel%
