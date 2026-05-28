"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Xotira va RAG Tizimi                  ║
║     ChromaDB bilan shaxsiy xotira, suhbat tarixi, RAG      ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from config import config, MEMORY_DIR
from utils import logger, safe_execute, retry

# ChromaDB import
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB o'rnatilmagan! Xotira tizimi cheklangan.")


class ConversationMemory:
    """Qisqa muddatli suhbat xotirasi (session ichida)"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.messages: List[Dict] = []
        self.session_start = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Xabar qo'shish"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Maksimal tarixdan oshsa, eski xabarlarni o'chirish
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context(self, last_n: int = 10) -> List[Dict]:
        """Oxirgi n ta xabarni olish (AI kontekst uchun)"""
        return self.messages[-last_n:]
    
    def get_formatted_history(self, last_n: int = 10) -> str:
        """Formatlangan suhbat tarixini olish"""
        history = self.get_context(last_n)
        formatted = []
        for msg in history:
            role = "Sarvar" if msg["role"] == "user" else "Yordamchi"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def clear(self):
        """Suhbat tarixini tozalash"""
        self.messages.clear()
    
    def get_message_count(self) -> int:
        """Xabarlar sonini olish"""
        return len(self.messages)


class LongTermMemory:
    """
    Uzoq muddatli xotira - ChromaDB bilan.
    Foydalanuvchining ma'lumotlari, eslatmalari, afzalliklari saqlanadi.
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialized = False
        
        if CHROMADB_AVAILABLE:
            self._initialize()
    
    @safe_execute(fallback_value=None)
    def _initialize(self):
        """ChromaDB ni ishga tushirish"""
        persist_dir = str(MEMORY_DIR / "chromadb")
        
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_or_create_collection(
            name=config.memory.collection_name,
            metadata={"description": "Yordamchi shaxsiy xotira"}
        )
        
        self._initialized = True
        logger.info(f"Xotira tizimi tayyor. "
                   f"Saqlangan: {self.collection.count()} yozuv")
    
    @safe_execute(fallback_value=False)
    def store(self, content: str, category: str = "general",
              metadata: Dict = None, importance: int = 5) -> bool:
        """
        Ma'lumotni xotiraga saqlash.
        
        Args:
            content: Saqlanadigan matn
            category: Kategoriya (general, personal, task, note, preference)
            metadata: Qo'shimcha ma'lumot
            importance: Muhimlik darajasi (1-10)
        """
        if not self._initialized:
            return False
        
        doc_id = f"mem_{int(time.time() * 1000)}"
        
        meta = {
            "category": category,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "user": config.user_name,
        }
        if metadata:
            meta.update(metadata)
        
        self.collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id]
        )
        
        logger.debug(f"Xotiraga saqlandi: [{category}] {content[:50]}...")
        return True
    
    @safe_execute(fallback_value=[])
    def search(self, query: str, n_results: int = 5,
               category: Optional[str] = None) -> List[Dict]:
        """
        Xotiradan qidirish (semantik).
        
        Args:
            query: Qidiruv so'rovi
            n_results: Natijalar soni
            category: Kategoriya filtri
        """
        if not self._initialized:
            return []
        
        where_filter = None
        if category:
            where_filter = {"category": category}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, config.memory.max_results),
            where=where_filter
        )
        
        memories = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                }
                memories.append(memory)
        
        return memories
    
    @safe_execute(fallback_value="")
    def get_relevant_context(self, query: str, max_tokens: int = 500) -> str:
        """AI uchun tegishli kontekstni olish"""
        memories = self.search(query, n_results=3)
        
        if not memories:
            return ""
        
        context_parts = ["[Xotiradan topilgan tegishli ma'lumotlar:]"]
        for mem in memories:
            cat = mem['metadata'].get('category', 'general')
            content = mem['content']
            context_parts.append(f"- [{cat}] {content}")
        
        context = "\n".join(context_parts)
        # Token limitini taxminiy cheklash
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4]
        
        return context
    
    @safe_execute(fallback_value=0)
    def count(self) -> int:
        """Xotiradagi yozuvlar sonini olish"""
        if not self._initialized:
            return 0
        return self.collection.count()
    
    @safe_execute(fallback_value=False)
    def delete(self, doc_id: str) -> bool:
        """Yozuvni o'chirish"""
        if not self._initialized:
            return False
        self.collection.delete(ids=[doc_id])
        return True
    
    @safe_execute(fallback_value=[])
    def get_all_by_category(self, category: str) -> List[Dict]:
        """Kategoriya bo'yicha barcha yozuvlarni olish"""
        if not self._initialized:
            return []
        
        results = self.collection.get(
            where={"category": category}
        )
        
        memories = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                memories.append({
                    "id": results['ids'][i],
                    "content": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                })
        
        return memories


