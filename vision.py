"""
╔══════════════════════════════════════════════════════════════╗
║           YORDAMCHI - Ko'rish (Vision) Moduli               ║
║   Kamera, yuz tanish, emotsiya aniqlash, OCR               ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import threading
from typing import Optional, Dict, List, Callable, Tuple
from pathlib import Path
import numpy as np

from config import config, FACES_DIR
from utils import logger, safe_execute

# OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV o'rnatilmagan!")

# Mediapipe
try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False

# DeepFace
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class VisionEngine:
    """
    Ko'rish tizimi - kamera orqali ko'rish,
    yuz tanish, emotsiya aniqlash.
    """
    
    def __init__(self):
        self.camera: Optional[cv2.VideoCapture] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_face_detected: Optional[Callable] = None
        self.on_emotion_detected: Optional[Callable] = None
        self.on_frame_ready: Optional[Callable] = None
        
        # Yuz ma'lumotlari
        self.known_faces: Dict[str, np.ndarray] = {}
        self._load_known_faces()
        
        # Mediapipe
        self.face_mesh = None
        self.face_detection = None
        if MP_AVAILABLE:
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.7
            )
        
        # Holat
        self.last_emotion: str = "neutral"
        self.face_detected: bool = False
        self.current_frame: Optional[np.ndarray] = None
        
        logger.info(f"Vision tizimi: CV2={CV2_AVAILABLE}, "
                   f"Mediapipe={MP_AVAILABLE}, DeepFace={DEEPFACE_AVAILABLE}")
    
    @safe_execute(fallback_value=None)
    def _load_known_faces(self):
        """Saqlangan yuzlarni yuklash"""
        if not CV2_AVAILABLE:
            return
        
        for face_file in FACES_DIR.glob("*.npy"):
            name = face_file.stem
            encoding = np.load(str(face_file))
            self.known_faces[name] = encoding
            logger.debug(f"Yuz yuklandi: {name}")
    
    @safe_execute(fallback_value=False)
    def start_camera(self, camera_id: int = 0) -> bool:
        """Kamerani ishga tushirish"""
        if not CV2_AVAILABLE:
            logger.error("OpenCV o'rnatilmagan!")
            return False
        
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            logger.error("Kamera ochilmadi!")
            return False
        
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        
        logger.info("Kamera ishga tushdi")
        return True
    
    def stop_camera(self):
        """Kamerani to'xtatish"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        if self.camera:
            self.camera.release()
            self.camera = None
        logger.info("Kamera to'xtatildi")
    
    def _capture_loop(self):
        """Kadr olish sikli"""
        while self._running and self.camera:
            ret, frame = self.camera.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            self.current_frame = frame
            
            # Yuz aniqlash (har 5-kadrda)
            if int(time.time() * 10) % 5 == 0:
                self._process_frame(frame)
            
            # Callback
            if self.on_frame_ready:
                self.on_frame_ready(frame)
            
            time.sleep(0.033)  # ~30 FPS
    
    @safe_execute(fallback_value=None)
    def _process_frame(self, frame: np.ndarray):
        """Kadrni qayta ishlash - yuz va emotsiya"""
        if not CV2_AVAILABLE:
            return
        
        # Mediapipe bilan yuz aniqlash
        if MP_AVAILABLE and self.face_detection:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            
            if results.detections:
                self.face_detected = True
                if self.on_face_detected:
                    self.on_face_detected(len(results.detections))
            else:
                self.face_detected = False
        
        # Emotsiya aniqlash (har 30 kadrda)
        if DEEPFACE_AVAILABLE and self.face_detected:
            if int(time.time()) % 3 == 0:
                self._detect_emotion(frame)
    
    @safe_execute(fallback_value=None)
    def _detect_emotion(self, frame: np.ndarray):
        """Emotsiyani aniqlash"""
        try:
            result = DeepFace.analyze(
                frame, actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if result and isinstance(result, list):
                emotion = result[0].get('dominant_emotion', 'neutral')
                
                # Emotsiyani o'zbekchaga tarjima
                emotion_map = {
                    'happy': 'xursand',
                    'sad': 'g\'amgin',
                    'angry': 'g\'azablangan',
                    'surprise': 'hayratda',
                    'fear': 'qo\'rqinchda',
                    'disgust': 'nafrat',
                    'neutral': 'oddiy'
                }
                
                self.last_emotion = emotion_map.get(emotion, emotion)
                
                if self.on_emotion_detected:
                    self.on_emotion_detected(self.last_emotion)
                    
        except Exception as e:
            logger.debug(f"Emotsiya aniqlashda xatolik: {e}")
    
    @safe_execute(fallback_value=False)
    def register_face(self, name: str) -> bool:
        """Yangi yuzni ro'yxatga olish"""
        if not CV2_AVAILABLE or self.current_frame is None:
            return False
        
        # Yuzni saqlash
        face_path = FACES_DIR / f"{name}.npy"
        
        if DEEPFACE_AVAILABLE:
            try:
                embedding = DeepFace.represent(
                    self.current_frame, model_name='Facenet',
                    enforce_detection=False
                )
                if embedding:
                    np.save(str(face_path), embedding[0]['embedding'])
                    self.known_faces[name] = np.array(embedding[0]['embedding'])
                    logger.info(f"Yuz ro'yxatga olindi: {name}")
                    return True
            except Exception as e:
                logger.error(f"Yuz saqlashda xatolik: {e}")
        
        # Oddiy rasm sifatida saqlash
        img_path = FACES_DIR / f"{name}.jpg"
        cv2.imwrite(str(img_path), self.current_frame)
        logger.info(f"Yuz rasmi saqlandi: {name}")
        return True
    
    @safe_execute(fallback_value=None)
    def identify_face(self) -> Optional[str]:
        """Hozirgi yuzni tanib olish"""
        if not DEEPFACE_AVAILABLE or self.current_frame is None:
            return None
        
        try:
            for name, known_encoding in self.known_faces.items():
                result = DeepFace.verify(
                    self.current_frame, 
                    known_encoding,
                    enforce_detection=False
                )
                if result.get('verified', False):
                    return name
        except Exception:
            pass
        
        return None
    
    @safe_execute(fallback_value="")
    def describe_scene(self) -> str:
        """Hozirgi kadrni tavsiflash (AI orqali)"""
        if self.current_frame is None:
            return "Kamera yoqilmagan"
        
        # Oddiy tavsif (AI uchun context)
        description_parts = []
        
        if self.face_detected:
            description_parts.append("Kadrda yuz aniqlandi")
            if self.last_emotion != "oddiy":
                description_parts.append(f"Emotsiya: {self.last_emotion}")
        
        # Yorug'lik darajasi
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()
        if brightness < 50:
            description_parts.append("Juda qorong'i muhit")
        elif brightness < 100:
            description_parts.append("Qorong'i muhit")
        elif brightness > 200:
            description_parts.append("Juda yorug' muhit")
        else:
            description_parts.append("Normal yorug'lik")
        
        return ". ".join(description_parts) if description_parts else "Oddiy sahna"
    
    @safe_execute(fallback_value=None)
    def capture_photo(self, save_path: str = None) -> Optional[str]:
        """Rasm olish"""
        if self.current_frame is None:
            return None
        
        if not save_path:
            save_path = str(Path.home() / "Desktop" / 
                          f"photo_{int(time.time())}.jpg")
        
        cv2.imwrite(save_path, self.current_frame)
        logger.info(f"Rasm saqlandi: {save_path}")
        return save_path
    
    def get_status(self) -> Dict:
        """Vision holati"""
        return {
            "camera_active": self._running,
            "face_detected": self.face_detected,
            "emotion": self.last_emotion,
            "known_faces": list(self.known_faces.keys()),
            "cv2_available": CV2_AVAILABLE,
            "deepface_available": DEEPFACE_AVAILABLE
        }
    
    def cleanup(self):
        """Resurslarni tozalash"""
        self.stop_camera()
        if self.face_detection:
            self.face_detection.close()
