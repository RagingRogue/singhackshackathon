from fastapi import FastAPI
from backend.payments.routers.purchase import router as purchase_router

app = FastAPI()

app.include_router(purchase_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Payment API is running!"}
