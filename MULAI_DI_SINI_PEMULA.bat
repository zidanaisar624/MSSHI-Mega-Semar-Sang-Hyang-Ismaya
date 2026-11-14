@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
echo ======================================================
echo   MSSHI v3.1.0 - Sovereign Sage & Ultimate Optimizer
echo ======================================================
echo 1. Pasang skill dan pilih nama bot (+ opsi unduh PDF)
echo 2. Migrasi Hermes yang sudah ada
echo 3. Buka Hermes Desktop
echo 4. Periksa hasil instalasi
echo 5. Unduh Buku Panduan PDF Lengkap (v3.1.0 / v3.0)
choice /c 12345 /n /m "Pilih 1-5: "
if errorlevel 5 goto pdfmanual
if errorlevel 4 goto audit
if errorlevel 3 goto desktop
if errorlevel 2 goto migrate
set "msshi_action=setup"
goto run
:pdfmanual
echo.
echo Pilih versi Buku Panduan PDF:
echo   1. Terbaru (v3.1.0 - Edisi Master Klien 130 halaman)
echo   2. Spesifikasi Optimizer (v3.0 - 50 halaman)
choice /c 12 /n /m "Pilih versi PDF [1-2]: "
if errorlevel 2 goto pdfv30
set "msshi_action=manual download --version v3.1.0"
goto run
:pdfv30
set "msshi_action=manual download --version v3.0"
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
