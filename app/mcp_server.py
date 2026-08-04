from mcp.server.fastmcp import FastMCP
from app.agents.document_search_agent import compiled_search_agent
from app.agents.meeting_summary_agent import compiled_meeting_agent
from app.agents.task_automation_agent import compiled_task_agent

mcp = FastMCP("enterprise-rag-platform")


@mcp.tool()
def document_search(query: str, session_id: str = "default") -> str:
    """Search stored documents and answer a question using retrieved context."""
    result = compiled_search_agent.invoke({
        "query": query,
        "session_id": session_id,
        "retrieved_docs": [],
        "answer": ""
    })
    return result["answer"]


@mcp.tool()
def meeting_summary(transcript: str, session_id: str = "default") -> str:
    """Summarize a meeting transcript into key points, decisions, and action items."""
    result = compiled_meeting_agent.invoke({
        "transcript": transcript,
        "session_id": session_id,
        "summary": ""
    })
    return result["summary"]


@mcp.tool()
def task_automation(request: str, session_id: str = "default") -> str:
    """Extract a prioritized task list from a natural language request."""
    result = compiled_task_agent.invoke({
        "request": request,
        "session_id": session_id,
        "tasks": ""
    })
    return result["tasks"]


if __name__ == "__main__":
    mcp.run()