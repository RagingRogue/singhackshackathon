from fastapi import APIRouter, Request, HTTPException
from backend.payments.services.stripe_service import create_checkout_session
from backend.payments.services.webhook_handler import handle_webhook

router = APIRouter()


@router.post("/purchase")
def purchase_policy(data: dict):
    """
    Example JSON:
    {
        "policy_name": "TravelEasy Silver",
        "price": 49.90,
        "user_email": "test@gmail.com"
    }
    """
    try:
        return create_checkout_session(
            policy_name=data["policy_name"],
            price=data["price"],
            user_email=data.get("user_email")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    return handle_webhook(payload, sig_header)
