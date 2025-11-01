from fastapi import APIRouter
from core.memory import clear_sessions

router = APIRouter()

@router.post("/reset")
async def reset_chat():
    clear_sessions()
    return {"status": "cleared"}
