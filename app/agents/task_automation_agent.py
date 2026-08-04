
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


class TaskState(TypedDict):
    request: str
    session_id: str
    tasks: str


def extract_tasks_node(state: TaskState) -> TaskState:
    prompt = f"""Extract a clear, actionable task list from the request below. Format as a numbered list with priority (High/Medium/Low) for each.

Request:
{state["request"]}

Tasks:"""
    response = llm.invoke(prompt)
    tasks = response.content

    db = SessionLocal()
    try:
        db.add(Conversation(session_id=state.get("session_id", "default"), role="user", content=state["request"], agent_type="task_automation"))
        db.add(Conversation(session_id=state.get("session_id", "default"), role="assistant", content=tasks, agent_type="task_automation"))
        db.commit()
    finally:
        db.close()

    return {**state, "tasks": tasks}


workflow = StateGraph(TaskState)
workflow.add_node("extract_tasks", extract_tasks_node)
workflow.set_entry_point("extract_tasks")
workflow.add_edge("extract_tasks", END)

compiled_task_agent = workflow.compile()