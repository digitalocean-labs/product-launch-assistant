import os
import json
from datetime import timedelta
from dotenv import load_dotenv
import redis
from langchain_gradient import ChatGradient

# Load environment variables
load_dotenv()

# API keys
DIGITALOCEAN_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Quality thresholds
MARKET_RESEARCH_MIN_CHARS = 800

# LLM clients
llm = ChatGradient(
    api_key=DIGITALOCEAN_INFERENCE_KEY,
    temperature=0.7,
    model="llama3.3-70b-instruct"
)

llm_fallback = ChatGradient(
    api_key=DIGITALOCEAN_INFERENCE_KEY,
    temperature=0.7,
    model="llama3.1-8b-instruct"
)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL")
SESSION_TTL_SECONDS = int(timedelta(days=1).total_seconds())
try:
    _redis = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:
    _redis = None


