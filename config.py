"""Configuración central de Tekni. Las claves secretas se cargan desde el entorno."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
DEEPSEEK_VISION_MODEL = os.getenv("DEEPSEEK_VISION_MODEL", DEEPSEEK_MODEL)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ESP32_PORT = os.getenv("ESP32_PORT", "/dev/ttyUSB0")
ESP32_BAUDRATE = int(os.getenv("ESP32_BAUDRATE", "115200"))
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")
WAKE_WORD = os.getenv("WAKE_WORD", "tekni")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
DB_PATH = str(DATA_DIR / "tekni.db")
