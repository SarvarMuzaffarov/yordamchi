@echo off
chcp 65001 >nul
title YORDAMCHI - AI Assistant

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║      🌟 YORDAMCHI ishga tushmoqda...    ║
echo  ╚══════════════════════════════════════════╝
echo.

REM Python tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python topilmadi!
    echo  💡 https://www.python.org/downloads/ dan o'rnating
    pause
    exit /b 1
)

REM Kutubxonalar tekshirish
echo  📦 Kutubxonalar tekshirilmoqda...
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo  ⚙️  Kutubxonalar o'rnatilmoqda...
    pip install -r requirements.txt
)

REM Dasturni ishga tushirish
echo.
echo  🚀 Yordamchi ishga tushdi!
echo.
python main.py

if errorlevel 1 (
    echo.
    echo  ❌ Xatolik yuz berdi
    pause
)
