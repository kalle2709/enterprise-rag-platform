from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.agents import document_search_agent
from app.db import get_db
from app.db.vectorstore import add_document_to_vectorstore, query_vectorstore
from app.models.document import Document
from app.models.schemas import DocumentCreate, DocumentResponse, QueryRequest
from app.agents.document_search_agent import compiled_search_agent

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    db_doc = Document(
        filename=payload.filename,
        content=payload.content,
        source=payload.source
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    add_document_to_vectorstore(
        doc_id=str(db_doc.id),
        text=payload.content,
        metadata={"filename": payload.filename, "source": payload.source or ""}
    )

    return db_doc


@router.post("/search")
def search_documents(payload: QueryRequest):
    results = query_vectorstore(payload.query, payload.n_results)
    return results

@router.post("/ask")
def ask_documents(payload: QueryRequest):
    result = compiled_search_agent.invoke({
        "query": payload.query,
        "retrieved_docs": [],
        "answer": ""
    })
    return {"answer": result["answer"], "sources": result["retrieved_docs"]}