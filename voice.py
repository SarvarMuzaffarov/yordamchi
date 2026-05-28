"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Ovoz Tizimi                           ║
║    Speech Recognition, TTS, Wake Word Detection             ║
╚══════════════════════════════════════════════════════════════╝
"""

import threading
import queue
import time
from typing import Optional, Callable
from enum import Enum

from config import config
from utils import logger, safe_execute

# Ovoz kutubxonalarini import qilish
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.warning("SpeechRecognition o'rnatilmagan!")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 o'rnatilmagan!")


class VoiceState(Enum):
    """Ovoz tizimi holatlari"""
    IDLE = "idle"              # Kutish
    LISTENING = "listening"     # Tinglash
    PROCESSING = "processing"  # Qayta ishlash
    SPEAKING = "speaking"      # Gapirish
    WAKE_WORD = "wake_word"    # Wake word kutish


class VoiceEngine:
    """
    Ovoz tizimi - tinglash, gapirish, wake word aniqlash.
    Alohida threadlarda ishlaydi.
    """
    
    def __init__(self):
        self.state = VoiceState.IDLE
        self._running = False
        self._paused = False
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_text_recognized: Optional[Callable] = None
        self.on_wake_word: Optional[Callable] = None
        self.on_volume_change: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Speech Recognition
        self.recognizer = None
        self.microphone = None
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = config.voice.energy_threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.0
        
        # TTS Engine
        self.tts_engine = None
        self._init_tts()
        
        # Queue va threading
        self._speech_queue = queue.Queue()
        self._listen_thread: Optional[threading.Thread] = None
        self._speak_thread: Optional[threading.Thread] = None
        
        # Ovoz darajasi (GUI waveform uchun)
        self.current_volume = 0.0
        
        logger.info("Ovoz tizimi yaratildi")
    
    @safe_execute(fallback_value=None)
    def _init_tts(self):
        """TTS dvigatelini ishga tushirish"""
        if not TTS_AVAILABLE:
            return
        
        self.tts_engine = pyttsx3.init()
        
        # Ovoz sozlamalari
        self.tts_engine.setProperty('rate', config.voice.rate)
        self.tts_engine.setProperty('volume', config.voice.volume)
        
        # Mavjud ovozlardan tanlash
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Erkak ovozni tanlash (birinchi topilgani)
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            if config.voice.voice_id:
                self.tts_engine.setProperty('voice', config.voice.voice_id)
        
        logger.info("TTS dvigatel tayyor")
    
    def _set_state(self, new_state: VoiceState):
        """Holatni o'zgartirish va xabardor qilish"""
        old_state = self.state
        self.state = new_state
        if self.on_state_change:
            try:
                self.on_state_change(new_state, old_state)
            except Exception as e:
                logger.error(f"State callback xatolik: {e}")
    
    # ===== TINGLASH =====
    
    def start_listening(self, continuous: bool = False):
        """
        Tinglashni boshlash.
        
        Args:
            continuous: True = doimiy tinglash (wake word rejimi)
        """
        if not SR_AVAILABLE:
            logger.error("SpeechRecognition mavjud emas!")
            return
        
        if self._listen_thread and self._listen_thread.is_alive():
            return
        
        self._running = True
        
        if continuous:
            self._listen_thread = threading.Thread(
                target=self._continuous_listen_loop, daemon=True
            )
        else:
            self._listen_thread = threading.Thread(
                target=self._single_listen, daemon=True
            )
        
        self._listen_thread.start()
    
    def stop_listening(self):
        """Tinglashni to'xtatish"""
        self._running = False
        self._set_state(VoiceState.IDLE)
    
    def pause_listening(self):
        """Tinglashni pauza qilish"""
        self._paused = True
    
    def resume_listening(self):
        """Tinglashni davom ettirish"""
        self._paused = False
    
    def _single_listen(self):
        """Bir marta tinglash"""
        self._set_state(VoiceState.LISTENING)
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Tinglayapman...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=config.voice.listen_timeout,
                    phrase_time_limit=config.voice.phrase_timeout
                )
            
            self._set_state(VoiceState.PROCESSING)
            text = self._recognize_audio(audio)
            
            if text and self.on_text_recognized:
                self.on_text_recognized(text)
        
        except sr.WaitTimeoutError:
            logger.debug("Tinglash vaqti tugadi")
        except Exception as e:
            logger.error(f"Tinglash xatolik: {e}")
            if self.on_error:
                self.on_error(str(e))
        finally:
            self._set_state(VoiceState.IDLE)
    
    def _continuous_listen_loop(self):
        """Doimiy tinglash (wake word rejimi)"""
        self._set_state(VoiceState.WAKE_WORD)
        
        while self._running:
            if self._paused:
                time.sleep(0.1)
                continue
            
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    
                    try:
                        audio = self.recognizer.listen(
                            source, timeout=3, phrase_time_limit=5
                        )
                    except sr.WaitTimeoutError:
                        continue
                
                # Ovoz darajasini hisoblash (GUI uchun)
                try:
                    raw_data = audio.get_raw_data()
                    if raw_data:
                        rms = self._calculate_rms(raw_data)
                        self.current_volume = min(rms / 3000, 1.0)
                        if self.on_volume_change:
                            self.on_volume_change(self.current_volume)
                except Exception:
                    pass
                
                # Matnni tanish
                text = self._recognize_audio(audio)
                
                if text:
                    text_lower = text.lower().strip()
                    
                    # Wake word tekshirish
                    is_wake = any(
                        wake in text_lower 
                        for wake in config.voice.wake_words
                    )
                    
                    if is_wake:
                        logger.info(f"Wake word aniqlandi: {text}")
                        if self.on_wake_word:
                            self.on_wake_word(text)
                        
                        # Wake worddan keyingi matnni ajratish
                        remaining = text_lower
                        for wake in config.voice.wake_words:
                            remaining = remaining.replace(wake, "").strip()
                        
                        if remaining and self.on_text_recognized:
                            self.on_text_recognized(remaining)
                    elif self.state == VoiceState.LISTENING:
                        # Aktiv tinglash rejimida
                        if self.on_text_recognized:
                            self.on_text_recognized(text)
            
            except Exception as e:
                logger.error(f"Doimiy tinglash xatolik: {e}")
                time.sleep(1)
        
        self._set_state(VoiceState.IDLE)
    
    @safe_execute(fallback_value=None)
    def _recognize_audio(self, audio) -> Optional[str]:
        """Audioni matnga aylantirish"""
        try:
            # Google Speech Recognition (bepul)
            text = self.recognizer.recognize_google(
                audio, language="uz-UZ"
            )
            return text
        except sr.UnknownValueError:
            # O'zbek tili tanilmasa ruscha urinib ko'rish
            try:
                text = self.recognizer.recognize_google(
                    audio, language="ru-RU"
                )
                return text
            except sr.UnknownValueError:
                return None
        except sr.RequestError as e:
            logger.error(f"Speech API xatolik: {e}")
            # Offline rejim
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except Exception:
                return None
    
    def _calculate_rms(self, raw_data: bytes) -> float:
        """RMS (ovoz kuchi) ni hisoblash"""
        import struct
        count = len(raw_data) // 2
        if count == 0:
            return 0.0
        shorts = struct.unpack(f"{count}h", raw_data[:count * 2])
        sum_squares = sum(s * s for s in shorts)
        return (sum_squares / count) ** 0.5
    
    # ===== GAPIRISH =====
    
    def speak(self, text: str, priority: bool = False):
        """
        Matnni ovozga aylantirish.
        
        Args:
            text: Gapiriladigan matn
            priority: True = navbatni chetlab o'tib gapirish
        """
        if not text:
            return
        
        if priority:
            # Navbatni tozalash va darhol gapirish
            while not self._speech_queue.empty():
                try:
                    self._speech_queue.get_nowait()
                except queue.Empty:
                    break
        
        self._speech_queue.put(text)
        
        # Gapirish threadini ishga tushirish
        if not self._speak_thread or not self._speak_thread.is_alive():
            self._speak_thread = threading.Thread(
                target=self._speak_loop, daemon=True
            )
            self._speak_thread.start()
    
    def _speak_loop(self):
        """Gapirish sikli"""
        while not self._speech_queue.empty():
            try:
                text = self._speech_queue.get(timeout=1)
                self._do_speak(text)
            except queue.Empty:
                break
    
    @safe_execute(fallback_value=None)
    def _do_speak(self, text: str):
        """Matnni gapirish (sinxron)"""
        if not TTS_AVAILABLE or not self.tts_engine:
            logger.warning(f"TTS mavjud emas. Matn: {text}")
            return
        
        self._set_state(VoiceState.SPEAKING)
        self.pause_listening()  # Tinglashni to'xtatish (echo oldini olish)
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS xatolik: {e}")
            # TTS ni qayta ishga tushirish
            self._init_tts()
        finally:
            self._set_state(VoiceState.IDLE)
            self.resume_listening()
    
    def stop_speaking(self):
        """Gaprishni to'xtatish"""
        if TTS_AVAILABLE and self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        
        # Navbatni tozalash
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
            except queue.Empty:
                break
        
        self._set_state(VoiceState.IDLE)
    
    # ===== YORDAMCHI =====
    
    def get_available_voices(self) -> list:
        """Mavjud ovozlar ro'yxatini olish"""
        if not TTS_AVAILABLE or not self.tts_engine:
            return []
        
        voices = self.tts_engine.getProperty('voices')
        return [{"id": v.id, "name": v.name} for v in voices]
    
    def set_voice(self, voice_id: str):
        """Ovozni o'zgartirish"""
        if TTS_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('voice', voice_id)
            config.voice.voice_id = voice_id
    
    def set_rate(self, rate: int):
        """Gapirish tezligini o'zgartirish"""
        if TTS_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
            config.voice.rate = rate
    
    def set_volume(self, volume: float):
        """Ovoz balandligini o'zgartirish"""
        if TTS_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
            config.voice.volume = volume
    
    def is_listening(self) -> bool:
        """Tinglayotganligini tekshirish"""
        return self.state in (VoiceState.LISTENING, VoiceState.WAKE_WORD)
    
    def is_speaking(self) -> bool:
        """Gapiriyotganligini tekshirish"""
        return self.state == VoiceState.SPEAKING
    
    def cleanup(self):
        """Resurslarni tozalash"""
        self.stop_listening()
        self.stop_speaking()
        if TTS_AVAILABLE and self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        logger.info("Ovoz tizimi tozalandi")
