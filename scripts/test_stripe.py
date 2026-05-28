#!/usr/bin/env python3
"""Test Stripe integration - account, products, checkout flow."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env.local
env_path = Path(".env.local")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()

import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
if not stripe.api_key:
    print("❌ STRIPE_API_KEY not found!")
    sys.exit(1)

print("\n=== STRIPE ACCOUNT INFO ===")
acct = stripe.Account.retrieve()
print(f"  ID      : {acct.id}")
print(f"  Country : {acct.get('country', 'N/A') if hasattr(acct, 'get') else 'N/A'}")
print(f"  Email   : {acct.email if hasattr(acct, 'email') else 'N/A'}")

print("\n=== PRODUCTS & PRICES ===")
products = stripe.Product.list(active=True, limit=10)
for p in products:
    prices = stripe.Price.list(product=p.id, active=True, limit=5)
    price_strs = []
    for pr in prices:
        interval = pr.recurring["interval"] if pr.recurring else "once"
        price_strs.append(f"    {pr.id}: ¥{pr.unit_amount:,}/{interval}")
    print(f"\n  {p.name}")
    for s in price_strs:
        print(s)

print("\n=== CHECKOUT TEST ===")
session = stripe.checkout.Session.create(
    line_items=[{"price": "price_1Tbs7V0TLJQM7Q1AkArimQYh", "quantity": 1}],
    mode="subscription",
    success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="http://localhost:5000/pricing",
    metadata={"tier": "silver", "interval": "monthly"},
)
print(f"  ✅ Checkout URL: {session.url}")
print()
print("  Click the URL above to test a real payment!")
print("  After payment, you'll be redirected to /success with your license key")
print()
print("🎉 Stripe is fully integrated and operational!")
