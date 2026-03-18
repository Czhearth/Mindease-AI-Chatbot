import os
import uuid
import requests
from time import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from crisis_detection import detect_crisis

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# =========================
# SESSION STORAGE
# =========================
sessions = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are MindEase, a calm and emotionally intelligent mental health support assistant.

Rules:
- Speak like a caring human
- Adapt tone based on emotion
- Comfort users when they are struggling
- Offer gentle advice when appropriate
- Ask thoughtful follow-up questions
"""
}

# =========================
# 🔥 RATE LIMITING (NEW)
# =========================
user_limits = {}
MAX_REQUESTS = 15      # per session
WINDOW = 3600          # 1 hour

GLOBAL_LIMIT = 300     # total requests safeguard
global_count = 0


def is_rate_limited(session_id):
    now = time()

    if session_id not in user_limits:
        user_limits[session_id] = []

    # remove old timestamps
    user_limits[session_id] = [
        t for t in user_limits[session_id]
        if now - t < WINDOW
    ]

    if len(user_limits[session_id]) >= MAX_REQUESTS:
        return True

    user_limits[session_id].append(now)
    return False


# =========================
# AI CALL
# =========================
def ask_ai(session_id, user_message):

    if session_id not in sessions:
        sessions[session_id] = [SYSTEM_PROMPT]

    conversation = sessions[session_id]

    conversation.append({
        "role": "user",
        "content": user_message
    })

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": conversation[-20:]
        }
    )

    data = response.json()

    if "choices" not in data:
        return "I'm having trouble responding right now."

    reply = data["choices"][0]["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": reply
    })

    sessions[session_id] = conversation

    return reply


# =========================
# CHAT ENDPOINT
# =========================
@app.post("/chat")
async def chat(req: ChatRequest):

    global global_count

    session_id = req.session_id or str(uuid.uuid4())

    # 🔥 GLOBAL LIMIT
    if global_count >= GLOBAL_LIMIT:
        return {
            "reply": "The server is currently busy. Please try again later.",
            "session_id": session_id
        }

    # 🔥 PER USER LIMIT
    if is_rate_limited(session_id):
        return {
            "reply": "You've reached your usage limit for now. Please try again later.",
            "session_id": session_id
        }

    global_count += 1

    # =========================
    # CRISIS DETECTION
    # =========================
    risk = detect_crisis(req.message)

    if risk == "HIGH":
        return {
            "reply":
            "I'm really sorry you're feeling this way. You deserve support and you're not alone.\n\n"
            "If you're in immediate danger, please consider reaching out to someone you trust or a mental health professional.\n\n"
            "You can also contact a suicide prevention helpline in your country for immediate support.",
            "session_id": session_id
        }

    # =========================
    # NORMAL FLOW
    # =========================
    reply = ask_ai(session_id, req.message)

    return {
        "reply": reply,
        "session_id": session_id
    }