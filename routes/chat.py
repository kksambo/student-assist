from fastapi import APIRouter, HTTPException
import httpx
import os
import asyncio

router = APIRouter(prefix="/tut-chat", tags=["TUT Chat Bot"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"


async def get_tut_guidance(question: str) -> str:
    """Use LLM to generate answers specifically about Tshwane University of Technology."""
    system_prompt = (
        "You are a friendly assistant specialized in Tshwane University of Technology (TUT). "
        "Answer questions related to courses, resources, student life, campus info, registration, and academics. "
        "Provide clear, concise, and helpful responses."
    )
    user_prompt = question

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 300,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(GROQ_URL, headers=headers, json=payload)
            response.raise_for_status()
            rdata = response.json()
            return rdata["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Sorry, I couldn't generate an answer due to: {e}"


@router.post("/")
async def chat_tut_bot(payload: dict):
    """
    Example payload:
    {
        "email": "student@example.com",
        "question": "How do I register for modules at TUT?"
    }
    """
    try:
        question = payload.get("question", "").strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question is required.")

        answer = await get_tut_guidance(question)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
