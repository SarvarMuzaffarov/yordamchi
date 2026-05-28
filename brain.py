"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - AI Miya (Brain)                       ║
║      Gemini + Ollama Hybrid AI tizimi                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import threading
from typing import Optional, Callable, List, Dict, Generator
from enum import Enum

from config import config
from memory import MemoryManager
from utils import (
    logger, safe_execute, retry, timed, 
    get_current_datetime_str, is_internet_available
)

# AI kutubxonalari
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        from google import genai as genai_new
        GEMINI_AVAILABLE = True
        # Yangi kutubxona uchun wrapper
        genai = None
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None
        logger.warning("Google Generative AI o'rnatilmagan!")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama kutubxonasi o'rnatilmagan!")


class AIMode(Enum):
    """AI ishlash rejimi"""
    ONLINE = "online"      # Gemini (internet bilan)
    OFFLINE = "offline"    # Ollama (lokal)
    HYBRID = "hybrid"      # Avval Gemini, xatolikda Ollama


class AIBrain:
    """
    Yordamchining asosiy miyasi.
    Gemini va Ollama ni hybrid tarzda ishlatadi.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.mode = AIMode.HYBRID
        self._gemini_model = None
        self._chat_session = None
        self._initialized = False
        
        # Callbacks
        self.on_thinking_start: Optional[Callable] = None
        self.on_thinking_end: Optional[Callable] = None
        self.on_stream_token: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Kontekst
        self._system_context = self._build_system_prompt()
        
        # Ishga tushirish
        self._initialize()
    
    def _build_system_prompt(self) -> str:
        """Tizim promptini yaratish"""
        current_time = get_current_datetime_str()
        
        system_prompt = f"""{config.ai.system_prompt}

Hozirgi vaqt: {current_time}
Foydalanuvchi ismi: {config.user_name}

