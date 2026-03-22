from flask import Flask, request, jsonify, render_template, send_from_directory
from groq import Groq
import os
import json
import logging
from datetime import datetime
import re
from functools import wraps
import hashlib

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
class Config:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", 8192))
    TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.25))
    RATE_LIMIT = int(os.environ.get("RATE_LIMIT", 60))
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

app.config.from_object(Config)

# Initialize Groq client
client = None
if app.config['GROQ_API_KEY']:
    client = Groq(api_key=app.config['GROQ_API_KEY'])
else:
    logger.error("GROQ_API_KEY not set!")

# Rate limiting
client_ips = {}
def rate_limit():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.now().timestamp()
            if ip not in client_ips:
                client_ips[ip] = []
            client_ips[ip] = [t for t in client_ips[ip] if now - t < 60]
            if len(client_ips[ip]) >= app.config['RATE_LIMIT']:
                return jsonify({"error": "Rate limit exceeded"}), 429
            client_ips[ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ULTRA-ENHANCED SYSTEM PROMPT with User Notes Integration
SYSTEM_PROMPT = """You are **ULTIMATE CodeMaster AI + OSINT Intel Pro v2.0** - World's most advanced programming & intelligence AI.

## 🛡️ USER CONTEXT INTEGRATION (2026-03-19 Notes)
