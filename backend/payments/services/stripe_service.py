import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(policy_name: str, price: float, user_email: str = None):
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
    return {"checkout_url": session.url}
