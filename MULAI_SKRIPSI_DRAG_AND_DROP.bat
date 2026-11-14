@echo off
setlocal EnableExtensions
title MuZA Skripsi Starter v1.1 (Drag-and-Drop Edition) - MSSHI
chcp 65001 >nul 2>&1
set "PYTHONIOENCODING=utf-8"

if exist "D:\HermesData" (
    if not exist "D:\HermesData\temp" mkdir "D:\HermesData\temp" >nul 2>&1
    set "TEMP=D:\HermesData\temp"
    set "TMP=D:\HermesData\temp"
)

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=py -3 -B -X utf8"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=python -B -X utf8"
    ) else (
        echo [ERROR] Python 3 belum ditemukan di PATH.
        echo Unduh Python 3.10+ atau jalankan MULAI_DI_SINI_PEMULA.bat terlebih dahulu.
        pause
        exit /b 1
    )
)

echo ============================================================================
echo   MuZA SKRIPSI STARTER v1.1 (DRAG-AND-DROP) - MSSHI v3.1.0
echo ============================================================================
echo   Kamu bisa:
echo   1. DRAG file .zip (MuZA_Search) dan/atau .pdf/.docx Pedoman ke ikon .bat ini
echo   2. Atau DOUBLE-CLICK langsung lalu isi nama kampus dan metodologi!
echo ============================================================================
echo.

%PY_CMD% "%~dp0scripts\msshi_skripsi_drop.py" --install-deps %*
set "ERR=%errorlevel%"
echo.
if %ERR%==0 (
    echo [OK] Template Word skripsi siap dipakai! Cek output path di atas.
) else (
    echo [PERHATIAN] Terjadi kendala (exit code %ERR%). Cek pesan di atas.
)
pause
exit /b %ERR%
