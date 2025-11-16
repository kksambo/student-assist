import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from routes import auth, resources,student_resources,chat,admin_resources,resource_router,finacial_aid,summaries
from models import Base
from database import engine  # async engine
from fastapi.middleware.cors import CORSMiddleware
import io
import json
import pdfplumber
import requests
import os
import re
import ast


import uvicorn

app = FastAPI(title="TUT Resources App")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # frontend URLs
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # allow all headers
)



app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resources.router, prefix="/api", tags=["resources"])
app.include_router(student_resources.router)
app.include_router(chat.router)
app.include_router(admin_resources.router)
app.include_router(resource_router.router)
app.include_router(finacial_aid.router)
app.include_router(summaries.router)


@app.on_event("startup")
async def init_models():
    # async create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

@app.get("/")
def root():
    return {"message": "TUT Resources API is running"}




GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OCRSPACE_API_KEY = os.getenv("OCRSPACE_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

# -----------------------
def ocr_extract_text(pdf_bytes: bytes) -> str:
    ocr_url = "https://api.ocr.space/parse/image"
    files = {"file": ("upload.pdf", pdf_bytes)}
    data = {"apikey": OCRSPACE_API_KEY, "language": "eng"}
    res = requests.post(ocr_url, data=data, files=files)
    res.raise_for_status()
    result = res.json()
    if result.get("IsErroredOnProcessing"):
        return ""
    parsed = result.get("ParsedResults", [])
    if not parsed:
        return ""
    return parsed[0].get("ParsedText", "")


# -----------------------
# PDF text extraction
# -----------------------
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        if text.strip():
            return text
    except Exception:
        pass
    return ocr_extract_text(pdf_bytes)


# -----------------------
# LLM: generate structured event details
# -----------------------
def generate_event_details(text: str) -> dict:
    prompt = f"""
You are an expert event information extractor.
Extract ONLY JSON with the following fields from this text:
- title
- description
- date
- time
- department

Output STRICTLY as valid JSON with no extra text, markdown, or comments.

TEXT TO ANALYZE:
{text}
"""

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "temperature": 0}

    res = requests.post(GROQ_URL, json=payload, headers=headers)
    if not res.ok:
        raise HTTPException(status_code=500, detail=f"LLM request failed: {res.text}")

    raw = res.json()["choices"][0]["message"]["content"].strip()

    # --- Attempt JSON parsing robustly ---
    try:
        # Remove unwanted characters outside {}
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            json_text = match.group()
        else:
            json_text = raw

        # Try json.loads
        try:
            data = json.loads(json_text)
        except:
            # Fallback using ast.literal_eval
            data = ast.literal_eval(json_text)

        # Ensure all fields exist
        for key in ["title", "description", "date", "time", "department"]:
            if key not in data:
                data[key] = ""

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM output: {str(e)}")


# -----------------------
# ROUTE
# -----------------------
@app.post("/extract-event")
async def extract_event(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF")

    event = generate_event_details(text)

    return {"success": True, "event": event}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
