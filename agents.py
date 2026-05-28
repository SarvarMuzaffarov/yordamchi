"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Multi-Agent Tizimi                    ║
║   Research, Coding, Vision, Personal agentlar               ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import threading
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Callable, Any
from enum import Enum
from dataclasses import dataclass

from config import config
from utils import logger, safe_execute, is_internet_available


class AgentStatus(Enum):
    """Agent holati"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentTask:
    """Agent vazifasi"""
    description: str
    priority: int = 5
    context: Dict = None
    result: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    steps_completed: int = 0
    total_steps: int = 0


class BaseAgent(ABC):
    """Barcha agentlar uchun asos klass"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        
    @abstractmethod
    def execute(self, task: AgentTask, ai_func: Callable) -> str:
        """Vazifani bajarish"""
        pass
    
    def report_progress(self, step: int, total: int, message: str):
        """Progressni xabardor qilish"""
        if self.current_task:
            self.current_task.steps_completed = step
            self.current_task.total_steps = total
        if self.on_progress:
            self.on_progress(self.name, step, total, message)
    
    def get_status_text(self) -> str:
        """Holatni matn sifatida olish"""
        if self.status == AgentStatus.WORKING and self.current_task:
            return (f"{self.name}: {self.current_task.steps_completed}/"
                   f"{self.current_task.total_steps} qadam")
        return f"{self.name}: {self.status.value}"


class ResearchAgent(BaseAgent):
    """
    Tadqiqot agenti - internetdan ma'lumot qidirish,
    maqolalar tahlil qilish, ma'lumot yig'ish.
    """
    
    def __init__(self):
        super().__init__(
            "Research Agent",
            "Internetdan ma'lumot qidirish va tahlil qilish"
        )
    
    def execute(self, task: AgentTask, ai_func: Callable) -> str:
        """Tadqiqot vazifasini bajarish"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            steps = [
                "Ma'lumot manbalarini aniqlash",
                "Qidiruv natijalarini tahlil qilish",
                "Tegishli ma'lumotlarni ajratish",
                "Xulosa tayyorlash"
            ]
            
            results = []
            
            for i, step in enumerate(steps, 1):
                self.report_progress(i, len(steps), step)
                
                prompt = (
                    f"Sen Research Agent san. Vazifa: {task.description}\n"
                    f"Hozirgi qadam ({i}/{len(steps)}): {step}\n"
                    f"Oldingi natijalar: {results[-1] if results else 'yo`q'}\n"
                    f"Faqat shu qadamni bajaring va natijani bering."
                )
                
                result = ai_func(prompt)
                results.append(result)
                time.sleep(0.5)
            
            # Yakuniy xulosa
            final_prompt = (
                f"Quyidagi tadqiqot natijalarini birlashtir va "
                f"Sarvar uchun qisqa, tushunarli xulosa yoz:\n\n"
                f"Vazifa: {task.description}\n"
                f"Natijalar:\n" + "\n---\n".join(results)
            )
            
            final_result = ai_func(final_prompt)
            
            self.status = AgentStatus.COMPLETED
            task.status = AgentStatus.COMPLETED
            task.result = final_result
            
            if self.on_complete:
                self.on_complete(self.name, final_result)
            
            return final_result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            task.status = AgentStatus.ERROR
            logger.error(f"Research Agent xatolik: {e}")
            return f"Tadqiqotda xatolik: {str(e)}"


class CodingAgent(BaseAgent):
    """
    Kodlash agenti - kod yozish, tuzatish, tahlil qilish,
    optimizatsiya va debugging.
    """
    
    def __init__(self):
        super().__init__(
            "Coding Agent",
            "Kod yozish, tuzatish va optimizatsiya"
        )
    
    def execute(self, task: AgentTask, ai_func: Callable) -> str:
        """Kodlash vazifasini bajarish"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            steps = [
                "Vazifani tahlil qilish va rejalashtirish",
                "Kod yozish",
                "Kodni tekshirish va optimizatsiya",
                "Dokumentatsiya va tushuntirish"
            ]
            
            results = []
            
            for i, step in enumerate(steps, 1):
                self.report_progress(i, len(steps), step)
                
                prompt = (
                    f"Sen professional Coding Agent san. "
                    f"Vazifa: {task.description}\n"
                    f"Hozirgi qadam ({i}/{len(steps)}): {step}\n"
                    f"{'Oldingi kod: ' + results[-1][:500] if results else ''}\n"
                    f"Professional, toza va kommentariyli kod yoz."
                )
                
                if task.context and 'code' in task.context:
                    prompt += f"\n\nMavjud kod:\n```\n{task.context['code']}\n```"
                
                result = ai_func(prompt)
                results.append(result)
                time.sleep(0.3)
            
            final_result = results[-1] if results else "Kod yaratilmadi"
            
            self.status = AgentStatus.COMPLETED
            task.status = AgentStatus.COMPLETED
            task.result = final_result
            
            if self.on_complete:
                self.on_complete(self.name, final_result)
            
            return final_result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Coding Agent xatolik: {e}")
            return f"Kodlashda xatolik: {str(e)}"


