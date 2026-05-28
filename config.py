"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Konfiguratsiya Moduli                 ║
║     Barcha sozlamalar va standart qiymatlar shu yerda       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

# ===== YO'LLAR =====
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"
FACES_DIR = DATA_DIR / "faces"
CONFIG_FILE = DATA_DIR / "config.json"

# Papkalarni yaratish
for d in [DATA_DIR, MEMORY_DIR, FACES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class VoiceConfig:
    """Ovoz sozlamalari"""
    language: str = "uz"
    rate: int = 165
    volume: float = 0.9
    voice_id: Optional[str] = None
    wake_words: List[str] = field(default_factory=lambda: [
        "yordamchi", "salom yordamchi", "jarvis"
    ])
    listen_timeout: int = 5
    phrase_timeout: int = 10
    energy_threshold: int = 300


@dataclass
class AIConfig:
    """AI sozlamalari"""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ollama_model: str = "llama3.1"
    ollama_host: str = "http://localhost:11434"
    use_offline: bool = False
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = (
        "Sen Yordamchi - Sarvarning shaxsiy AI yordamchisisan. "
        "Sen o'zbek tilida gaplashasan. Sen juda aqlli, hazilkash, "
        "va doimo yordam berishga tayyorsan. Sarvarni hurmat qilasan "
        "va uning barcha savollariga aniq, tushunarli javob berasan. "
        "Sen Iron Man dagi JARVIS kabi akllisan va professional."
    )


@dataclass
class GUIConfig:
    """Interfeys sozlamalari"""
    # Asosiy ranglar
    primary_color: str = "#00f5ff"       # Neon cyan
    secondary_color: str = "#7b2ff7"     # Neon purple
    accent_color: str = "#ff006e"        # Neon pink
    background_color: str = "#0a0e1a"    # Dark space blue
    surface_color: str = "#141829"       # Slightly lighter
    text_color: str = "#e0e6ff"          # Light blue-white
    success_color: str = "#00ff88"       # Neon green
    warning_color: str = "#ffaa00"       # Amber
    error_color: str = "#ff3366"         # Red-pink
    
    # Gradient ranglar
    gradient_start: str = "#667eea"
    gradient_end: str = "#764ba2"
    
    # Oyna sozlamalari
    window_width: int = 1400
    window_height: int = 850
    opacity: float = 0.95
    borderless: bool = True
    always_on_top: bool = False
    
    # Animatsiya
    particle_count: int = 80
    animation_speed: float = 1.0
    enable_particles: bool = True
    enable_scanlines: bool = True
    enable_glow: bool = True
    
    # Tema
    theme: str = "cyberpunk"  # cyberpunk, holographic, minimal


@dataclass
class AgentsConfig:
    """Multi-Agent sozlamalari"""
    enable_research: bool = True
    enable_coding: bool = True
    enable_vision: bool = True
    enable_personal: bool = True
    max_steps: int = 10
    auto_mode: bool = False


@dataclass
class MemoryConfig:
    """Xotira sozlamalari"""
    collection_name: str = "yordamchi_memory"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_results: int = 5
    auto_save: bool = True


@dataclass
class AutomationConfig:
    """Avtomatlashtirish sozlamalari"""
    enable_browser: bool = True
    enable_files: bool = True
    enable_apps: bool = True
    browser_path: str = ""
    safe_mode: bool = True  # Xavfli amallardan oldin so'rash


@dataclass
class AppConfig:
    """Asosiy dastur konfiguratsiyasi"""
    user_name: str = "Sarvar"
    app_name: str = "Yordamchi"
    version: str = "2.0.0"
    first_run: bool = True
    
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    
    def save(self):
        """Konfiguratsiyani faylga saqlash"""
        config_dict = asdict(self)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """Konfiguratsiyani fayldan yuklash"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                config = cls()
                config.user_name = data.get('user_name', 'Sarvar')
                config.app_name = data.get('app_name', 'Yordamchi')
                config.version = data.get('version', '2.0.0')
                config.first_run = data.get('first_run', True)
                
                # Voice config
                if 'voice' in data:
                    config.voice = VoiceConfig(**{
                        k: v for k, v in data['voice'].items()
                        if k in VoiceConfig.__dataclass_fields__
                    })
                
                # AI config
                if 'ai' in data:
                    config.ai = AIConfig(**{
                        k: v for k, v in data['ai'].items()
                        if k in AIConfig.__dataclass_fields__
                    })
                
                # GUI config
                if 'gui' in data:
                    config.gui = GUIConfig(**{
                        k: v for k, v in data['gui'].items()
                        if k in GUIConfig.__dataclass_fields__
                    })
                
                # Agents config
                if 'agents' in data:
                    config.agents = AgentsConfig(**{
                        k: v for k, v in data['agents'].items()
                        if k in AgentsConfig.__dataclass_fields__
                    })
                
                # Memory config
                if 'memory' in data:
                    config.memory = MemoryConfig(**{
                        k: v for k, v in data['memory'].items()
                        if k in MemoryConfig.__dataclass_fields__
                    })
                
                # Automation config
                if 'automation' in data:
                    config.automation = AutomationConfig(**{
                        k: v for k, v in data['automation'].items()
                        if k in AutomationConfig.__dataclass_fields__
                    })
                
                return config
            except Exception as e:
                print(f"[CONFIG] Xatolik: {e}, standart sozlamalar ishlatilmoqda")
                return cls()
        return cls()


# Global config instance
config = AppConfig.load()