MUHIM QOIDALAR:
1. Doimo o'zbek tilida javob ber (agar boshqa til so'ralmasa)
2. Qisqa va aniq javob ber, lekin kerak bo'lsa batafsil tushuntir
3. Sarvarni hurmat bilan "Sarvar" deb murojaat qil
4. Texnik savollarni oddiy tilda tushuntir
5. Hazil va emotsiya qo'sh, lekin professional bo'l
6. Agar biror narsani bilmasang, ochiq ayt
7. Kompyuterni boshqarish buyruqlari berilsa, aniq bajariladigan vazifani tasdiqlat
8. Xotirangdagi ma'lumotlarni ishlatib, shaxsiy javoblar ber
"""
        return system_prompt
    
    @safe_execute(fallback_value=None)
    def _initialize(self):
        """AI ni ishga tushirish"""
        # Gemini
        if GEMINI_AVAILABLE and config.ai.gemini_api_key:
            try:
                genai.configure(api_key=config.ai.gemini_api_key)
                
                generation_config = genai.types.GenerationConfig(
                    temperature=config.ai.temperature,
                    max_output_tokens=config.ai.max_tokens,
                    top_p=0.95,
                    top_k=40,
                )
                
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                self._gemini_model = genai.GenerativeModel(
                    model_name=config.ai.gemini_model,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    system_instruction=self._system_context
                )
                
                self._chat_session = self._gemini_model.start_chat(history=[])
                self._initialized = True
                logger.info(f"Gemini ({config.ai.gemini_model}) tayyor")
                
            except Exception as e:
                logger.error(f"Gemini ishga tushmadi: {e}")
        
        # Ollama tekshirish
        if OLLAMA_AVAILABLE:
            try:
                ollama.list()
                logger.info("Ollama mavjud")
            except Exception:
                logger.warning("Ollama serveriga ulanib bo'lmadi")
        
        if not self._initialized:
            logger.warning("AI to'liq ishga tushmadi. API kalitni tekshiring.")
    
    @timed
    def think(self, user_input: str, context: str = "", 
              stream: bool = True) -> str:
        """
        Asosiy fikrlash funksiyasi.
        
        Args:
            user_input: Foydalanuvchi kiritgan matn
            context: Qo'shimcha kontekst (tizim monitori, vazifalar va h.k.)
            stream: Oqim rejimida javob berish
            
        Returns:
            AI javobi
        """
        if not user_input.strip():
            return ""
        
        # Thinking boshlandi
        if self.on_thinking_start:
            self.on_thinking_start()
        
        try:
            # Xotiradan kontekst olish
            memory_context = self.memory.get_ai_context(user_input)
            
            # To'liq prompt yaratish
            full_prompt = self._build_prompt(user_input, context, memory_context)
            
            # AI dan javob olish
            if self.mode == AIMode.ONLINE or self.mode == AIMode.HYBRID:
                response = self._ask_gemini(full_prompt, stream)
                if response is None and self.mode == AIMode.HYBRID:
                    response = self._ask_ollama(full_prompt)
            else:
                response = self._ask_ollama(full_prompt)
            
            if response is None:
                response = "Kechirasiz, hozir javob bera olmayapman. Internet yoki AI tizimini tekshiring."
            
            # Xotiraga saqlash
            self.memory.add_to_conversation("user", user_input)
            self.memory.add_to_conversation("assistant", response)
            
            # Muhim ma'lumotni xotiraga saqlash
            self._auto_memorize(user_input, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Think xatolik: {e}")
            if self.on_error:
                self.on_error(str(e))
            return f"Xatolik yuz berdi: {str(e)}"
        
        finally:
            if self.on_thinking_end:
                self.on_thinking_end()
    
    def _build_prompt(self, user_input: str, context: str, 
                      memory_context: str) -> str:
        """To'liq promptni yaratish"""
        parts = []
        
        if context:
            parts.append(f"[Joriy kontekst:]\n{context}")
        
        if memory_context:
            parts.append(memory_context)
        
        parts.append(f"Sarvar: {user_input}")
        
        return "\n\n".join(parts)
    
    @retry(max_attempts=2, delay=1.0)
    def _ask_gemini(self, prompt: str, stream: bool = True) -> Optional[str]:
        """Gemini dan javob olish"""
        if not self._initialized or not self._chat_session:
            return None
        
        try:
            if stream and self.on_stream_token:
                response = self._chat_session.send_message(prompt, stream=True)
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        self.on_stream_token(chunk.text)
                return full_response
            else:
                response = self._chat_session.send_message(prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Gemini xatolik: {e}")
            # Chat sessionni yangilash
            if self._gemini_model:
                self._chat_session = self._gemini_model.start_chat(history=[])
            return None
    
    @safe_execute(fallback_value=None)
    def _ask_ollama(self, prompt: str) -> Optional[str]:
        """Ollama dan javob olish (offline)"""
        if not OLLAMA_AVAILABLE:
            return None
        
        try:
            response = ollama.chat(
                model=config.ai.ollama_model,
                messages=[
                    {"role": "system", "content": self._system_context},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama xatolik: {e}")
            return None
    
    def _auto_memorize(self, user_input: str, response: str):
        """Muhim ma'lumotni avtomatik xotiraga saqlash"""
        # Eslab qolish kerak bo'lgan kalit so'zlar
        memory_triggers = [
            "eslab qol", "yodingda bo'lsin", "men", "mening",
            "sevaman", "yoqtiraman", "yoqtirmayman", "ism",
            "tug'ilgan", "manzil", "telefon", "email"
        ]
        
        input_lower = user_input.lower()
        should_memorize = any(trigger in input_lower for trigger in memory_triggers)
        
        if should_memorize:
            # Shaxsiy ma'lumotni saqlash
            self.memory.remember(
                f"Sarvar aytdi: {user_input}",
                category="personal",
                importance=7
            )
    
    def reset_chat(self):
        """Chat sessionni qayta boshlash"""
        if self._gemini_model:
            self._chat_session = self._gemini_model.start_chat(history=[])
        self.memory.conversation.clear()
        self._system_context = self._build_system_prompt()
        logger.info("Chat session yangilandi")
    
    def set_mode(self, mode: AIMode):
        """AI rejimini o'zgartirish"""
        self.mode = mode
        logger.info(f"AI rejimi: {mode.value}")
    
    def update_api_key(self, api_key: str):
        """API kalitni yangilash va qayta ulash"""
        config.ai.gemini_api_key = api_key
        config.save()
        self._initialize()
    
    def get_status(self) -> Dict:
        """AI holatini olish"""
        return {
            "mode": self.mode.value,
            "gemini_ready": self._initialized,
            "ollama_available": OLLAMA_AVAILABLE,
            "model": config.ai.gemini_model if self._initialized else config.ai.ollama_model,
            "internet": is_internet_available()
        }
    
    def quick_response(self, text: str) -> str:
        """Tezkor javob (kontekstsiz, oddiy savollar uchun)"""
        # Oddiy buyruqlarni o'zi javob berish
        text_lower = text.lower().strip()
        
        # Salomlashish
        greetings = ["salom", "assalomu alaykum", "hey", "hi", "hello"]
        if any(g in text_lower for g in greetings):
            from utils import get_greeting
            greeting = get_greeting()
            return f"{greeting}, Sarvar! Sizga qanday yordam bera olaman?"
        
        # Vaqt
        if any(w in text_lower for w in ["soat", "vaqt", "necha"]):
            return f"Hozir {get_current_datetime_str()}"
        
        return ""  # Tezkor javob topilmadi, to'liq think() ishlatiladi
