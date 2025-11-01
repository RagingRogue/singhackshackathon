import stripe
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import boto3

# Load env for Stripe
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
table = dynamodb.Table("Payments")  # ✅ Must already exist

# ✅ Use mock policies for now
with open("backend/data/mock_policies.json", "r") as f:
    POLICIES = json.load(f)

def create_checkout_session(policy_name: str):
    if policy_name not in POLICIES:
        raise ValueError(f"Policy '{policy_name}' not found in mock_policies.json")

    price = POLICIES[policy_name]["price"]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email="test@example.com",  # can change to dynamic later
        line_items=[{
            "price_data": {
                "currency": "sgd",
                "product_data": {"name": policy_name},
                "unit_amount": int(price * 100)
            },
            "quantity": 1
        }],
        success_url="http://localhost:3000/payment-success",
        cancel_url="http://localhost:3000/payment-cancel",
    )

    # Save to DB pending
    table.put_item(Item={
        "transaction_id": session.id,
        "policy_name": policy_name,
        "price": str(price),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    })

    return {"checkout_url": session.url}
