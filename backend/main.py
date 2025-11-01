from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# FastAPI setup
app = FastAPI()

# Enable CORS so your Vite frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session history
chat_sessions = {}  # e.g., {"default_user": [{"role": "user", "content": "..."}, ...]}

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/chat")
async def chat(req: ChatRequest):
    """Chat endpoint with memory"""
    user_id = req.user_id
    user_msg = {"role": "user", "content": req.message}

    # Initialize session if new
    if user_id not in chat_sessions:
        chat_sessions[user_id] = [
            {"role": "system", "content": "You are Milo, a friendly and witty travel insurance assistant who remembers past context."}
        ]

    # Add user message to history
    chat_sessions[user_id].append(user_msg)

    # Call Groq API with full chat history
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=chat_sessions[user_id],
        temperature=0.8,
        max_completion_tokens=1024,
    )

    reply = completion.choices[0].message.content.strip()

    # Store assistant reply in memory
    chat_sessions[user_id].append({"role": "assistant", "content": reply})

    return {"reply": reply}

@app.post("/reset")
async def reset_chat():
    """Optional endpoint to clear all session memory"""
    chat_sessions.clear()
    return {"status": "cleared"}
