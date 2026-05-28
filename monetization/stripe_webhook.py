#!/usr/bin/env python3
"""
==================================================================================
OMEGA PRIME — Stripe Payment Webhook
==================================================================================

Auto-generate license keys when customers pay via Stripe.

Flow:
    1. Customer clicks Stripe Payment Link
    2. Stripe processes payment
    3. Stripe sends webhook POST to this server
    4. This script generates an HMAC-signed license key
    5. Email sent to customer with license key (or returned via API)

Deployment:
    # Test locally
    python stripe_webhook.py --port 8080
    
    # Deploy with ngrok (for Stripe test webhook)
    ngrok http 8080
    # Then set webhook URL in Stripe Dashboard:
    # https://dashboard.stripe.com/webhooks

Requirements:
    pip install flask stripe

Environment Variables:
    OMEGA_SECRET_KEY    — Secret key for HMAC license signing
    STRIPE_WEBHOOK_SECRET — Stripe webhook signing secret
    STRIPE_API_KEY      — Stripe secret key (sk_live_...)
    SMTP_SERVER         — SMTP server for email delivery (optional)
    SMTP_USERNAME       — SMTP login (optional)
    SMTP_PASSWORD       — SMTP password (optional)
==================================================================================
"""

import os
import sys
import json
import hmac
import hashlib
import base64
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Try importing optional dependencies
try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

try:
    import stripe
    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

# License tiers mapped to Stripe Price IDs
STRIPE_PRICE_TO_TIER = {
    # 🥉 Bronze
    "price_bronze_monthly": {"tier": "bronze", "days": 30},
    "price_bronze_yearly":  {"tier": "bronze", "days": 365},
    # 🥈 Silver
    "price_silver_monthly":  {"tier": "silver", "days": 30},
    "price_silver_yearly":   {"tier": "silver", "days": 365},
    # 🥇 Gold
    "price_gold_monthly":    {"tier": "gold", "days": 30},
    "price_gold_yearly":     {"tier": "gold", "days": 365},
    # 💎 Platinum
    "price_platinum":        {"tier": "platinum", "days": 365 * 10},  # 10 years
}

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("omega-license")


# ------------------------------------------------------------------
# License Generation
# ------------------------------------------------------------------

def get_secret_key():
    """Get OMEGA_SECRET_KEY from environment."""
    key = os.environ.get("OMEGA_SECRET_KEY")
    if not key:
        logger.error("OMEGA_SECRET_KEY not set!")
        sys.exit(1)
    return key


