import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PROVIDER_NAME = os.getenv("LLM_PROVIDER", "mock").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SESSION_TTL = int(os.getenv("SESSION_TTL", "20"))
MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", "3"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
