from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.db import SessionLocal
from app.models.conversation import Conversation
from app.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.google_api_key
)


class MeetingState(TypedDict):
    transcript: str
    session_id: str
    summary: str


def summarize_node(state: MeetingState) -> MeetingState:
    prompt = f"""Summarize the following meeting transcript into:
1. Key discussion points
2. Decisions made
3. Action items with owners (if mentioned)

Transcript:
{state["transcript"]}

Summary:"""
    response = llm.invoke(prompt)
    summary = response.content

    db = SessionLocal()
    try:
        db.add(Conversation(session_id=state.get("session_id", "default"), role="user", content=state["transcript"][:500], agent_type="meeting_summary"))
        db.add(Conversation(session_id=state.get("session_id", "default"), role="assistant", content=summary, agent_type="meeting_summary"))
        db.commit()
    finally:
        db.close()

    return {**state, "summary": summary}


workflow = StateGraph(MeetingState)
workflow.add_node("summarize", summarize_node)
workflow.set_entry_point("summarize")
workflow.add_edge("summarize", END)

compiled_meeting_agent = workflow.compile()