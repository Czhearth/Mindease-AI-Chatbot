import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def detect_crisis(text):

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are a mental health safety classifier.

Your job is to analyze a user's message and determine
if it contains suicidal intent.

Respond ONLY with one word:

LOW
MEDIUM
HIGH

LOW = normal conversation
MEDIUM = sadness or emotional distress
HIGH = suicidal thoughts or self harm intent
"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0
            }
        )

        data = response.json()

        if "choices" not in data:
            return "LOW"

        risk = data["choices"][0]["message"]["content"].strip()

        return risk

    except Exception as e:

        print("CRISIS DETECTION ERROR:", e)

        return "LOW"