class UserProfile:
    """Foydalanuvchi profili - odatlar, afzalliklar"""
    
    def __init__(self):
        self.profile_file = MEMORY_DIR / "user_profile.json"
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Profilni yuklash"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "name": config.user_name,
            "preferences": {},
            "habits": {},
            "important_dates": {},
            "frequent_tasks": [],
            "mood_history": [],
            "interaction_count": 0,
            "created_at": datetime.now().isoformat()
        }
    
    def save(self):
        """Profilni saqlash"""
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Profil saqlashda xatolik: {e}")
    
    def update_preference(self, key: str, value):
        """Afzallikni yangilash"""
        self.data["preferences"][key] = value
        self.save()
    
    def add_habit(self, habit_name: str, time_pattern: str):
        """Odatni qo'shish"""
        self.data["habits"][habit_name] = {
            "pattern": time_pattern,
            "last_triggered": None
        }
        self.save()
    
    def log_interaction(self, mood: str = "neutral"):
        """Muloqotni qayd qilish"""
        self.data["interaction_count"] += 1
        self.data["mood_history"].append({
            "mood": mood,
            "time": datetime.now().isoformat()
        })
        # Oxirgi 100 ta mood ni saqlash
        self.data["mood_history"] = self.data["mood_history"][-100:]
        self.save()
    
    def get_summary(self) -> str:
        """Profil xulosasini olish"""
        return (
            f"Foydalanuvchi: {self.data['name']}\n"
            f"Muloqotlar soni: {self.data['interaction_count']}\n"
            f"Afzalliklar: {len(self.data['preferences'])} ta\n"
            f"Odatlar: {len(self.data['habits'])} ta"
        )


class MemoryManager:
    """Barcha xotira tizimlarini boshqaruvchi asosiy klass"""
    
    def __init__(self):
        self.conversation = ConversationMemory()
        self.long_term = LongTermMemory()
        self.user_profile = UserProfile()
        logger.info("Xotira menejeri ishga tushdi")
    
    def remember(self, content: str, category: str = "general", 
                 importance: int = 5) -> bool:
        """Nimanidir eslab qolish"""
        return self.long_term.store(content, category, importance=importance)
    
    def recall(self, query: str, n_results: int = 5) -> List[Dict]:
        """Nimanidir eslash"""
        return self.long_term.search(query, n_results)
    
    def add_to_conversation(self, role: str, content: str):
        """Suhbatga qo'shish"""
        self.conversation.add_message(role, content)
    
    def get_ai_context(self, current_query: str) -> str:
        """AI uchun to'liq kontekst tayyorlash"""
        parts = []
        
        # Suhbat tarixi
        history = self.conversation.get_formatted_history(last_n=6)
        if history:
            parts.append(f"[Suhbat tarixi:]\n{history}")
        
        # Xotiradan tegishli ma'lumot
        memory_context = self.long_term.get_relevant_context(current_query)
        if memory_context:
            parts.append(memory_context)
        
        return "\n\n".join(parts)
    
    def get_stats(self) -> Dict:
        """Xotira statistikasini olish"""
        return {
            "conversation_messages": self.conversation.get_message_count(),
            "long_term_memories": self.long_term.count(),
            "user_interactions": self.user_profile.data.get("interaction_count", 0)
        }
