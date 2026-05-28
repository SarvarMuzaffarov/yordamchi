"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Tizim Monitoringi                     ║
║      CPU, RAM, Disk, Tarmoq, Batareya real-time monitoring  ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import threading
from datetime import datetime
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from utils import logger, safe_execute


@dataclass
class SystemStats:
    """Tizim statistikasi"""
    cpu_percent: float = 0.0
    cpu_count: int = 0
    cpu_freq: float = 0.0
    
    ram_total: int = 0
    ram_used: int = 0
    ram_percent: float = 0.0
    
    disk_total: int = 0
    disk_used: int = 0
    disk_percent: float = 0.0
    
    net_sent: int = 0
    net_recv: int = 0
    net_speed_up: float = 0.0
    net_speed_down: float = 0.0
    
    battery_percent: float = -1.0
    battery_charging: bool = False
    
    uptime: str = ""
    current_time: str = ""
    
    # Jarayonlar
    process_count: int = 0
    top_processes: list = field(default_factory=list)


class SystemMonitor:
    """
    Real-time tizim monitoringi.
    Alohida threadda ishlaydi va GUI ga yangilanishlarni yuboradi.
    """
    
    def __init__(self, update_interval: float = 2.0):
        self.update_interval = update_interval
        self.stats = SystemStats()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list = []
        self._prev_net = None
        self._prev_time = None
        
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil o'rnatilmagan! Tizim monitoringi cheklangan.")
    
    def start(self):
        """Monitoringni boshlash"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Tizim monitoringi ishga tushdi")
    
    def stop(self):
        """Monitoringni to'xtatish"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Tizim monitoringi to'xtatildi")
    
    def add_callback(self, callback: Callable[[SystemStats], None]):
        """Yangilanish callbackini qo'shish"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Callbackni olib tashlash"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _monitor_loop(self):
        """Asosiy monitoring sikli"""
        while self._running:
            try:
                self._update_stats()
                self._notify_callbacks()
            except Exception as e:
                logger.error(f"Monitor xatolik: {e}")
            time.sleep(self.update_interval)
    
    @safe_execute(fallback_value=None)
    def _update_stats(self):
        """Statistikani yangilash"""
        if not PSUTIL_AVAILABLE:
            self.stats.current_time = datetime.now().strftime("%H:%M:%S")
            return
        
        # CPU
        self.stats.cpu_percent = psutil.cpu_percent(interval=0.1)
        self.stats.cpu_count = psutil.cpu_count()
        freq = psutil.cpu_freq()
        if freq:
            self.stats.cpu_freq = freq.current
        
        # RAM
        mem = psutil.virtual_memory()
        self.stats.ram_total = mem.total
        self.stats.ram_used = mem.used
        self.stats.ram_percent = mem.percent
        
        # Disk
        disk = psutil.disk_usage('/')
        self.stats.disk_total = disk.total
        self.stats.disk_used = disk.used
        self.stats.disk_percent = (disk.used / disk.total) * 100
        
        # Tarmoq
        net = psutil.net_io_counters()
        current_time = time.time()
        
        if self._prev_net and self._prev_time:
            time_delta = current_time - self._prev_time
            if time_delta > 0:
                self.stats.net_speed_up = (net.bytes_sent - self._prev_net.bytes_sent) / time_delta
                self.stats.net_speed_down = (net.bytes_recv - self._prev_net.bytes_recv) / time_delta
        
        self.stats.net_sent = net.bytes_sent
        self.stats.net_recv = net.bytes_recv
        self._prev_net = net
        self._prev_time = current_time
        
        # Batareya
        battery = psutil.sensors_battery()
        if battery:
            self.stats.battery_percent = battery.percent
            self.stats.battery_charging = battery.power_plugged
        
        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        self.stats.uptime = f"{hours}s {minutes}d"
        
        # Vaqt
        self.stats.current_time = datetime.now().strftime("%H:%M:%S")
        
        # Jarayonlar
        self.stats.process_count = len(psutil.pids())
        
        # Top 5 jarayon (CPU bo'yicha)
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] and info['cpu_percent'] > 0:
                        processes.append({
                            'name': info['name'][:20],
                            'cpu': info['cpu_percent'],
                            'ram': info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            self.stats.top_processes = processes[:5]
        except Exception:
            pass
    
    def _notify_callbacks(self):
        """Callbacklarni xabardor qilish"""
        for callback in self._callbacks:
            try:
                callback(self.stats)
            except Exception as e:
                logger.error(f"Monitor callback xatolik: {e}")
    
    def get_stats(self) -> SystemStats:
        """Joriy statistikani olish"""
        return self.stats
    
    def get_summary(self) -> str:
        """Statistika xulosasini olish (AI uchun)"""
        s = self.stats
        summary = (
            f"Tizim holati:\n"
            f"- CPU: {s.cpu_percent}% ({s.cpu_count} yadro)\n"
            f"- RAM: {s.ram_percent}% ({s.ram_used // (1024**3):.1f}/"
            f"{s.ram_total // (1024**3):.1f} GB)\n"
            f"- Disk: {s.disk_percent:.1f}%\n"
            f"- Jarayonlar: {s.process_count}\n"
            f"- Vaqt: {s.current_time}\n"
        )
        if s.battery_percent >= 0:
            status = "quvvatlanmoqda" if s.battery_charging else "batareya"
            summary += f"- Batareya: {s.battery_percent}% ({status})\n"
        
        return summary
    
    @safe_execute(fallback_value="")
    def get_alert(self) -> str:
        """Ogohlantirish xabarini olish (yuqori yuklanish bo'lsa)"""
        alerts = []
        s = self.stats
        
        if s.cpu_percent > 90:
            alerts.append(f"⚠️ CPU juda yuqori: {s.cpu_percent}%")
        if s.ram_percent > 90:
            alerts.append(f"⚠️ RAM juda yuqori: {s.ram_percent}%")
        if s.disk_percent > 95:
            alerts.append(f"⚠️ Disk to'lmoqda: {s.disk_percent:.1f}%")
        if 0 <= s.battery_percent < 15 and not s.battery_charging:
            alerts.append(f"⚠️ Batareya past: {s.battery_percent}%")
        
        return " | ".join(alerts) if alerts else ""
