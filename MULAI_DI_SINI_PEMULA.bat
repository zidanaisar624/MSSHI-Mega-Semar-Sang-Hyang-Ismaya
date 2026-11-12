@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
echo MSSHI v3.0
echo 1. Pasang skill dan pilih nama bot
echo 2. Migrasi Hermes yang sudah ada
echo 3. Buka Hermes Desktop
echo 4. Periksa hasil instalasi
choice /c 1234 /n /m "Pilih 1-4: "
if errorlevel 4 goto audit
if errorlevel 3 goto desktop
if errorlevel 2 goto migrate
set "msshi_action=setup"
goto run
:audit
set "msshi_action=audit"
goto run
:desktop
set "msshi_action=desktop"
goto run
:migrate
set "msshi_action=runtime migrate"
:run
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -B -X utf8 "%~dp0scripts\msshi_cli.py" %msshi_action%
goto done
:usepython
python -B -X utf8 "%~dp0scripts\msshi_cli.py" %msshi_action%
:done
set "msshi_result=%errorlevel%"
pause
exit /b %msshi_result%
