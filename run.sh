#!/bin/bash

# YORDAMCHI - Linux/macOS uchun ishga tushirish skripti

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║      🌟 YORDAMCHI ishga tushmoqda...    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo "  ❌ Python3 topilmadi!"
    echo "  💡 sudo apt install python3.11 (Linux) yoki brew install python@3.11 (macOS)"
    exit 1
fi

# Virtual muhit (agar yo'q bo'lsa yarat)
if [ ! -d "venv" ]; then
    echo "  📦 Virtual muhit yaratilmoqda..."
    python3 -m venv venv
fi

# Virtual muhitni faollashtirish
source venv/bin/activate

# Kutubxonalar tekshirish
if ! python -c "import PyQt6" 2>/dev/null; then
    echo "  ⚙️  Kutubxonalar o'rnatilmoqda..."
    pip install -r requirements.txt
fi

# Dasturni ishga tushirish
echo ""
echo "  🚀 Yordamchi ishga tushdi!"
echo ""
python main.py
