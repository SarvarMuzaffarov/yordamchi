# 🌟 YORDAMCHI - Futuristik AI Assistant

Iron Man dagi JARVIS uslubidagi shaxsiy AI yordamchi dastur. Cyberpunk + Holographic dizayn, ko'p agentli AI tizimi, ovozli boshqaruv va kompyuter avtomatlashtirish.

![Version](https://img.shields.io/badge/version-2.0-00f5ff)
![Python](https://img.shields.io/badge/python-3.11+-7b2ff7)
![License](https://img.shields.io/badge/license-MIT-ff006e)

## ✨ Asosiy Imkoniyatlar

- 🧠 **Hybrid AI** - Gemini 2.0 Flash (online) + Ollama (offline)
- 🎤 **Ovozli boshqaruv** - O'zbek tilida wake word detection
- 🤖 **Multi-Agent** - Research, Coding, Vision, Personal agentlar
- 💾 **Shaxsiy xotira** - ChromaDB asosidagi RAG tizim
- 👁 **Computer Vision** - yuz va emotsiya tanish
- 🎨 **Futuristik GUI** - Hologram orb, particles, neon glow
- ⚡ **Avtomatlashtirish** - kompyuter, brauzer, fayllar boshqaruvi
- 📊 **Tizim monitoringi** - real-time CPU, RAM, Disk monitoring

## 🚀 Tezkor Boshlash

### 1. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Dasturni ishga tushirish

```bash
python main.py
```

### 3. Birinchi ishga tushirishda:
- Ismingizni kiriting
- Gemini API kalitni kiriting (https://aistudio.google.com/app/apikey)
- "Boshlaymiz!" ni bosing

## 📋 Tizim Talablari

- **OS:** Windows 10/11, macOS, Linux
- **Python:** 3.11 yoki yuqori
- **RAM:** Minimum 4GB (tavsiya 8GB+)
- **Internet:** Gemini AI uchun (Ollama bilan offline ishlaydi)
- **Mikrofon:** Ovoz tanish uchun
- **Kamera:** Vision xususiyatlari uchun (ixtiyoriy)

## 🎮 Foydalanish

### Ovoz orqali:
- "Yordamchi" yoki "Jarvis" deb ayting
- Savolingizni bering
- Misol: "Yordamchi, YouTube ochib ber"

### Matn orqali:
- Pastdagi maydonga yozing
- Enter bosing

### Klaviatura yorliqlari:
- `F11` - To'liq ekran rejimi
- `Esc` - Joriy amalni to'xtatish

## 🛠 Sozlash

Sozlamalar oynasini ochish uchun **⚙️ Sozlamalar** tugmasini bosing:

- **AI tab** - API kalit, model, temperature
- **Ovoz tab** - tezlik, balandlik, wake words
- **Interfeys tab** - particles, scanlines, tema
- **Agentlar tab** - qaysi agentlarni yoqish
- **Umumiy tab** - ism, xavfsizlik

## 📁 Loyiha Strukturasi

```
yordamchi/
├── main.py              # Dasturni ishga tushirish
├── config.py            # Sozlamalar
├── gui.py               # Futuristik GUI
├── voice.py             # Ovoz tizimi
├── brain.py             # AI miya
├── agents.py            # Multi-Agent tizimi
├── memory.py            # Xotira (ChromaDB)
├── system_monitor.py    # Tizim monitoringi
├── automation.py        # Avtomatlashtirish
├── vision.py            # Kamera, yuz tanish
├── settings.py          # Sozlamalar oynasi
├── utils.py             # Yordamchi funksiyalar
├── requirements.txt     # Python kutubxonalari
└── data/                # Ma'lumotlar
    ├── memory/          # ChromaDB ma'lumotlari
    ├── faces/           # Saqlangan yuzlar
    └── logs/            # Log fayllar
```

## 🐛 Muammolarni hal qilish

### "PyAudio o'rnatilmadi" xatoligi:
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### "OpenCV xatoligi":
```bash
pip install --upgrade opencv-python opencv-contrib-python
```

### Gemini API ishlamayapti:
1. API kalitingizni tekshiring: https://aistudio.google.com/app/apikey
2. Internet aloqasini tekshiring
3. Sozlamalarda API kalitni qayta kiriting

## 💡 Maslahatlar

- API kalitni `.env` faylida saqlashingiz mumkin
- Offline rejim uchun Ollama o'rnating: https://ollama.com
- Bir necha yuzni saqlash mumkin (yuz tanish uchun)
- Loglar `data/logs/` papkasida saqlanadi

## 📝 Litsenziya

MIT License - Sarvar uchun yaratilgan ❤️

## 🙏 Minnatdorchilik

- Google Gemini AI
- PyQt6 jamoasi
- ChromaDB
- Va barcha ochiq manba kutubxonalari yaratuvchilariga
