"""
Configuration settings for YouTube Automation Pipeline
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# YouTube Configuration
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
VIDEO_CATEGORY_ID = os.getenv("VIDEO_CATEGORY_ID", "28")  # Science & Technology
VIDEO_PRIVACY = os.getenv("VIDEO_PRIVACY", "public")  # public, private, unlisted

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

# Content Configuration
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "Tech Master")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# TTS Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# Pexels API (for stock footage)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Video Settings
VIDEO_RESOLUTION = (1920, 1080)  # 1080p
VIDEO_FPS = 30
THUMBNAIL_SIZE = (1280, 720)

# Audio Settings
TTS_LANGUAGE = "en"
BACKGROUND_MUSIC_VOLUME = 0.1  # 10% of original volume

# Content Topics (Evergreen Tech Topics)
EVERGREEN_TOPICS = [
    "artificial intelligence basics",
    "cybersecurity tips",
    "programming fundamentals",
    "cloud computing explained",
    "blockchain technology",
    "machine learning concepts",
    "web development best practices",
    "mobile app development",
    "data science fundamentals",
    "internet of things (IoT)",
    "quantum computing basics",
    "5G technology explained",
    "virtual reality and augmented reality",
    "software engineering principles",
    "database management systems",
]
