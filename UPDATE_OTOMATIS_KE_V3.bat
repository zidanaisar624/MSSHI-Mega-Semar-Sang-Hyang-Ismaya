@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -B -X utf8 "%~dp0scripts\msshi_cli.py" update --source "%~dp0"
goto done
:usepython
python -B -X utf8 "%~dp0scripts\msshi_cli.py" update --source "%~dp0"
:done
set "msshi_result=%errorlevel%"
if not "%msshi_result%"=="0" echo Update memerlukan perhatian. Baca pesan di atas.
pause
exit /b %msshi_result%
