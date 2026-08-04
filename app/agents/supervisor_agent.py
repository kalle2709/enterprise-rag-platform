import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.google_api_key
)

server_params = StdioServerParameters(
    command="python",
    args=["-m", "app.mcp_server"],
    env={"PYTHONPATH": "."}
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


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text


def dispatch_node(state: SupervisorState) -> SupervisorState:
    route = state["route"]
    session_id = state.get("session_id", "default")

    if "document_search" in route:
        result = asyncio.run(call_mcp_tool("document_search", {
            "query": state["user_input"],
            "session_id": session_id
        }))
    elif "meeting_summary" in route:
        result = asyncio.run(call_mcp_tool("meeting_summary", {
            "transcript": state["user_input"],
            "session_id": session_id
        }))
    elif "task_automation" in route:
        result = asyncio.run(call_mcp_tool("task_automation", {
            "request": state["user_input"],
            "session_id": session_id
        }))
    else:
        result = "Could not determine which agent should handle this request."

    return {**state, "result": result}


workflow = StateGraph(SupervisorState)
workflow.add_node("classify", route_node)
workflow.add_node("dispatch", dispatch_node)
workflow.set_entry_point("classify")
workflow.add_edge("classify", "dispatch")
workflow.add_edge("dispatch", END)

compiled_supervisor_agent = workflow.compile()