def generate_license(customer_id: str, tier: str, days: int) -> str:
    """
    Generate HMAC-SHA256 license key.
    Compatible with OmegaPrime.Production.SecurityValidator.
    
    Format: OMEGA-{base64_json}-{base64_hmac_truncated_16}
    """
    secret_key = get_secret_key()
    
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=days)
    
    payload = {
        "customer_id": customer_id,
        "tier": tier,
        "issued_at": now.isoformat(),
        "expiry": expiry.isoformat(),
        "nonce": __import__("uuid").uuid4().hex[:16],
    }
    
    json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    
    sig = hmac.new(
        secret_key.encode("utf-8"),
        json_str.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.b64encode(sig).decode("utf-8")[:16]
    
    json_b64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    
    return f"OMEGA-{json_b64}-{sig_b64}"


# ------------------------------------------------------------------
# Stripe Webhook Handler
# ------------------------------------------------------------------

def handle_stripe_event(payload: dict, sig_header: str = None) -> dict:
    """
    Process Stripe webhook event and generate license.
    
    Args:
        payload: Raw request body (bytes)
        sig_header: Stripe-Signature header
        
    Returns:
        dict with result status
    """
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    if HAS_STRIPE and webhook_secret:
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return {"status": "error", "message": "Invalid signature"}
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return {"status": "error", "message": "Invalid payload"}
    else:
        # For testing without Stripe SDK
        event = payload if isinstance(payload, dict) else json.loads(payload)
    
    logger.info(f"Received event: {event.get('type', 'unknown')}")
    
    # Handle checkout.session.completed
    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        return handle_checkout_completed(session)
    
    # Handle invoice.paid (subscription renewals)
    elif event.get("type") == "invoice.paid":
        invoice = event["data"]["object"]
        return handle_invoice_paid(invoice)
    
    # Handle customer.subscription.updated
    elif event.get("type") == "customer.subscription.updated":
        subscription = event["data"]["object"]
        return handle_subscription_updated(subscription)
    
    return {"status": "ignored", "event_type": event.get("type")}


def handle_checkout_completed(session: dict) -> dict:
    """Process completed checkout session."""
    customer_email = session.get("customer_details", {}).get("email", "unknown")
    customer_name = session.get("customer_details", {}).get("name", customer_email)
    price_id = session.get("line_items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
    
    # Determine tier from price ID
    tier_info = STRIPE_PRICE_TO_TIER.get(price_id, {"tier": "bronze", "days": 30})
    tier = tier_info["tier"]
    days = tier_info["days"]
    
    # Generate license
    license_key = generate_license(customer_email, tier, days)
    
    logger.info(f"✅ License generated for {customer_email} ({tier}, {days} days)")
    logger.info(f"   License key: {license_key[:50]}...")
    
    # TODO: Send email with license key
    # send_license_email(customer_email, license_key, tier, days)
    
    # Store in database (optional)
    # store_license(customer_email, license_key, tier, days)
    
    return {
        "status": "success",
        "customer": customer_email,
        "tier": tier,
        "license_key": license_key,
    }


def handle_invoice_paid(invoice: dict) -> dict:
    """Process subscription renewal invoice."""
    customer_email = invoice.get("customer_email", "unknown")
    subscription_id = invoice.get("subscription", "unknown")
    
    logger.info(f"💰 Invoice paid for {customer_email} (subscription: {subscription_id})")
    
    # Extend existing license by the billing period
    lines = invoice.get("lines", {}).get("data", [])
    for line in lines:
        price_id = line.get("price", {}).get("id", "")
        tier_info = STRIPE_PRICE_TO_TIER.get(price_id, {"tier": "bronze", "days": 30})
        
        license_key = generate_license(customer_email, tier_info["tier"], tier_info["days"])
        
        logger.info(f"🔄 License renewed for {customer_email}")
        
        return {
            "status": "renewed",
            "customer": customer_email,
            "tier": tier_info["tier"],
            "license_key": license_key,
        }
    
    return {"status": "ignored"}


def handle_subscription_updated(subscription: dict) -> dict:
    """Process subscription changes (upgrades/downgrades/cancellations)."""
    customer_email = subscription.get("customer", {}).get("email", "unknown")
    status = subscription.get("status", "unknown")
    
    logger.info(f"📊 Subscription {status} for {customer_email}")
    
    if status == "canceled":
        # TODO: Mark license as cancelled
        logger.info(f"⚠️  License cancelled for {customer_email}")
    elif status == "past_due":
        logger.info(f"⚠️  Payment past due for {customer_email}")
    
    return {"status": "processed", "subscription_status": status}


# ------------------------------------------------------------------
# Flask Web Server
# ------------------------------------------------------------------

def create_app():
    """Create Flask application."""
    if not HAS_FLASK:
        logger.error("Flask not installed. Run: pip install flask")
        return None
    
    app = Flask(__name__)
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "service": "omega-license-server"})
    
    @app.route("/webhook/stripe", methods=["POST"])
    def stripe_webhook():
        """Receive Stripe webhook events."""
        payload = request.get_data()
        sig_header = request.headers.get("Stripe-Signature", "")
        
        result = handle_stripe_event(payload, sig_header)
        
        if result.get("status") == "error":
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    @app.route("/api/validate", methods=["POST"])
    def validate_license_api():
        """Validate a license key via API."""
        data = request.get_json()
        if not data or "license_key" not in data:
            return jsonify({"valid": False, "error": "Missing license_key"}), 400
        
        from generate_license import validate_license
        result = validate_license(data["license_key"])
        
        return jsonify(result), 200 if result.get("valid") else 401
    
    @app.route("/api/generate", methods=["POST"])
    def generate_license_api():
        """Generate a new license key (admin only)."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        
        # Simple API key check
        api_key = request.headers.get("X-API-Key", "")
        expected_key = os.environ.get("LICENSE_API_KEY", "")
        if expected_key and api_key != expected_key:
            return jsonify({"error": "Unauthorized"}), 403
        
        customer = data.get("customer")
        tier = data.get("tier", "silver")
        days = data.get("days", 365)
        
        if not customer:
            return jsonify({"error": "Missing customer"}), 400
        
        license_key = generate_license(customer, tier, days)
        
        return jsonify({
            "license_key": license_key,
            "customer": customer,
            "tier": tier,
            "days": days,
        }), 200
    
    return app


def main():
    """Start the license server."""
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8080
    
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║        OMEGA PRIME — License Server              ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"  🚀  Server starting on port {port}...")
    print(f"  📋  POST /webhook/stripe  — Stripe webhook")
    print(f"  📋  POST /api/validate    — License validation API")
    print(f"  📋  POST /api/generate    — Admin license generation")
    print(f"  📋  GET  /health          — Health check")
    print()
    
    if not HAS_FLASK:
        print("❌  Flask not installed!")
        print("   Install: pip install flask stripe")
        sys.exit(1)
    
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