class VisionAgent(BaseAgent):
    """
    Ko'rish agenti - rasmlarni tahlil qilish,
    kamera orqali ko'rish, OCR.
    """
    
    def __init__(self):
        super().__init__(
            "Vision Agent",
            "Rasmlarni ko'rish va tahlil qilish"
        )
    
    def execute(self, task: AgentTask, ai_func: Callable) -> str:
        """Ko'rish vazifasini bajarish"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            self.report_progress(1, 3, "Tasvirni olish")
            
            # Agar rasm berilgan bo'lsa
            image_data = None
            if task.context and 'image' in task.context:
                image_data = task.context['image']
            
            self.report_progress(2, 3, "Tasvirni tahlil qilish")
            
            prompt = (
                f"Sen Vision Agent san. Vazifa: {task.description}\n"
                f"Tasvirni batafsil tavsiflang va tahlil qiling."
            )
            
            result = ai_func(prompt)
            
            self.report_progress(3, 3, "Natijani tayyorlash")
            
            self.status = AgentStatus.COMPLETED
            task.status = AgentStatus.COMPLETED
            task.result = result
            
            if self.on_complete:
                self.on_complete(self.name, result)
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Vision Agent xatolik: {e}")
            return f"Ko'rishda xatolik: {str(e)}"


class PersonalAgent(BaseAgent):
    """
    Shaxsiy agent - kundalik rejalar, eslatmalar,
    shaxsiy maslahatlar, motivatsiya.
    """
    
    def __init__(self):
        super().__init__(
            "Personal Agent",
            "Shaxsiy yordam, rejalar va eslatmalar"
        )
    
    def execute(self, task: AgentTask, ai_func: Callable) -> str:
        """Shaxsiy vazifani bajarish"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            self.report_progress(1, 2, "Vazifani tahlil qilish")
            
            prompt = (
                f"Sen Personal Agent san - Sarvarning shaxsiy yordamchisi. "
                f"Vazifa: {task.description}\n"
                f"Sarvarning odatlari va afzalliklarini hisobga olib, "
                f"shaxsiy va foydali javob ber. "
                f"Motivatsiya va ijobiy ton ishlatib, yordam ber."
            )
            
            result = ai_func(prompt)
            
            self.report_progress(2, 2, "Tayyor")
            
            self.status = AgentStatus.COMPLETED
            task.status = AgentStatus.COMPLETED
            task.result = result
            
            if self.on_complete:
                self.on_complete(self.name, result)
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Personal Agent xatolik: {e}")
            return f"Shaxsiy agentda xatolik: {str(e)}"


