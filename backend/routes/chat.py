from fastapi import APIRouter
from pydantic import BaseModel
from core.memory import get_session
from services.llm_service import ask_llm

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@router.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    session = get_session(user_id)

    # add user message
    session.append({"role": "user", "content": req.message})

    # call model
    reply = ask_llm(session)

    # store reply
    session.append({"role": "assistant", "content": reply})

    return {"reply": reply}
