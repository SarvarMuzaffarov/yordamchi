"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Futuristik GUI                        ║
║   Cyberpunk + Glassmorphism + Holographic Design            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import math
import random
import time
from typing import Optional, List, Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QPoint, QRect, QSize, pyqtSignal, QThread, QObject
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QRadialGradient,
    QPen, QBrush, QFont, QFontDatabase, QPainterPath,
    QPixmap, QIcon, QPalette, QConicalGradient
)

from config import config
from utils import logger, get_greeting, get_current_datetime_str, format_bytes



# ===== RANGLAR VA STILLAR =====
class Colors:
    """Dastur ranglari"""
    PRIMARY = QColor(0, 245, 255)        # Neon Cyan
    SECONDARY = QColor(123, 47, 247)     # Neon Purple
    ACCENT = QColor(255, 0, 110)         # Neon Pink
    BG_DARK = QColor(10, 14, 26)         # Space Dark
    BG_SURFACE = QColor(20, 24, 41)      # Surface
    BG_CARD = QColor(25, 30, 52)         # Card
    TEXT = QColor(224, 230, 255)          # Light text
    TEXT_DIM = QColor(140, 150, 180)     # Dim text
    SUCCESS = QColor(0, 255, 136)        # Green
    WARNING = QColor(255, 170, 0)        # Amber
    ERROR = QColor(255, 51, 102)         # Red
    BORDER = QColor(60, 70, 120, 80)     # Border


# ===== PARTICLE SYSTEM =====
class Particle:
    """Bitta zarrача"""
    def __init__(self, width: int, height: int):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, -0.1)
        self.size = random.uniform(1, 3)
        self.alpha = random.uniform(0.2, 0.7)
        self.color = random.choice([Colors.PRIMARY, Colors.SECONDARY, Colors.ACCENT])
        self.life = random.uniform(0.5, 1.0)
        self.max_life = self.life
        self.width = width
        self.height = height

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.005

        if self.life <= 0 or self.y < -10:
            self.reset()

    def reset(self):
        self.x = random.uniform(0, self.width)
        self.y = self.height + 10
        self.life = random.uniform(0.5, 1.0)
        self.max_life = self.life
        self.alpha = random.uniform(0.2, 0.7)



