from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.purchase import router as purchase_router

app = FastAPI(title="Payments Service")

# ✅ Allow frontend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Add payment routes
app.include_router(purchase_router)

@app.get("/")
def home():
    return {"message": "Payments API is running ✅"}
