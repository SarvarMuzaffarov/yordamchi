# 📥 YORDAMCHI - O'rnatish Qo'llanmasi

## 🪟 WINDOWS uchun

### 1-qadam: Python o'rnatish
1. https://www.python.org/downloads/ ga kiring
2. **Python 3.11** yoki yuqorisini yuklab oling
3. O'rnatishda **"Add Python to PATH"** ni belgilang ✅

### 2-qadam: Loyihani yuklab olish
ZIP faylni kerakli papkaga arxivdan chiqaring (masalan: `C:\Yordamchi\`)

### 3-qadam: Terminal ochish
- `Win + R` bosing
- `cmd` deb yozing va Enter
- Loyiha papkasiga o'ting:
```cmd
cd C:\Yordamchi
```

### 4-qadam: Kutubxonalarni o'rnatish
```cmd
pip install -r requirements.txt
```

**Agar PyAudio xato bersa:**
```cmd
pip install pipwin
pipwin install pyaudio
```

### 5-qadam: Dasturni ishga tushirish
```cmd
python main.py
```

Yoki shunchaki **`run.bat`** faylga ikki marta bosing!

---

## 🐧 LINUX uchun (Ubuntu/Debian)

```bash
# 1. Python va kerakli paketlar
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
sudo apt install portaudio19-dev python3-pyaudio
sudo apt install libgl1-mesa-glx libglib2.0-0  # OpenCV uchun

# 2. Virtual muhit (tavsiya etiladi)
python3 -m venv venv
source venv/bin/activate

# 3. Kutubxonalar
pip install -r requirements.txt

# 4. Ishga tushirish
python main.py
```

Yoki **`./run.sh`** faylni bajaring.

---

## 🍎 macOS uchun

```bash
# 1. Homebrew bilan kerakli paketlar
brew install python@3.11 portaudio

# 2. Virtual muhit
python3 -m venv venv
source venv/bin/activate

# 3. Kutubxonalar
pip install -r requirements.txt

# 4. Ishga tushirish
python main.py
```

---

## 🔑 Gemini API Key olish

1. https://aistudio.google.com/app/apikey ga kiring
2. Google akkaunt bilan kiring
3. **"Create API Key"** ni bosing
4. API kalitni nusxalang
5. Dastur ishga tushganda Wizard ga kiriting

---

## 🦙 Ollama o'rnatish (Offline AI)

Internet bo'lmaganda ham AI ishlashi uchun:

### Windows/macOS:
1. https://ollama.com ga kiring
2. Yuklab olib o'rnating
3. Modelni yuklang:
```bash
ollama pull llama3.1
```

### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
```

---

## ❗ Tez-tez Uchraydigan Muammolar

### "ModuleNotFoundError"
```bash
pip install --upgrade -r requirements.txt
```

### Mikrofon ishlamayapti
- Tizim sozlamalarida mikrofonga ruxsat bering
- `pip install --upgrade pyaudio`

### Gemini ishlamayapti
- API kalitni tekshiring
- Internet aloqani tekshiring
- VPN ishlatib ko'ring

### GUI ochilmayapti
```bash
pip install --upgrade PyQt6
```

### ChromaDB xatoligi
```bash
pip install --upgrade chromadb sentence-transformers
```

---

## 🎯 Birinchi Ishga Tushirish

1. `python main.py` ni ishga tushiring
2. **First Run Wizard** ochiladi
3. Ismingizni kiriting (default: Sarvar)
4. Gemini API kalitni kiriting (yoki keyinroq)
5. **🚀 Boshlaymiz!** ni bosing
6. Asosiy oyna ochiladi - tayyor! 🎉

---

## 💡 Maslahatlar

- **Tezroq ishlashi uchun:** SSD diskga o'rnating
- **Xotira saqlanadi:** `data/memory/` papkasida
- **Loglar:** `data/logs/` papkasida (xatolik tekshirish uchun)
- **API kalitni xavfsiz saqlang:** Hech kimga bermang!
