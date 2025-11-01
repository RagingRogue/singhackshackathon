from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, reset

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(chat.router)
app.include_router(reset.router)