# ===== HOLOGRAPHIC ORB WIDGET =====
class HolographicOrb(QWidget):
    """
    Markazdagi holografik shar - asosiy vizual element.
    Pulsatsiya, glow, waveform animatsiyalari.
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 280)
        self._pulse = 0.0
        self._rotation = 0.0
        self._glow_intensity = 0.5
        self._wave_data = [0.0] * 64
        self._is_listening = False
        self._is_speaking = False
        self._is_thinking = False
        self._hover = False

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)  # ~60 FPS

    def set_listening(self, active: bool):
        self._is_listening = active
        self._glow_intensity = 0.9 if active else 0.5

    def set_speaking(self, active: bool):
        self._is_speaking = active

    def set_thinking(self, active: bool):
        self._is_thinking = active

    def set_wave_data(self, data: list):
        self._wave_data = data[:64] if len(data) >= 64 else data + [0.0] * (64 - len(data))

    def _animate(self):
        self._pulse += 0.03
        self._rotation += 0.5
        if self._rotation >= 360:
            self._rotation = 0
        self.update()

    def enterEvent(self, event):
        self._hover = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2
        base_radius = 90
        pulse_offset = math.sin(self._pulse) * 8
        radius = base_radius + pulse_offset

        # Outer glow
        for i in range(5, 0, -1):
            glow_color = QColor(Colors.PRIMARY)
            alpha = int(self._glow_intensity * 30 * (6 - i))
            glow_color.setAlpha(min(255, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow_color))
            glow_r = radius + i * 15
            painter.drawEllipse(QPoint(cx, cy), int(glow_r), int(glow_r))

        # Main orb gradient
        gradient = QRadialGradient(cx, cy, radius)
        if self._is_listening:
            gradient.setColorAt(0, QColor(0, 245, 255, 180))
            gradient.setColorAt(0.5, QColor(123, 47, 247, 120))
            gradient.setColorAt(1, QColor(0, 245, 255, 40))
        elif self._is_thinking:
            gradient.setColorAt(0, QColor(255, 170, 0, 180))
            gradient.setColorAt(0.5, QColor(255, 100, 0, 120))
            gradient.setColorAt(1, QColor(255, 170, 0, 40))
        elif self._is_speaking:
            gradient.setColorAt(0, QColor(0, 255, 136, 180))
            gradient.setColorAt(0.5, QColor(0, 200, 100, 120))
            gradient.setColorAt(1, QColor(0, 255, 136, 40))
        else:
            gradient.setColorAt(0, QColor(123, 47, 247, 150))
            gradient.setColorAt(0.5, QColor(0, 245, 255, 80))
            gradient.setColorAt(1, QColor(10, 14, 26, 20))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPoint(cx, cy), int(radius), int(radius))

        # Orbital rings
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(3):
            ring_color = QColor(Colors.PRIMARY)
            ring_color.setAlpha(60 + i * 20)
            pen = QPen(ring_color, 1.5)
            painter.setPen(pen)
            angle = self._rotation + i * 120
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(angle)
            painter.scale(1.0, 0.3 + i * 0.1)
            r = int(radius + 20 + i * 10)
            painter.drawEllipse(QPoint(0, 0), r, r)
            painter.restore()


        # Waveform visualization (circular)
        if self._is_listening or self._is_speaking:
            wave_pen = QPen(QColor(0, 245, 255, 200), 2)
            painter.setPen(wave_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            path = QPainterPath()
            for j, val in enumerate(self._wave_data):
                angle_rad = (j / len(self._wave_data)) * 2 * math.pi
                wave_r = radius + 25 + val * 30
                wx = cx + wave_r * math.cos(angle_rad)
                wy = cy + wave_r * math.sin(angle_rad)
                if j == 0:
                    path.moveTo(wx, wy)
                else:
                    path.lineTo(wx, wy)
            path.closeSubpath()
            painter.drawPath(path)

        # Center icon / text
        painter.setPen(QPen(Colors.TEXT, 1))
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(font)

        if self._is_listening:
            status_text = "🎤 Tinglayapman..."
        elif self._is_thinking:
            status_text = "🧠 O'ylayapman..."
        elif self._is_speaking:
            status_text = "🔊 Gapiryapman..."
        else:
            status_text = "⚡ Tayyor"

        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, status_text)

        # Hover effect
        if self._hover:
            hover_color = QColor(Colors.PRIMARY)
            hover_color.setAlpha(30)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(hover_color))
            painter.drawEllipse(QPoint(cx, cy), int(radius + 5), int(radius + 5))

        painter.end()



# ===== GLASSMORPHISM PANEL =====
class GlassPanel(QFrame):
    """Shaffof shisha effektli panel"""
    def __init__(self, parent=None, border_color=None):
        super().__init__(parent)
        self._border_color = border_color or Colors.BORDER
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg = QColor(20, 24, 41, 180)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        painter.drawPath(path)

        # Border glow
        border_pen = QPen(self._border_color, 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 16, 16)

        painter.end()
        super().paintEvent(event)


# ===== SYSTEM MONITOR PANEL =====
class SystemPanel(GlassPanel):
    """Chap panel - tizim monitoringi"""
    def __init__(self, parent=None):
        super().__init__(parent, QColor(0, 245, 255, 60))
        self.setFixedWidth(280)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        # Title
        title = QLabel("⚡ TIZIM MONITORI")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #00f5ff; background: transparent;")
        layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                         "stop:0 transparent, stop:0.5 #00f5ff, stop:1 transparent);")
        layout.addWidget(sep)

        # Stats labels
        self.time_label = self._create_stat_label("🕐 Vaqt", "00:00:00")
        self.cpu_label = self._create_stat_label("⚙️ CPU", "0%")
        self.ram_label = self._create_stat_label("🧠 RAM", "0%")
        self.disk_label = self._create_stat_label("💾 Disk", "0%")
        self.net_label = self._create_stat_label("🌐 Tarmoq", "0 KB/s")
        self.battery_label = self._create_stat_label("🔋 Batareya", "N/A")

        layout.addWidget(self.time_label)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.net_label)
        layout.addWidget(self.battery_label)

        layout.addStretch()

        # AI Status
        self.ai_status = QLabel("🤖 AI: Tayyor")
        self.ai_status.setFont(QFont("Segoe UI", 9))
        self.ai_status.setStyleSheet("color: #00ff88; background: transparent;")
        layout.addWidget(self.ai_status)

    def _create_stat_label(self, name: str, value: str) -> QLabel:
        label = QLabel(f"{name}: {value}")
        label.setFont(QFont("Consolas", 10))
        label.setStyleSheet("color: #e0e6ff; background: transparent; padding: 4px;")
        return label


    def update_stats(self, stats):
        """Tizim statistikasini yangilash"""
        self.time_label.setText(f"🕐 Vaqt: {stats.current_time}")
        self.cpu_label.setText(f"⚙️ CPU: {stats.cpu_percent}%")
        self.ram_label.setText(f"🧠 RAM: {stats.ram_percent}%")
        self.disk_label.setText(f"💾 Disk: {stats.disk_percent:.0f}%")

        speed = stats.net_speed_down
        if speed > 1024*1024:
            net_str = f"{speed/(1024*1024):.1f} MB/s"
        elif speed > 1024:
            net_str = f"{speed/1024:.1f} KB/s"
        else:
            net_str = f"{speed:.0f} B/s"
        self.net_label.setText(f"🌐 Tarmoq: {net_str}")

        if stats.battery_percent >= 0:
            icon = "⚡" if stats.battery_charging else "🔋"
            self.battery_label.setText(f"{icon} Batareya: {stats.battery_percent:.0f}%")


# ===== MISSION LOG (Chat) PANEL =====
class MissionLog(GlassPanel):
    """O'ng panel - suhbat tarixi (Mission Log)"""
    def __init__(self, parent=None):
        super().__init__(parent, QColor(123, 47, 247, 60))
        self.setFixedWidth(340)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        # Title
        title = QLabel("📋 MISSION LOG")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #7b2ff7; background: transparent;")
        layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                         "stop:0 transparent, stop:0.5 #7b2ff7, stop:1 transparent);")
        layout.addWidget(sep)

        # Chat scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                background: transparent; 
                border: none; 
            }
            QScrollBar:vertical {
                background: #141829;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #7b2ff7;
                border-radius: 3px;
                min-height: 20px;
            }
        """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)


    def add_message(self, text: str, is_user: bool = False):
        """Xabar qo'shish"""
        msg_widget = QLabel(text)
        msg_widget.setWordWrap(True)
        msg_widget.setFont(QFont("Segoe UI", 9))
        msg_widget.setMaximumWidth(290)

        if is_user:
            msg_widget.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 rgba(0,245,255,40), stop:1 rgba(123,47,247,40));
                    color: #e0e6ff;
                    padding: 10px 14px;
                    border-radius: 12px;
                    border: 1px solid rgba(0,245,255,60);
                }
            """)
        else:
            msg_widget.setStyleSheet("""
                QLabel {
                    background: rgba(25,30,52,200);
                    color: #e0e6ff;
                    padding: 10px 14px;
                    border-radius: 12px;
                    border: 1px solid rgba(123,47,247,40);
                }
            """)

        # Insert before the stretch
        count = self.chat_layout.count()
        self.chat_layout.insertWidget(count - 1, msg_widget)

        # Auto-scroll
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def clear_log(self):
        """Logni tozalash"""
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ===== NEON INPUT FIELD =====
class NeonInput(QLineEdit):
    """Neon effektli input maydoni"""
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("💬 Yozing yoki mikrofon bosing...")
        self.setFont(QFont("Segoe UI", 11))
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(20, 24, 41, 200);
                color: #e0e6ff;
                border: 2px solid rgba(0, 245, 255, 60);
                border-radius: 20px;
                padding: 12px 20px;
                selection-background-color: #7b2ff7;
            }
            QLineEdit:focus {
                border: 2px solid #00f5ff;
            }
            QLineEdit::placeholder {
                color: rgba(140, 150, 180, 150);
            }
        """)
        self.returnPressed.connect(self._on_submit)

    def _on_submit(self):
        text = self.text().strip()
        if text:
            self.submitted.emit(text)
            self.clear()



