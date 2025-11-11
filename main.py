import asyncio
from fastapi import FastAPI
from routes import auth, resources,student_resources,chat,admin_resources,resource_router,finacial_aid,summaries
from models import Base
from database import engine  # async engine
from fastapi.middleware.cors import CORSMiddleware

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
