"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Avtomatlashtirish Moduli              ║
║    Kompyuter, brauzer, fayllar, ilovalar boshqaruvi         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import time
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum

from config import config
from utils import logger, safe_execute, AutomationError

# Avtomatlashtirish kutubxonalari
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Burchakka olib borsa to'xtaydi
    pyautogui.PAUSE = 0.3
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class ActionType(Enum):
    """Amal turlari"""
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    TYPE_TEXT = "type_text"
    CLICK = "click"
    SCREENSHOT = "screenshot"
    OPEN_URL = "open_url"
    FILE_OP = "file_operation"
    SYSTEM_CMD = "system_command"
    HOTKEY = "hotkey"


class ComputerAutomation:
    """
    Kompyuterni avtomatlashtirish.
    Ilovalar, brauzer, fayllar va tizim boshqaruvi.
    """
    
    def __init__(self):
        self.os_name = platform.system().lower()
        self.safe_mode = config.automation.safe_mode
        self._action_history: List[Dict] = []
        logger.info(f"Avtomatlashtirish tayyor (OS: {self.os_name})")
    
    # ===== ILOVALAR =====
    
    @safe_execute(fallback_value=False)
    def open_application(self, app_name: str) -> bool:
        """Ilovani ochish"""
        app_map = {
            # Windows
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "chrome": "chrome",
            "firefox": "firefox",
            "vscode": "code",
            "telegram": "telegram",
            
            # O'zbek nomlari
            "bloknot": "notepad.exe",
            "kalkulyator": "calc.exe",
            "brauzer": "chrome",
            "terminal": "cmd.exe",
        }
        
        # Ilovani topish
        app_cmd = app_map.get(app_name.lower(), app_name)
        
        logger.info(f"Ilova ochilmoqda: {app_cmd}")
        
        if self.os_name == "windows":
            os.startfile(app_cmd)
        elif self.os_name == "linux":
            subprocess.Popen([app_cmd], stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        elif self.os_name == "darwin":  # macOS
            subprocess.Popen(["open", "-a", app_cmd])
        
        self._log_action(ActionType.OPEN_APP, {"app": app_name})
        return True
    
    @safe_execute(fallback_value=False)
    def close_application(self, app_name: str) -> bool:
        """Ilovani yopish"""
        if self.os_name == "windows":
            os.system(f"taskkill /f /im {app_name}.exe 2>nul")
        else:
            os.system(f"pkill -f {app_name} 2>/dev/null")
        
        self._log_action(ActionType.CLOSE_APP, {"app": app_name})
        return True
    
    # ===== BRAUZER =====
    
    @safe_execute(fallback_value=False)
    def open_url(self, url: str) -> bool:
        """URLni brauzerda ochish"""
        import webbrowser
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        webbrowser.open(url)
        self._log_action(ActionType.OPEN_URL, {"url": url})
        logger.info(f"URL ochildi: {url}")
        return True
    
    @safe_execute(fallback_value=False)
    def google_search(self, query: str) -> bool:
        """Google da qidirish"""
        import urllib.parse
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        return self.open_url(url)
    
    @safe_execute(fallback_value=False)
    def youtube_search(self, query: str) -> bool:
        """YouTube da qidirish"""
        import urllib.parse
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        return self.open_url(url)
    
    # ===== KLAVIATURA VA SICHQONCHA =====
    
    @safe_execute(fallback_value=False)
    def type_text(self, text: str, interval: float = 0.02) -> bool:
        """Matn yozish"""
        if not PYAUTOGUI_AVAILABLE:
            logger.error("PyAutoGUI mavjud emas!")
            return False
        
        # Unicode matnlar uchun clipboard ishlatish
        if any(ord(c) > 127 for c in text):
            if CLIPBOARD_AVAILABLE:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.typewrite(text, interval=interval)
        else:
            pyautogui.typewrite(text, interval=interval)
        
        self._log_action(ActionType.TYPE_TEXT, {"text": text[:50]})
        return True
    
    @safe_execute(fallback_value=False)
    def press_hotkey(self, *keys) -> bool:
        """Klaviatura yorliqlarini bosish"""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        pyautogui.hotkey(*keys)
        self._log_action(ActionType.HOTKEY, {"keys": list(keys)})
        return True
    
    @safe_execute(fallback_value=False)
    def click(self, x: int = None, y: int = None, 
              button: str = "left", clicks: int = 1) -> bool:
        """Sichqoncha bosish"""
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button, clicks=clicks)
        else:
            pyautogui.click(button=button, clicks=clicks)
        
        self._log_action(ActionType.CLICK, {"x": x, "y": y, "button": button})
        return True
    
    @safe_execute(fallback_value=None)
    def take_screenshot(self, region=None) -> Optional[str]:
        """Skrinshot olish"""
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        screenshot_path = str(Path.home() / "Desktop" / 
                            f"screenshot_{int(time.time())}.png")
        
        img = pyautogui.screenshot(region=region)
        img.save(screenshot_path)
        
        self._log_action(ActionType.SCREENSHOT, {"path": screenshot_path})
        logger.info(f"Skrinshot saqlandi: {screenshot_path}")
        return screenshot_path
    
    # ===== FAYL OPERATSIYALARI =====
    
    @safe_execute(fallback_value=False)
    def create_file(self, path: str, content: str = "") -> bool:
        """Fayl yaratish"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        
        self._log_action(ActionType.FILE_OP, {"op": "create", "path": path})
        logger.info(f"Fayl yaratildi: {path}")
        return True
    
    @safe_execute(fallback_value=None)
    def read_file(self, path: str) -> Optional[str]:
        """Faylni o'qish"""
        file_path = Path(path)
        if not file_path.exists():
            logger.error(f"Fayl topilmadi: {path}")
            return None
        return file_path.read_text(encoding='utf-8')
    
    @safe_execute(fallback_value=False)
    def open_file(self, path: str) -> bool:
        """Faylni standart ilova bilan ochish"""
        if self.os_name == "windows":
            os.startfile(path)
        elif self.os_name == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        
        self._log_action(ActionType.FILE_OP, {"op": "open", "path": path})
        return True
    
    @safe_execute(fallback_value=[])
    def list_files(self, directory: str = ".", pattern: str = "*") -> List[str]:
        """Fayllar ro'yxatini olish"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        return [str(f) for f in dir_path.glob(pattern)]
    
    # ===== TIZIM BUYRUQLARI =====
    
    @safe_execute(fallback_value="")
    def run_command(self, command: str, timeout: int = 30) -> str:
        """Tizim buyrug'ini bajarish"""
        if self.safe_mode:
            # Xavfli buyruqlarni bloklash
            dangerous = ["rm -rf", "format", "del /f", "shutdown", "mkfs"]
            if any(d in command.lower() for d in dangerous):
                logger.warning(f"Xavfli buyruq bloklandi: {command}")
                return "⚠️ Xavfli buyruq bloklandi. Safe mode yoqilgan."
        
        result = subprocess.run(
            command, shell=True, capture_output=True, 
            text=True, timeout=timeout
        )
        
        output = result.stdout or result.stderr
        self._log_action(ActionType.SYSTEM_CMD, {"cmd": command})
        return output.strip()
    
    @safe_execute(fallback_value=False)
    def set_volume(self, level: int) -> bool:
        """Ovoz balandligini o'zgartirish (0-100)"""
        level = max(0, min(100, level))
        
        if self.os_name == "windows":
            # Windows uchun
            from ctypes import cast, POINTER
            try:
                import comtypes
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100, None)
            except ImportError:
                os.system(f"nircmd.exe setsysvolume {int(level * 655.35)}")
        elif self.os_name == "linux":
            os.system(f"amixer -q sset Master {level}%")
        elif self.os_name == "darwin":
            os.system(f"osascript -e 'set volume output volume {level}'")
        
        return True
    
    @safe_execute(fallback_value=False)
    def shutdown_computer(self, mode: str = "shutdown", delay: int = 60) -> bool:
        """Kompyuterni o'chirish/qayta ishga tushirish"""
        if self.safe_mode:
            logger.warning("Shutdown buyrug'i safe mode da bloklangan")
            return False
        
        if self.os_name == "windows":
            if mode == "shutdown":
                os.system(f"shutdown /s /t {delay}")
            elif mode == "restart":
                os.system(f"shutdown /r /t {delay}")
            elif mode == "sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            if mode == "shutdown":
                os.system(f"shutdown -h +{delay // 60}")
            elif mode == "restart":
                os.system(f"shutdown -r +{delay // 60}")
        
        return True
    
    # ===== CLIPBOARD =====
    
    @safe_execute(fallback_value="")
    def get_clipboard(self) -> str:
        """Clipboard matnini olish"""
        if CLIPBOARD_AVAILABLE:
            return pyperclip.paste()
        return ""
    
    @safe_execute(fallback_value=False)
    def set_clipboard(self, text: str) -> bool:
        """Clipboardga matn yozish"""
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(text)
            return True
        return False
    
    # ===== TARIX =====
    
    def _log_action(self, action_type: ActionType, details: Dict):
        """Amalni tarixga yozish"""
        self._action_history.append({
            "type": action_type.value,
            "details": details,
            "time": time.time()
        })
        # Oxirgi 100 ta amalni saqlash
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-100:]
    
    def get_history(self, last_n: int = 10) -> List[Dict]:
        """Amallar tarixini olish"""
        return self._action_history[-last_n:]
    
    # ===== BUYRUQ TAHLILCHISI =====
    
    def parse_and_execute(self, command_text: str) -> str:
        """
        Matnli buyruqni tahlil qilib bajarish.
        AI tomonidan chaqiriladi.
        """
        text_lower = command_text.lower().strip()
        
        # URL ochish
        if any(w in text_lower for w in ["och", "open"]):
            if "youtube" in text_lower:
                query = text_lower.replace("youtube", "").replace("och", "").strip()
                if query:
                    self.youtube_search(query)
                    return f"YouTube da '{query}' qidirildi"
                else:
                    self.open_url("https://youtube.com")
                    return "YouTube ochildi"
            
            if "google" in text_lower:
                query = text_lower.replace("google", "").replace("och", "").strip()
                if query:
                    self.google_search(query)
                    return f"Google da '{query}' qidirildi"
                else:
                    self.open_url("https://google.com")
                    return "Google ochildi"
            
            if "telegram" in text_lower:
                self.open_application("telegram")
                return "Telegram ochildi"
        
        # Skrinshot
        if any(w in text_lower for w in ["skrinshot", "screenshot", "ekran"]):
            path = self.take_screenshot()
            if path:
                return f"Skrinshot saqlandi: {path}"
            return "Skrinshot olishda xatolik"
        
        # Ovoz
        if "ovoz" in text_lower or "volume" in text_lower:
            import re
            numbers = re.findall(r'\d+', text_lower)
            if numbers:
                level = int(numbers[0])
                self.set_volume(level)
                return f"Ovoz balandligi {level}% ga o'zgartirildi"
        
        return ""
