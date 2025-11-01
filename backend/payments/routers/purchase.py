from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.stripe_service import create_checkout_session
from ..services.webhook_handler import LATEST_PAYMENT_STATUS

router = APIRouter(prefix="/payments", tags=["Payments"])

class PurchaseRequest(BaseModel):
    policy_name: str

@router.post("/purchase")
async def purchase(req: PurchaseRequest):
    try:
        result = create_checkout_session(req.policy_name)
        return {
            "message": "Checkout session created",
            "checkout_url": result["checkout_url"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_status():
    return {"latest_payment_status": LATEST_PAYMENT_STATUS}
