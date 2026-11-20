@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
echo ======================================================
echo   MSSHI v3.1.2 - Sovereign Sage ^& Ultimate Optimizer
echo ======================================================
echo 1. Pasang MSSHI Standar (bebas pilih folder: C:/D:/E:/mana saja)
echo 2. Pasang MSSHI Mode Hemat Windows 10 RAM 4 GB (Light Build + Low-RAM)
echo 3. Migrasi Hermes yang sudah ada
echo 4. Buka Hermes Desktop
echo 5. Periksa hasil instalasi (Doctor)
echo 6. Unduh Buku Panduan PDF Lengkap (v3.1.2 / v3.0)
echo 7. Panduan Mode CLI Hemat RAM (tanpa membuka Desktop)
choice /c 1234567 /n /m "Pilih 1-7: "
if errorlevel 7 goto clifallback
if errorlevel 6 goto pdfmanual
if errorlevel 5 goto audit
if errorlevel 4 goto desktop
if errorlevel 3 goto migrate
if errorlevel 2 goto setup_lite
echo.
set "custom_msshi_dir="
set /p "custom_msshi_dir=Folder instalasi MSSHI (Enter=otomatis, atau ketik bebas misal D:\MSSHI atau E:\MSSHI): "
if not "%custom_msshi_dir%"=="" set "MSSHI_HOME=%custom_msshi_dir%"
set "msshi_action=setup"
goto run
:setup_lite
echo.
echo [Mode Hemat Windows 10 RAM 4 GB: Light Build ^<= 50 MB + Low-RAM ^<= 150 MB]
set "custom_msshi_dir="
set /p "custom_msshi_dir=Folder instalasi MSSHI (Enter=otomatis, atau ketik bebas misal C:\MSSHI, D:\MSSHI, E:\MSSHI): "
if not "%custom_msshi_dir%"=="" set "MSSHI_HOME=%custom_msshi_dir%"
set "msshi_action=setup --low-ram --no-pdf"
goto run
:clifallback
set "msshi_action=desktop --prefer-cli"
goto run
:pdfmanual
echo.
echo Pilih versi Buku Panduan PDF:
echo   1. Terbaru (v3.1.2)
echo   2. Spesifikasi Optimizer (v3.0 - 50 halaman)
choice /c 12 /n /m "Pilih versi PDF [1-2]: "
if errorlevel 2 goto pdfv30
set "msshi_action=manual download --version latest"
goto run
:pdfv30
set "msshi_action=manual download --version v3.0"
goto run
:audit
set "msshi_action=doctor"
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
