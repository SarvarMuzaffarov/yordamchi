"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ██╗   ██╗ ██████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗ ██████╗  ║
║     ╚██╗ ██╔╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗████╗ ████║██╔════╝  ║
║      ╚████╔╝ ██║   ██║██████╔╝██║  ██║███████║██╔████╔██║██║       ║
║       ╚██╔╝  ██║   ██║██╔══██╗██║  ██║██╔══██║██║╚██╔╝██║██║       ║
║        ██║   ╚██████╔╝██║  ██║██████╔╝██║  ██║██║ ╚═╝ ██║╚██████╗  ║
║        ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝  ║
║                                                                      ║
║              Futuristik AI Yordamchi v2.0                            ║
║              Yaratuvchi: Sarvar                                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import threading
from typing import Optional

# Path ni to'g'rilash
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, AppConfig
from utils import logger, get_greeting, dispatcher
from system_monitor import SystemMonitor
from memory import MemoryManager



class YordamchiApp:
    """
    Asosiy dastur sinfi.
    Barcha modullarni birlashtiradi va boshqaradi.
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("  YORDAMCHI AI Assistant v2.0 ishga tushmoqda...")
        logger.info("=" * 60)

        # Core components
        self.memory: Optional[MemoryManager] = None
        self.brain = None
        self.voice = None
        self.agents = None
        self.automation = None
        self.vision_engine = None
        self.system_monitor: Optional[SystemMonitor] = None
        self.window = None
        self.app = None

        # Initialize
        self._init_core()

    def _init_core(self):
        """Asosiy komponentlarni ishga tushirish"""
        # 1. Xotira tizimi
        logger.info("[1/6] Xotira tizimi...")
        self.memory = MemoryManager()

        # 2. AI Brain
        logger.info("[2/6] AI miya...")
        from brain import AIBrain
        self.brain = AIBrain(self.memory)

        # 3. Voice Engine
        logger.info("[3/6] Ovoz tizimi...")
        from voice import VoiceEngine
        self.voice = VoiceEngine()
        self.voice.on_text_recognized = self._on_voice_input
        self.voice.on_wake_word = self._on_wake_word

        # 4. Agent System
        logger.info("[4/6] Agent tizimi...")
        from agents import AgentOrchestrator
        self.agents = AgentOrchestrator(self.brain.think)

        # 5. Automation
        logger.info("[5/6] Avtomatlashtirish...")
        from automation import ComputerAutomation
        self.automation = ComputerAutomation()

        # 6. System Monitor
        logger.info("[6/6] Tizim monitoringi...")
        self.system_monitor = SystemMonitor(update_interval=2.0)

        logger.info("Barcha komponentlar tayyor! ✅")

    def _on_voice_input(self, text: str):
        """Ovozdan matn kelganda"""
        logger.info(f"Ovoz kiritdi: {text}")
        if self.window:
            self.window.set_listening_state(False)
            self.window.mission_log.add_message(f"👤 {text}", is_user=True)
        self._process_input(text)

    def _on_wake_word(self, text: str):
        """Wake word aniqlanganda"""
        logger.info(f"Wake word: {text}")
        if self.window:
            self.window.set_listening_state(True)

    def _process_input(self, text: str):
        """Foydalanuvchi kiritmasini qayta ishlash"""
        if not text.strip():
            return

        # Threading bilan AI javobini olish
        def _get_response():
            try:
                if self.window:
                    self.window.set_thinking_state(True)

                # Tezkor javobni tekshirish
                quick = self.brain.quick_response(text)
                if quick:
                    self._deliver_response(quick)
                    return

                # Avtomatlashtirish buyrug'ini tekshirish
                auto_result = self.automation.parse_and_execute(text)
                if auto_result:
                    self._deliver_response(auto_result)
                    return

                # Agent yoki to'g'ridan-to'g'ri AI
                agent_result = self.agents.execute_task(text)
                if agent_result:
                    self._deliver_response(agent_result)
                else:
                    # Tizim konteksti
                    context = ""
                    if self.system_monitor:
                        alert = self.system_monitor.get_alert()
                        if alert:
                            context = f"Tizim ogohlantirishlari: {alert}"

                    response = self.brain.think(text, context=context)
                    self._deliver_response(response)

            except Exception as e:
                logger.error(f"Process input xatolik: {e}")
                self._deliver_response(f"Xatolik yuz berdi: {str(e)}")

        thread = threading.Thread(target=_get_response, daemon=True)
        thread.start()

    def _deliver_response(self, text: str):
        """Javobni foydalanuvchiga yetkazish"""
        if self.window:
            self.window.set_thinking_state(False)
            self.window.show_response(text)

        # Ovozli javob
        if self.voice:
            self.voice.speak(text)

    def _on_system_stats_update(self, stats):
        """Tizim statistikasi yangilanganda"""
        if self.window:
            self.window.update_system_display(stats)

    def run(self):
        """Dasturni ishga tushirish"""
        from PyQt6.QtWidgets import QApplication
        from gui import YordamchiWindow
        from settings import FirstRunWizard

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Yordamchi")

        # Birinchi ishga tushirish
        if config.first_run:
            wizard = FirstRunWizard()
            if wizard.exec() != wizard.DialogCode.Accepted:
                logger.info("Foydalanuvchi bekor qildi")
                sys.exit(0)

        # Asosiy oyna
        self.window = YordamchiWindow()
        self.window.request_ai_response.connect(self._process_input)

        # System monitor
        self.system_monitor.add_callback(self._on_system_stats_update)
        self.system_monitor.start()

        # Voice (continuous listening)
        # self.voice.start_listening(continuous=True)

        # Show window
        self.window.show()
        logger.info(f"🚀 {get_greeting()}, {config.user_name}! Yordamchi tayyor.")

        # Run
        exit_code = self.app.exec()

        # Cleanup
        self._cleanup()
        sys.exit(exit_code)

    def _cleanup(self):
        """Resurslarni tozalash"""
        logger.info("Dastur yopilmoqda...")
        if self.system_monitor:
            self.system_monitor.stop()
        if self.voice:
            self.voice.cleanup()
        config.save()
        logger.info("Yordamchi to'xtatildi. Xayr! 👋")


# ===== ENTRY POINT =====
if __name__ == "__main__":
    try:
        app = YordamchiApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Ctrl+C - Dastur to'xtatildi")
    except Exception as e:
        logger.critical(f"Kritik xatolik: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
