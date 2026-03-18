import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

system_prompt = """
You are MindEase, a calm and supportive AI mental health companion.

Your role is to talk to the user like a therapist during a first consultation.

Rules:
- Speak calmly and naturally.
- Do NOT analyze their message patterns.
- Do NOT mention if they repeated something.
- Do NOT talk about conversation mechanics.

Behavior:
- Acknowledge the user's message
- Ask gentle follow-up questions
- Encourage reflection
- Offer grounding suggestions when helpful

Tone:
- warm
- supportive
- simple
- non-judgmental
"""

def generate_reply(user_message, history):

    try:

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        for msg in history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        messages.append({
            "role": "user",
            "content": user_message
        })

        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:

        print("AI ERROR:", e)

        return "I'm having trouble responding right now. Please try again."