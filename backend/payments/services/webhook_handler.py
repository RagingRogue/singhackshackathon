import os
import stripe
from dotenv import load_dotenv
import boto3
from fastapi import APIRouter, Header, HTTPException, Request

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("Payments")

router = APIRouter(prefix="/webhook", tags=["Stripe Webhook"])
LATEST_PAYMENT_STATUS = "None"

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    global LATEST_PAYMENT_STATUS
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Webhook signature failed")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]

        table.update_item(
            Key={"transaction_id": session_id},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "success"}
        )

        LATEST_PAYMENT_STATUS = "✅ Payment completed!"

    return {"status": "received"}