# ===== NEON BUTTON =====
class NeonButton(QPushButton):
    """Neon effektli tugma"""
    def __init__(self, text: str, color: QColor = None, parent=None):
        super().__init__(text, parent)
        self._color = color or Colors.PRIMARY
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba({r},{g},{b},30);
                color: rgb({r},{g},{b});
                border: 1px solid rgba({r},{g},{b},100);
                border-radius: 12px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: rgba({r},{g},{b},60);
                border: 1px solid rgba({r},{g},{b},200);
            }}
            QPushButton:pressed {{
                background: rgba({r},{g},{b},90);
            }}
        """)


# ===== MAIN WINDOW =====
class YordamchiWindow(QMainWindow):
    """Asosiy dastur oynasi"""

    # Signals
    request_ai_response = pyqtSignal(str)
    update_system_stats = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YORDAMCHI • AI Assistant")
        self.setMinimumSize(1200, 750)
        self.resize(config.gui.window_width, config.gui.window_height)

        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet(f"background-color: {config.gui.background_color};")

        # Particles
        self._particles: List[Particle] = []
        self._init_particles()

        # Animation timer
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._update_animations)
        self._anim_timer.start(33)  # ~30 FPS

        # Scanline offset
        self._scanline_offset = 0

        # Setup UI
        self._setup_ui()
        self._apply_theme()

        logger.info("GUI tayyor")


    def _init_particles(self):
        """Zarralar tizimini ishga tushirish"""
        w, h = config.gui.window_width, config.gui.window_height
        self._particles = [
            Particle(w, h) for _ in range(config.gui.particle_count)
        ]

    def _setup_ui(self):
        """Asosiy UI ni yaratish"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # === LEFT PANEL: System Monitor ===
        self.system_panel = SystemPanel()
        main_layout.addWidget(self.system_panel)

        # === CENTER: Orb + Input ===
        center_layout = QVBoxLayout()
        center_layout.setSpacing(16)

        # Header
        header = QLabel(f"🌟 {get_greeting()}, {config.user_name}!")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #e0e6ff; background: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(header)

        # Date
        date_label = QLabel(get_current_datetime_str())
        date_label.setFont(QFont("Segoe UI", 9))
        date_label.setStyleSheet("color: #8c96b4; background: transparent;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._date_label = date_label
        center_layout.addWidget(date_label)

        center_layout.addStretch()

        # Holographic Orb
        orb_container = QHBoxLayout()
        orb_container.addStretch()
        self.orb = HolographicOrb()
        self.orb.clicked.connect(self._on_orb_clicked)
        orb_container.addWidget(self.orb)
        orb_container.addStretch()
        center_layout.addLayout(orb_container)

        center_layout.addStretch()

        # Response display
        self.response_label = QLabel("")
        self.response_label.setWordWrap(True)
        self.response_label.setFont(QFont("Segoe UI", 11))
        self.response_label.setStyleSheet("""
            color: #e0e6ff; background: transparent;
            padding: 10px;
        """)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setMaximumHeight(120)
        center_layout.addWidget(self.response_label)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_mic = NeonButton("🎤 Tinglash", Colors.PRIMARY)
        self.btn_mic.clicked.connect(self._on_mic_clicked)

        self.btn_stop = NeonButton("⏹ To'xtat", Colors.ERROR)
        self.btn_stop.clicked.connect(self._on_stop_clicked)

        self.btn_clear = NeonButton("🗑 Tozalash", Colors.WARNING)
        self.btn_clear.clicked.connect(self._on_clear_clicked)

        self.btn_settings = NeonButton("⚙️ Sozlamalar", Colors.SECONDARY)
        self.btn_settings.clicked.connect(self._on_settings_clicked)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_mic)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_settings)
        btn_layout.addStretch()
        center_layout.addLayout(btn_layout)

        # Input field
        self.input_field = NeonInput()
        self.input_field.submitted.connect(self._on_text_submitted)
        center_layout.addWidget(self.input_field)

        main_layout.addLayout(center_layout, 1)

        # === RIGHT PANEL: Mission Log ===
        self.mission_log = MissionLog()
        main_layout.addWidget(self.mission_log)


    def _apply_theme(self):
        """Tema qo'llash"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {config.gui.background_color};
            }}
            QWidget {{
                font-family: 'Segoe UI', sans-serif;
            }}
        """)

    def _update_animations(self):
        """Animatsiyalarni yangilash"""
        # Particles
        for p in self._particles:
            p.update()
        # Scanline
        self._scanline_offset = (self._scanline_offset + 1) % self.height()
        self.update()

    def paintEvent(self, event):
        """Background chizish - particles, grid, scanlines"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark background
        painter.fillRect(self.rect(), QColor(config.gui.background_color))

        # Neon Grid
        if config.gui.enable_glow:
            grid_pen = QPen(QColor(0, 245, 255, 15), 1)
            painter.setPen(grid_pen)
            spacing = 60
            for x in range(0, self.width(), spacing):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), spacing):
                painter.drawLine(0, y, self.width(), y)

        # Particles
        if config.gui.enable_particles:
            for p in self._particles:
                color = QColor(p.color)
                alpha = int(p.alpha * 255 * (p.life / p.max_life))
                color.setAlpha(min(255, max(0, alpha)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(int(p.x), int(p.y), int(p.size), int(p.size))

        # Scanlines
        if config.gui.enable_scanlines:
            scanline_color = QColor(0, 0, 0, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(scanline_color))
            for y in range(0, self.height(), 4):
                painter.drawRect(0, y, self.width(), 1)

        painter.end()

    # ===== EVENT HANDLERS =====

    def _on_orb_clicked(self):
        """Orb bosilganda"""
        self._on_mic_clicked()

    def _on_mic_clicked(self):
        """Mikrofon tugmasi"""
        self.orb.set_listening(True)
        self.response_label.setText("🎤 Tinglayapman... Gapiring!")

    def _on_stop_clicked(self):
        """To'xtatish tugmasi"""
        self.orb.set_listening(False)
        self.orb.set_speaking(False)
        self.orb.set_thinking(False)
        self.response_label.setText("")

    def _on_clear_clicked(self):
        """Tozalash"""
        self.mission_log.clear_log()
        self.response_label.setText("")

    def _on_settings_clicked(self):
        """Sozlamalar"""
        from settings import SettingsWindow
        self.settings_win = SettingsWindow(self)
        self.settings_win.show()

    def _on_text_submitted(self, text: str):
        """Matn yuborilganda"""
        self.mission_log.add_message(f"👤 {text}", is_user=True)
        self.orb.set_thinking(True)
        self.response_label.setText("🧠 O'ylayapman...")
        self.request_ai_response.emit(text)


    # ===== PUBLIC API =====

    def show_response(self, text: str):
        """AI javobini ko'rsatish"""
        self.orb.set_thinking(False)
        self.orb.set_speaking(True)
        # Qisqa versiya response_label uchun
        short_text = text[:200] + "..." if len(text) > 200 else text
        self.response_label.setText(short_text)
        self.mission_log.add_message(f"🤖 {text}", is_user=False)
        # 3 soniyadan keyin speaking off
        QTimer.singleShot(3000, lambda: self.orb.set_speaking(False))

    def show_error(self, text: str):
        """Xatolik ko'rsatish"""
        self.orb.set_thinking(False)
        self.response_label.setText(f"❌ {text}")
        self.response_label.setStyleSheet(
            "color: #ff3366; background: transparent; padding: 10px;"
        )
        QTimer.singleShot(5000, lambda: self.response_label.setStyleSheet(
            "color: #e0e6ff; background: transparent; padding: 10px;"
        ))

    def update_system_display(self, stats):
        """Tizim monitorini yangilash"""
        self.system_panel.update_stats(stats)

    def set_ai_status(self, status: str):
        """AI holatini yangilash"""
        self.system_panel.ai_status.setText(f"🤖 AI: {status}")

    def set_listening_state(self, active: bool):
        """Tinglash holatini yangilash"""
        self.orb.set_listening(active)
        if active:
            self.response_label.setText("🎤 Tinglayapman...")
            self.btn_mic.setEnabled(False)
        else:
            self.btn_mic.setEnabled(True)

    def set_thinking_state(self, active: bool):
        """Fikrlash holatini yangilash"""
        self.orb.set_thinking(active)
        if active:
            self.response_label.setText("🧠 O'ylayapman...")

    def keyPressEvent(self, event):
        """Klaviatura hodisalari"""
        if event.key() == Qt.Key.Key_Escape:
            self._on_stop_clicked()
        elif event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Oyna yopilganda"""
        config.save()
        event.accept()
