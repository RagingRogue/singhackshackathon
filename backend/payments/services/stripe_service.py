import boto3, os, stripe
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal   # ✅ Add this

# Load environment variables
load_dotenv(dotenv_path="backend/payments/.env")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("Payments")

def create_checkout_session(policy_name, price, user_email):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "sgd",
                "product_data": {"name": policy_name},
                "unit_amount": int(price * 100),  # in cents
            },
            "quantity": 1,
        }],
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )

    # ✅ Save to DynamoDB (no floats allowed!)
    table.put_item(
        Item={
            "transaction_id": session.id,
            "policy_name": policy_name,
            "user_email": user_email,
            "amount": Decimal(str(price)),  # ✅ Fix here
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
    )

    return {"checkout_url": session.url}
