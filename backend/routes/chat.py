from fastapi import APIRouter
from pydantic import BaseModel
from core.memory import get_session
from agents.controller import handle_message

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@router.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    session = get_session(user_id)
    session.append({"role": "user", "content": req.message})

    # Step 1: use agentic controller (routes to correct handler)
    reply = handle_message(req.message)

    # Step 2: store reply in memory
    session.append({"role": "assistant", "content": reply})

    return {"reply": reply}

