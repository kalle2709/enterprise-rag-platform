from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.document_search_agent import compiled_search_agent
from app.agents.meeting_summary_agent import compiled_meeting_agent
from app.agents.task_automation_agent import compiled_task_agent
from app.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.google_api_key
)


class SupervisorState(TypedDict):
    user_input: str
    session_id: str
    route: str
    result: str


def route_node(state: SupervisorState) -> SupervisorState:
    prompt = f"""Classify the user's request into exactly one category. Reply with only the category name, nothing else.

Categories:
- document_search: questions asking to look up or explain something from stored documents or general knowledge
- meeting_summary: input that looks like a meeting transcript or dialogue between multiple speakers (e.g. "Name: said something"), where the goal is to summarize what was discussed and decided
- task_automation: a request written as an instruction or to-do list asking to extract or organize action items, NOT a transcript of a conversation

Important: if the input contains multiple speaker names followed by colons (like a transcript), it is meeting_summary, even if some lines mention tasks.

Request: {state["user_input"]}

Category:"""
    response = llm.invoke(prompt)
    route = response.content.strip().lower()
    return {**state, "route": route}

def dispatch_node(state: SupervisorState) -> SupervisorState:
    route = state["route"]
    session_id = state.get("session_id", "default")

    if "document_search" in route:
        result = compiled_search_agent.invoke({
            "query": state["user_input"],
            "session_id": session_id,
            "retrieved_docs": [],
            "answer": ""
        })
        return {**state, "result": result["answer"]}

    elif "meeting_summary" in route:
        result = compiled_meeting_agent.invoke({
            "transcript": state["user_input"],
            "session_id": session_id,
            "summary": ""
        })
        return {**state, "result": result["summary"]}

    elif "task_automation" in route:
        result = compiled_task_agent.invoke({
            "request": state["user_input"],
            "session_id": session_id,
            "tasks": ""
        })
        return {**state, "result": result["tasks"]}

    else:
        return {**state, "result": "Could not determine which agent should handle this request."}


workflow = StateGraph(SupervisorState)
workflow.add_node("classify", route_node)
workflow.add_node("dispatch", dispatch_node)
workflow.set_entry_point("classify")
workflow.add_edge("classify", "dispatch")
workflow.add_edge("dispatch", END)

compiled_supervisor_agent = workflow.compile()