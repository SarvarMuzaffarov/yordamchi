"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Yordamchi Funksiyalar                 ║
║       Xatoliklarni boshqarish, logging, helpers             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import logging
import traceback
import functools
from datetime import datetime
from pathlib import Path
from typing import Callable, Any, Optional

from config import BASE_DIR, DATA_DIR


# ===== LOGGING TIZIMI =====
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"yordamchi_{datetime.now().strftime('%Y%m%d')}.log"

# Logger yaratish
logger = logging.getLogger("Yordamchi")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
    datefmt='%H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '\033[36m[%(levelname)s]\033[0m %(message)s'
)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# ===== XATOLIK BOSHQARUVI =====
class YordamchiError(Exception):
    """Asosiy xatolik sinfi"""
    def __init__(self, message: str, module: str = "Unknown", 
                 recoverable: bool = True, suggestion: str = ""):
        self.message = message
        self.module = module
        self.recoverable = recoverable
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.module}] {self.message}"


class AIError(YordamchiError):
    """AI bilan bog'liq xatolik"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module="AI Brain", **kwargs)


class VoiceError(YordamchiError):
    """Ovoz tizimi xatoligi"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module="Voice", **kwargs)


class GUIError(YordamchiError):
    """Interfeys xatoligi"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module="GUI", **kwargs)


class MemoryError(YordamchiError):
    """Xotira tizimi xatoligi"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module="Memory", **kwargs)


class AutomationError(YordamchiError):
    """Avtomatlashtirish xatoligi"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module="Automation", **kwargs)


# ===== DEKORATORLAR =====
def safe_execute(fallback_value=None, log_error: bool = True):
    """Xavfsiz bajarish dekoratori - xatolikni ushlaydi va dastur to'xtamaydi"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except YordamchiError as e:
                if log_error:
                    logger.error(f"{e.module}: {e.message}")
                    if e.suggestion:
                        logger.info(f"  Taklif: {e.suggestion}")
                return fallback_value
            except Exception as e:
                if log_error:
                    logger.error(f"{func.__name__}: {str(e)}")
                    logger.debug(traceback.format_exc())
                return fallback_value
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Qayta urinish dekoratori"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__}: Urinish {attempt}/{max_attempts} "
                            f"muvaffaqiyatsiz. {current_delay}s kutilmoqda..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__}: Barcha {max_attempts} urinish "
                            f"muvaffaqiyatsiz: {str(e)}"
                        )
            raise last_exception
        return wrapper
    return decorator


def timed(func: Callable) -> Callable:
    """Funksiya bajarilish vaqtini o'lchash"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__name__} - {elapsed:.3f}s")
        return result
    return wrapper


# ===== YORDAMCHI FUNKSIYALAR =====
def get_greeting() -> str:
    """Vaqtga qarab salom berish"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Xayrli tong"
    elif 12 <= hour < 17:
        return "Xayrli kun"
    elif 17 <= hour < 22:
        return "Xayrli kech"
    else:
        return "Xayrli tun"


def format_time(seconds: float) -> str:
    """Sekundlarni o'qilishi oson formatga o'zgartirish"""
    if seconds < 60:
        return f"{seconds:.1f} soniya"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} daqiqa"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} soat"


def format_bytes(bytes_val: int) -> str:
    """Baytlarni o'qilishi oson formatga o'zgartirish"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"


def is_internet_available() -> bool:
    """Internet mavjudligini tekshirish"""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_system_language() -> str:
    """Tizim tilini aniqlash"""
    import locale
    lang = locale.getdefaultlocale()[0]
    if lang and lang.startswith('uz'):
        return 'uz'
    return 'uz'  # Default o'zbek tili


def sanitize_text(text: str) -> str:
    """Matnni tozalash"""
    if not text:
        return ""
    # Ortiqcha bo'shliqlarni olib tashlash
    text = ' '.join(text.split())
    return text.strip()


def get_current_datetime_str() -> str:
    """Hozirgi vaqtni o'zbek formatida olish"""
    now = datetime.now()
    kunlar = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 
              'Juma', 'Shanba', 'Yakshanba']
    oylar = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
             'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr']
    
    kun_nomi = kunlar[now.weekday()]
    oy_nomi = oylar[now.month - 1]
    
    return f"{kun_nomi}, {now.day}-{oy_nomi} {now.year}, {now.strftime('%H:%M')}"


# ===== SIGNAL DISPATCHER =====
class SignalDispatcher:
    """Oddiy signal/event tizimi modullar orasida aloqa uchun"""
    
    def __init__(self):
        self._listeners = {}
    
    def connect(self, signal_name: str, callback: Callable):
        """Signalga callback ulash"""
        if signal_name not in self._listeners:
            self._listeners[signal_name] = []
        self._listeners[signal_name].append(callback)
    
    def disconnect(self, signal_name: str, callback: Callable):
        """Callbackni uzish"""
        if signal_name in self._listeners:
            self._listeners[signal_name].remove(callback)
    
    def emit(self, signal_name: str, *args, **kwargs):
        """Signalni yuborish"""
        if signal_name in self._listeners:
            for callback in self._listeners[signal_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Signal '{signal_name}' xatolik: {e}")


# Global dispatcher
dispatcher = SignalDispatcher()
