from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.meeting_summary_agent import compiled_meeting_agent
from app.agents.task_automation_agent import compiled_task_agent
from app.agents.supervisor_agent import compiled_supervisor_agent

router = APIRouter(prefix="/agents", tags=["agents"])


class MeetingRequest(BaseModel):
    transcript: str
    session_id: str = "default"


class TaskRequest(BaseModel):
    request: str
    session_id: str = "default"


class SupervisorRequest(BaseModel):
    input: str
    session_id: str = "default"


@router.post("/summarize-meeting")
def summarize_meeting(payload: MeetingRequest):
    result = compiled_meeting_agent.invoke({
        "transcript": payload.transcript,
        "session_id": payload.session_id,
        "summary": ""
    })
    return {"summary": result["summary"]}


@router.post("/extract-tasks")
def extract_tasks(payload: TaskRequest):
    result = compiled_task_agent.invoke({
        "request": payload.request,
        "session_id": payload.session_id,
        "tasks": ""
    })
    return {"tasks": result["tasks"]}


@router.post("/route")
def route_request(payload: SupervisorRequest):
    result = compiled_supervisor_agent.invoke({
        "user_input": payload.input,
        "session_id": payload.session_id,
        "route": "",
        "result": ""
    })
    return {"routed_to": result["route"], "result": result["result"]}