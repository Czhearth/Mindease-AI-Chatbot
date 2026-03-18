import os
import uuid
import requests
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


@app.post("/chat")
async def chat(req: ChatRequest):

    session_id = req.session_id or str(uuid.uuid4())

    risk = detect_crisis(req.message)

    # HIGH RISK RESPONSE

    if risk == "HIGH":

        return {
            "reply":
            "I'm really sorry you're feeling this way. You deserve support and you're not alone.\n\n"
            "If you're in immediate danger, please consider reaching out to someone you trust or a mental health professional.\n\n"
            "You can also contact a suicide prevention helpline in your country for immediate support.",
            "session_id": session_id
        }

    reply = ask_ai(session_id, req.message)

    return {
        "reply": reply,
        "session_id": session_id
    }