from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse  # ✅ Missing import added!
from dotenv import load_dotenv
import os

# ✅ Load .env from inside payments folder
load_dotenv(dotenv_path="backend/payments/.env")

# ✅ Debug to verify environment variable loads
print("Stripe Key Loaded:", os.getenv("STRIPE_SECRET_KEY") is not None)

app = FastAPI()

# ✅ Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later (e.g., to http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include payment routes
from backend.payments.routers.purchase import router as purchase_router
app.include_router(purchase_router, prefix="/api")

# ✅ SUCCESS PAGE
@app.get("/success", response_class=HTMLResponse)
def success_page():
    return """
    <html>
        <body style="font-family: Arial; text-align:center; padding-top: 50px;">
            <h2>✅ Payment Successful!</h2>
            <p>Your policy will be issued shortly.</p>
        </body>
    </html>
    """

# ✅ CANCEL PAGE
@app.get("/cancel", response_class=HTMLResponse)
def cancel_page():
    return """
    <html>
        <body style="font-family: Arial; text-align:center; padding-top: 50px;">
            <h2>❌ Payment Cancelled</h2>
            <p>Your transaction was not completed. You can try again anytime.</p>
        </body>
    </html>
    """

# ✅ HEALTH CHECK / BASE ROUTE
@app.get("/")
def root():
    return {"message": "Payment API is running!"}
