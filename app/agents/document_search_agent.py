from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.db.vectorstore import query_vectorstore
from app.config import settings
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.db import SessionLocal

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.google_api_key
)


class AgentState(TypedDict):
    query: str
    session_id: str
    retrieved_docs: List[str]
    answer: str
    
def retrieve_node(state: AgentState) -> AgentState:
    results = query_vectorstore(state["query"], n_results=3)
    docs = results.get("documents", [[]])[0]
    return {**state, "retrieved_docs": docs}


def generate_node(state: AgentState) -> AgentState:
    context = "\n\n".join(state["retrieved_docs"])
    prompt = f"""Answer the question using only the context below. If the context doesn't contain the answer, say so.

    Context:
    {context}

    Question: {state["query"]}

    Answer:"""
    response = llm.invoke(prompt)
    answer = response.content

    db = SessionLocal()
    try:
        db.add(Conversation(session_id=state.get("session_id", "default"), role="user", content=state["query"], agent_type="document_search"))
        db.add(Conversation(session_id=state.get("session_id", "default"), role="assistant", content=answer, agent_type="document_search"))
        db.commit()
    finally:
        db.close()

    return {**state, "answer": answer}

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

compiled_search_agent = workflow.compile()