import os
import stripe
import boto3
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path="backend/payments/.env")

# Stripe API and webhook secret
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# DynamoDB table
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("Payments")

def handle_webhook(payload, sig_header):
    try:
        # Verify webhook signature from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            transaction_id = session["id"]

            print(f"✅ Payment successful for session: {transaction_id}")

            # ✅ Update DynamoDB record to paid
            table.update_item(
                Key={"transaction_id": transaction_id},
                UpdateExpression="SET #status = :s, updated_at = :t",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":s": "paid",
                    ":t": session.get("created")
                }
            )

        return {"status": "success"}

    except Exception as e:
        print("❌ Webhook error:", str(e))
        return {"status": "error", "message": str(e)}
