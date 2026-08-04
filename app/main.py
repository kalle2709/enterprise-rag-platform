from fastapi import FastAPI
from app.routes import agents
from app.db import Base, engine
from app.models import document, conversation
from app.routes import documents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise RAG Platform",
    description="AI agent orchestration platform for document search, meeting summarization, and task automation",
    version="1.0.0"
)

app.include_router(documents.router)
app.include_router(agents.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}