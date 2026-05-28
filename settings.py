"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Sozlamalar Oynasi                     ║
║    API kalit, ovoz, tema, agentlar sozlamalari              ║
╚══════════════════════════════════════════════════════════════╝
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFormLayout, QSlider,
    QCheckBox, QComboBox, QGroupBox, QSpinBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import config
from utils import logger


class SettingsWindow(QDialog):
    """Sozlamalar oynasi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ YORDAMCHI - Sozlamalar")
        self.setMinimumSize(650, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0e1a;
                color: #e0e6ff;
            }
            QTabWidget::pane {
                background: #141829;
                border: 1px solid rgba(0,245,255,40);
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #141829;
                color: #8c96b4;
                padding: 10px 20px;
                border: 1px solid transparent;
                border-radius: 6px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(0,245,255,20);
                color: #00f5ff;
                border: 1px solid rgba(0,245,255,60);
            }
            QGroupBox {
                color: #00f5ff;
                border: 1px solid rgba(0,245,255,30);
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background: #1a1f35;
                color: #e0e6ff;
                border: 1px solid rgba(0,245,255,40);
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #00f5ff;
            }
            QPushButton {
                background: rgba(0,245,255,20);
                color: #00f5ff;
                border: 1px solid rgba(0,245,255,60);
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0,245,255,40);
            }
            QCheckBox {
                color: #e0e6ff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid rgba(0,245,255,60);
                background: #1a1f35;
            }
            QCheckBox::indicator:checked {
                background: #00f5ff;
            }
            QSlider::groove:horizontal {
                background: #1a1f35;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00f5ff;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QLabel {
                color: #e0e6ff;
            }
        """)
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("⚙️ SOZLAMALAR")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00f5ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_ai_tab(), "🤖 AI")
        tabs.addTab(self._create_voice_tab(), "🎤 Ovoz")
        tabs.addTab(self._create_gui_tab(), "🎨 Interfeys")
        tabs.addTab(self._create_agents_tab(), "🔧 Agentlar")
        tabs.addTab(self._create_general_tab(), "📋 Umumiy")
        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Saqlash")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Bekor")
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(255,51,102,20); 
                color: #ff3366; 
                border-color: rgba(255,51,102,60); 
            }
        """)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)


    def _create_ai_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Gemini API kalitingizni kiriting...")
        layout.addRow("🔑 Gemini API Key:", self.api_key_input)

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"
        ])
        layout.addRow("🧠 Model:", self.model_combo)

        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText("llama3.1")
        layout.addRow("🦙 Ollama Model:", self.ollama_model)

        self.temperature = QSlider(Qt.Orientation.Horizontal)
        self.temperature.setRange(0, 100)
        self.temperature.setValue(70)
        layout.addRow("🌡 Temperatura:", self.temperature)

        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(256, 8192)
        self.max_tokens.setValue(4096)
        layout.addRow("📝 Max tokens:", self.max_tokens)

        return tab

    def _create_voice_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.voice_rate = QSlider(Qt.Orientation.Horizontal)
        self.voice_rate.setRange(80, 300)
        self.voice_rate.setValue(165)
        layout.addRow("⏩ Tezlik:", self.voice_rate)

        self.voice_volume = QSlider(Qt.Orientation.Horizontal)
        self.voice_volume.setRange(0, 100)
        self.voice_volume.setValue(90)
        layout.addRow("🔊 Ovoz balandligi:", self.voice_volume)

        self.wake_word_input = QLineEdit()
        self.wake_word_input.setPlaceholderText("yordamchi, jarvis")
        layout.addRow("🗣 Wake Words:", self.wake_word_input)

        self.energy_threshold = QSpinBox()
        self.energy_threshold.setRange(100, 5000)
        self.energy_threshold.setValue(300)
        layout.addRow("📊 Sezgirlik:", self.energy_threshold)

        return tab

    def _create_gui_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.particles_check = QCheckBox("Zarralar animatsiyasi")
        layout.addRow(self.particles_check)

        self.scanlines_check = QCheckBox("Scanline effekti")
        layout.addRow(self.scanlines_check)

        self.glow_check = QCheckBox("Neon glow")
        layout.addRow(self.glow_check)

        self.particle_count = QSpinBox()
        self.particle_count.setRange(10, 200)
        self.particle_count.setValue(80)
        layout.addRow("✨ Zarralar soni:", self.particle_count)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["cyberpunk", "holographic", "minimal"])
        layout.addRow("🎨 Tema:", self.theme_combo)

        return tab

    def _create_agents_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.research_check = QCheckBox("🔍 Research Agent")
        self.coding_check = QCheckBox("💻 Coding Agent")
        self.vision_check = QCheckBox("👁 Vision Agent")
        self.personal_check = QCheckBox("👤 Personal Agent")

        layout.addWidget(self.research_check)
        layout.addWidget(self.coding_check)
        layout.addWidget(self.vision_check)
        layout.addWidget(self.personal_check)

        self.auto_agent = QCheckBox("🤖 Avtomatik agent tanlash")
        layout.addWidget(self.auto_agent)
        layout.addStretch()

        return tab

    def _create_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.user_name_input = QLineEdit()
        layout.addRow("👤 Ismingiz:", self.user_name_input)

        self.safe_mode_check = QCheckBox("Xavfsiz rejim (xavfli buyruqlarni bloklash)")
        layout.addRow(self.safe_mode_check)

        self.auto_save_check = QCheckBox("Avtomatik saqlash")
        layout.addRow(self.auto_save_check)

        return tab


    def _load_current_settings(self):
        """Joriy sozlamalarni yuklash"""
        # AI
        self.api_key_input.setText(config.ai.gemini_api_key)
        self.model_combo.setCurrentText(config.ai.gemini_model)
        self.ollama_model.setText(config.ai.ollama_model)
        self.temperature.setValue(int(config.ai.temperature * 100))
        self.max_tokens.setValue(config.ai.max_tokens)

        # Voice
        self.voice_rate.setValue(config.voice.rate)
        self.voice_volume.setValue(int(config.voice.volume * 100))
        self.wake_word_input.setText(", ".join(config.voice.wake_words))
        self.energy_threshold.setValue(config.voice.energy_threshold)

        # GUI
        self.particles_check.setChecked(config.gui.enable_particles)
        self.scanlines_check.setChecked(config.gui.enable_scanlines)
        self.glow_check.setChecked(config.gui.enable_glow)
        self.particle_count.setValue(config.gui.particle_count)
        self.theme_combo.setCurrentText(config.gui.theme)

        # Agents
        self.research_check.setChecked(config.agents.enable_research)
        self.coding_check.setChecked(config.agents.enable_coding)
        self.vision_check.setChecked(config.agents.enable_vision)
        self.personal_check.setChecked(config.agents.enable_personal)
        self.auto_agent.setChecked(config.agents.auto_mode)

        # General
        self.user_name_input.setText(config.user_name)
        self.safe_mode_check.setChecked(config.automation.safe_mode)
        self.auto_save_check.setChecked(config.memory.auto_save)

    def _save_settings(self):
        """Sozlamalarni saqlash"""
        # AI
        config.ai.gemini_api_key = self.api_key_input.text().strip()
        config.ai.gemini_model = self.model_combo.currentText()
        config.ai.ollama_model = self.ollama_model.text().strip()
        config.ai.temperature = self.temperature.value() / 100.0
        config.ai.max_tokens = self.max_tokens.value()

        # Voice
        config.voice.rate = self.voice_rate.value()
        config.voice.volume = self.voice_volume.value() / 100.0
        wake_words = [w.strip() for w in self.wake_word_input.text().split(",") if w.strip()]
        config.voice.wake_words = wake_words or ["yordamchi"]
        config.voice.energy_threshold = self.energy_threshold.value()

        # GUI
        config.gui.enable_particles = self.particles_check.isChecked()
        config.gui.enable_scanlines = self.scanlines_check.isChecked()
        config.gui.enable_glow = self.glow_check.isChecked()
        config.gui.particle_count = self.particle_count.value()
        config.gui.theme = self.theme_combo.currentText()

        # Agents
        config.agents.enable_research = self.research_check.isChecked()
        config.agents.enable_coding = self.coding_check.isChecked()
        config.agents.enable_vision = self.vision_check.isChecked()
        config.agents.enable_personal = self.personal_check.isChecked()
        config.agents.auto_mode = self.auto_agent.isChecked()

        # General
        config.user_name = self.user_name_input.text().strip() or "Sarvar"
        config.automation.safe_mode = self.safe_mode_check.isChecked()
        config.memory.auto_save = self.auto_save_check.isChecked()

        # First run off
        config.first_run = False

        config.save()
        logger.info("Sozlamalar saqlandi")
        self.close()


class FirstRunWizard(QDialog):
    """Birinchi marta ishga tushirganda konfiguratsiya oynasi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚀 YORDAMCHI - Xush kelibsiz!")
        self.setFixedSize(550, 450)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0a0e1a, stop:1 #141829);
                color: #e0e6ff;
            }
            QLabel { color: #e0e6ff; }
            QLineEdit {
                background: #1a1f35;
                color: #e0e6ff;
                border: 1px solid rgba(0,245,255,40);
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #00f5ff; }
            QPushButton {
                background: rgba(0,245,255,20);
                color: #00f5ff;
                border: 1px solid rgba(0,245,255,80);
                border-radius: 10px;
                padding: 12px 32px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,245,255,50); }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        # Welcome
        welcome = QLabel("🌟 YORDAMCHI ga Xush Kelibsiz!")
        welcome.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        welcome.setStyleSheet("color: #00f5ff;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome)

        subtitle = QLabel("Sizning shaxsiy AI yordamchingiz tayyor.\nKeling, sozlamalarni kiritamiz.")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #8c96b4;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Name
        name_label = QLabel("👤 Ismingiz:")
        name_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Masalan: Sarvar")
        self.name_input.setText(config.user_name)
        layout.addWidget(self.name_input)

        # API Key
        api_label = QLabel("🔑 Gemini API Key (ixtiyoriy):")
        api_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(api_label)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("API kalitni kiriting (keyinroq ham kiritish mumkin)")
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_input)

        layout.addStretch()

        # Start button
        start_btn = QPushButton("🚀 Boshlaymiz!")
        start_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        start_btn.clicked.connect(self._on_start)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _on_start(self):
        """Boshlash tugmasi"""
        name = self.name_input.text().strip()
        api_key = self.api_input.text().strip()

        if name:
            config.user_name = name
        if api_key:
            config.ai.gemini_api_key = api_key

        config.first_run = False
        config.save()
        self.accept()
