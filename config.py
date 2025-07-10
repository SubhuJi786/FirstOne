import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

# === Azure OpenAI Configuration ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
ENDPOINT_URL = os.getenv("ENDPOINT_URL", "")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-4")

# For compatibility with existing code
OPENAI_API_KEY = AZURE_OPENAI_API_KEY
OPENAI_MODEL = DEPLOYMENT_NAME

# === LiveKit Configuration ===
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")

# === Directories ===
DATA_DIR = "chapters"
UPLOADS_DIR = "uploads"
AUDIO_DIR = "audio"
USER_DATA_DIR = "user_data"

# === User Settings ===
DEFAULT_USER_ID = "demo_user"
TTS_RATE = 120  # Slower for neuro-friendly learning
TTS_PAUSE_DURATION = 0.5

# === Learning Settings ===
FLASHCARD_DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
QUIZ_QUESTION_COUNT = 3
FOCUS_TIME_THRESHOLD = 10  # seconds
STREAK_GOALS = [3, 7, 14, 30]

# === Supported Languages ===
SUPPORTED_LANGUAGES = {
   "English": "en",
   "Hindi": "hi",
   "Spanish": "es",
   "French": "fr"
}

# === Mood Options ===
MOOD_OPTIONS = {
   "😊": "Happy",
   "😐": "Neutral",
   "😔": "Sad",
   "😤": "Frustrated",
   "🤔": "Confused",
   "😴": "Tired"
}

# === Create directories if they don't exist ===
for dir_name in [DATA_DIR, UPLOADS_DIR, AUDIO_DIR, USER_DATA_DIR]:
   os.makedirs(dir_name, exist_ok=True)