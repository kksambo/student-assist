from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
import os
import asyncio
import fitz  # PyMuPDF for PDF text extraction

router = APIRouter(prefix="/llama", tags=["AI Study Assistant"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"


# =========================================
# Helper Function: Ask LLaMA via Groq
# =========================================
async def ask_llama(prompt: str) -> str:
    """Send a prompt to Groq’s LLaMA model and return the response."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an intelligent academic assistant. "
                    "Provide clear, structured explanations, summaries, and answers "
                    "suitable for students and tutors in South Africa."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(GROQ_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI request error: {e}")
        return f"Could not generate response due to: {e}"


# =========================================
# Endpoint: Ask AI a question
# =========================================
@router.post("/ask")
async def ask_study_assistant(data: dict):
    """General academic Q&A endpoint for learners."""
    prompt = data.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    result = await ask_llama(prompt)
    return {"answer": result}


# =========================================
# Helper Function: Extract text from PDF
# =========================================
def extract_pdf_text(file_path: str) -> str:
    """Extract readable text from a PDF file using PyMuPDF."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


# =========================================
# Endpoint: Summarize an uploaded PDF
# =========================================
@router.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    """Extract text from a PDF and summarize it using the LLaMA model."""
    try:
        # Save temporary file
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        text = extract_pdf_text(temp_path)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

        # Truncate if too long for token limits
        truncated = text[:3000]

        prompt = (
            "Summarize the following study material clearly and concisely for a learner:\n\n"
            f"{truncated}"
        )

        summary = await ask_llama(prompt)
        os.remove(temp_path)
        return {"summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing PDF: {e}")
