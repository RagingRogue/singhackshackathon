import os
import stripe
from dotenv import load_dotenv
from backend.payments.services.policy_issuer import generate_policy


load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

def handle_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            email = session.get("customer_email", "unknown@user.com")

            policy = generate_policy(email=email, session_id=session.get("id"))
            print("✅ Payment successful. Policy issued:", policy)

        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}
