# OMEGA PRIME — Auto Money System
# Pipedream workflow for fully automated license delivery
# No server needed! 100% cloud, 100% free.

import os
import json
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timedelta, timezone

# ============================================================
# CONFIGURATION
# ============================================================
# These are set in Pipedream Environment Variables
OMEGA_SECRET_KEY = os.environ.get("OMEGA_SECRET_KEY", "")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

# Price ID → Tier mapping
PRICE_TIERS = {
    "price_1Tbs7U0TLJQM7Q1AYMR6Dc2h": ("bronze", 30),
    "price_1Tbs7U0TLJQM7Q1AutYfI0wz": ("bronze", 365),
    "price_1Tbs7V0TLJQM7Q1AkArimQYh": ("silver", 30),
    "price_1Tbs7V0TLJQM7Q1AgU8mmkvi": ("silver", 365),
    "price_1Tbs7W0TLJQM7Q1AeSWRXGUH": ("gold", 30),
    "price_1Tbs7X0TLJQM7Q1AMIapGGXB": ("gold", 365),
    "price_1Tbs7X0TLJQM7Q1AYaywJO9v": ("platinum", 3650),
}

# ============================================================
# LICENSE GENERATION
# ============================================================

def generate_license(customer_id, tier, days):
    """Generate HMAC-SHA256 license key (same as server-side)."""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=days)

    payload = {
        "customer_id": customer_id,
        "tier": tier,
        "issued_at": now.isoformat(),
        "expiry": expiry.isoformat(),
        "nonce": uuid.uuid4().hex[:16],
    }

    json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    sig = hmac.new(
        OMEGA_SECRET_KEY.encode("utf-8"),
        json_str.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.b64encode(sig).decode("utf-8")[:16]
    json_b64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    license_key = f"OMEGA-{json_b64}-{sig_b64}"
    return license_key, payload

# ============================================================
# PIPEDREAM WORKFLOW HANDLER
# ============================================================

async def handler(event):
    """
    Pipedream workflow handler.
    Trigger: Stripe webhook (checkout.session.completed)
    """
    # 1. Verify this is a checkout.session.completed event
    event_type = event.get("type", "")
    if event_type != "checkout.session.completed":
        return {"status": "ignored", "event": event_type}

    # 2. Get session data
    session = event["data"]["object"]
    customer_email = session.get("customer_details", {}).get("email", "")
    payment_status = session.get("payment_status", "")
    amount_total = session.get("amount_total", 0)
    currency = session.get("currency", "")

    if payment_status != "paid":
        return {"status": "pending", "message": "Payment not yet completed"}

    # 3. Get line items to determine tier
    # For payment links, we need to expand line_items
    line_items = session.get("line_items", {}).get("data", [])
    tier = "bronze"
    days = 30

    for item in line_items:
        price_id = item.get("price", {}).get("id", "")
        if price_id in PRICE_TIERS:
            tier, days = PRICE_TIERS[price_id]
            break

    # 4. Generate license
    license_key, payload = generate_license(
        customer_id=customer_email,
        tier=tier,
        days=days,
    )

    # 5. Log for Pipedream
    print(f"[OK] Payment received: {amount_total/100} {currency.upper()} from {customer_email}")
    print(f"[KEY] License generated ({tier}): {license_key[:50]}...")
    print(f"[EXP] Expires: {payload['expiry']}")

    # 6. Return result (Pipedream can send email via built-in action)
    return {
        "status": "success",
        "customer": customer_email,
        "tier": tier,
        "license_key": license_key,
        "expiry": payload["expiry"],
        "amount": amount_total / 100,
        "currency": currency,
    }

# ============================================================
# For local testing
# ============================================================
if __name__ == "__main__":
    import asyncio
    test_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer_details": {"email": "test@example.com"},
                "payment_status": "paid",
                "amount_total": 5000,
                "currency": "jpy",
                "line_items": {"data": [{"price": {"id": "price_1Tbs7V0TLJQM7Q1AkArimQYh"}}]},
            }
        },
    }
    os.environ["OMEGA_SECRET_KEY"] = "MyOmegaSuperSecretKey2026!"
    result = asyncio.run(handler(test_event))
    print(json.dumps(result, indent=2))