class AgentOrchestrator:
    """
    Agent orkestrator - agentlarni boshqaradi,
    vazifalarni to'g'ri agentga yo'naltiradi.
    """
    
    def __init__(self, ai_think_func: Callable):
        self.ai_think = ai_think_func
        
        # Agentlar
        self.agents = {
            "research": ResearchAgent(),
            "coding": CodingAgent(),
            "vision": VisionAgent(),
            "personal": PersonalAgent(),
        }
        
        # Callbacks
        self.on_agent_start: Optional[Callable] = None
        self.on_agent_progress: Optional[Callable] = None
        self.on_agent_complete: Optional[Callable] = None
        
        # Agent callbacklarini ulash
        for agent in self.agents.values():
            agent.on_progress = self._handle_progress
            agent.on_complete = self._handle_complete
        
        logger.info("Agent orkestrator tayyor")
    
    def classify_task(self, user_input: str) -> str:
        """
        Foydalanuvchi so'rovini tahlil qilib, 
        qaysi agent bajarishini aniqlash.
        """
        input_lower = user_input.lower()
        
        # Kodlash
        code_keywords = [
            "kod", "code", "dastur", "program", "funksiya", "function",
            "xatolik", "bug", "debug", "python", "javascript", "html",
            "yoz", "tuzat", "optimallashtir", "class", "api"
        ]
        if any(kw in input_lower for kw in code_keywords):
            return "coding"
        
        # Tadqiqot
        research_keywords = [
            "qidir", "izla", "top", "ma'lumot", "nima", "kim",
            "qachon", "qayerda", "necha", "qancha", "tarix",
            "yangilik", "texnologiya", "tadqiqot"
        ]
        if any(kw in input_lower for kw in research_keywords):
            return "research"
        
        # Ko'rish
        vision_keywords = [
            "ko'r", "rasm", "tasvir", "kamera", "surat", "skrinshot",
            "ekran", "o'qi", "tanib", "yuz"
        ]
        if any(kw in input_lower for kw in vision_keywords):
            return "vision"
        
        # Shaxsiy
        personal_keywords = [
            "reja", "eslatma", "remind", "schedule", "kundalik",
            "motivatsiya", "maslahat", "yordam", "kayfiyat", "his"
        ]
        if any(kw in input_lower for kw in personal_keywords):
            return "personal"
        
        # Default - oddiy savol (agentsiz)
        return "none"
    
    def execute_task(self, user_input: str, context: Dict = None,
                     force_agent: str = None) -> Optional[str]:
        """
        Vazifani bajarish.
        
        Args:
            user_input: Foydalanuvchi so'rovi
            context: Qo'shimcha kontekst
            force_agent: Majburiy agent tanlash
            
        Returns:
            Agent natijasi yoki None (agent kerak emas)
        """
        # Agentni aniqlash
        agent_name = force_agent or self.classify_task(user_input)
        
        if agent_name == "none":
            return None  # Oddiy savol, agent kerak emas
        
        if agent_name not in self.agents:
            return None
        
        agent = self.agents[agent_name]
        
        # Vazifa yaratish
        task = AgentTask(
            description=user_input,
            context=context or {}
        )
        
        # Agent ishga tushganini xabardor qilish
        if self.on_agent_start:
            self.on_agent_start(agent_name, agent.description)
        
        logger.info(f"Agent ishga tushdi: {agent_name} - {user_input[:50]}...")
        
        # Vazifani bajarish (alohida thread da)
        result = agent.execute(task, self._agent_ai_call)
        
        return result
    
    def execute_task_async(self, user_input: str, context: Dict = None,
                           callback: Callable = None):
        """Vazifani asinxron bajarish"""
        def _run():
            result = self.execute_task(user_input, context)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
    
    def _agent_ai_call(self, prompt: str) -> str:
        """Agent uchun AI chaqiruvi"""
        return self.ai_think(prompt, stream=False)
    
    def _handle_progress(self, agent_name: str, step: int, 
                         total: int, message: str):
        """Agent progressini boshqarish"""
        if self.on_agent_progress:
            self.on_agent_progress(agent_name, step, total, message)
    
    def _handle_complete(self, agent_name: str, result: str):
        """Agent tugaganini boshqarish"""
        if self.on_agent_complete:
            self.on_agent_complete(agent_name, result)
    
    def get_all_statuses(self) -> Dict[str, str]:
        """Barcha agentlar holatini olish"""
        return {
            name: agent.get_status_text()
            for name, agent in self.agents.items()
        }
    
    def is_any_working(self) -> bool:
        """Biror agent ishlayotganini tekshirish"""
        return any(
            agent.status == AgentStatus.WORKING
            for agent in self.agents.values()
        )
