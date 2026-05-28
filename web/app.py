#!/usr/bin/env python3
"""
===========================================================================
OMEGA PRIME — Web License Store
===========================================================================
Complete web application for selling OMEGA PRIME licenses.

Pages:
  /              — Landing page
  /pricing       — Pricing & plans
  /checkout/<tier> — Stripe checkout redirect
  /success       — License key after payment
  /validate      — License validation tool
  /admin         — Admin dashboard (API key required)
  /health        — Health check

Run:
    python web/app.py
    # Open http://localhost:5000

Environment:
    OMEGA_SECRET_KEY     — HMAC signing key (REQUIRED)
    STRIPE_API_KEY       — Stripe secret key
    STRIPE_PUBLIC_KEY    — Stripe publishable key
    LICENSE_API_KEY      — Admin API key
===========================================================================
"""

import os
import sys
import json
import uuid
import hmac
import hashlib
import base64
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from monetization.generate_license import generate_license, validate_license as py_validate

# Load .env.local if present (must be before any config reads)
_env_path = Path(__file__).parent.parent / ".env.local"
if _env_path.exists():
    print(f"📄 Loading environment from: {_env_path}")
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

try:
    from flask import (
        Flask, render_template, request, jsonify, redirect,
        url_for, session, flash
    )
    from flask_cors import CORS
except ImportError:
    print("❌ Flask not installed! Run: pip install flask flask-cors")
    sys.exit(1)

try:
    import stripe
except ImportError:
    stripe = None

# ==========================================================================
# Configuration
# ==========================================================================

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", os.urandom(32).hex())
    OMEGA_SECRET_KEY = os.environ.get("OMEGA_SECRET_KEY", "")
    STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_xxxxxxxx")
    LICENSE_API_KEY = os.environ.get("LICENSE_API_KEY", "admin123")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

    # Stripe Price IDs (replace with your Stripe Dashboard IDs)
    # Format: {tier}_{interval} = "price_xxxx"
    STRIPE_PRICES = {
        "bronze_monthly": os.environ.get("STRIPE_BRONZE_MONTHLY", "price_bronze_monthly"),
        "bronze_yearly":  os.environ.get("STRIPE_BRONZE_YEARLY", "price_bronze_yearly"),
        "silver_monthly": os.environ.get("STRIPE_SILVER_MONTHLY", "price_silver_monthly"),
        "silver_yearly":  os.environ.get("STRIPE_SILVER_YEARLY", "price_silver_yearly"),
        "gold_monthly":   os.environ.get("STRIPE_GOLD_MONTHLY", "price_gold_monthly"),
        "gold_yearly":    os.environ.get("STRIPE_GOLD_YEARLY", "price_gold_yearly"),
        "platinum":       os.environ.get("STRIPE_PLATINUM", "price_platinum"),
    }

# ==========================================================================
# App Setup
# ==========================================================================

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
CORS(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omega-web")

if stripe and Config.STRIPE_API_KEY:
    stripe.api_key = Config.STRIPE_API_KEY

# ==========================================================================
# Tier Data (shared across templates)
# ==========================================================================

TIERS = [
    {
        "id": "free",
        "name": "Free",
        "emoji": "🆓",
        "price_monthly": 0,
        "price_yearly": 0,
        "price_label": "ฟรี",
        "popular": False,
        "features": [
            "Full source code (C# + Python)",
            "Build & run locally",
            "Community support",
            "MIT License",
            "Docker Compose (6 services)",
            "CI/CD pipeline template",
        ],
        "disabled_features": [
            "License Key Activation",
            "Commercial Use",
            "API Access",
            "Priority Support",
        ],
        "color": "gray",
        "stripe_id": None,
    },
    {
        "id": "bronze",
        "name": "Bronze",
        "emoji": "🥉",
        "price_monthly": 1000,
        "price_label": "¥1,000",
        "popular": False,
        "features": [
            "ทุกอย่างใน Free",
            "GitHub Sponsor badge",
            "Priority support (24h)",
            "Discord role พิเศษ",
            "Roadmap meeting รายเดือน",
        ],
        "disabled_features": [
            "License Key Activation",
            "Commercial Use",
            "API Access",
        ],
        "color": "#CD7F32",
        "stripe_id_monthly": Config.STRIPE_PRICES["bronze_monthly"],
        "stripe_id_yearly": Config.STRIPE_PRICES["bronze_yearly"],
    },
    {
        "id": "silver",
        "name": "Silver",
        "emoji": "🥈",
        "price_monthly": 5000,
        "price_label": "¥5,000",
        "popular": True,
        "features": [
            "ทุกอย่างใน Bronze",
            "✅ License Key แท้!",
            "✅ Online License Validation",
            "✅ API Access",
            "✅ License Dashboard",
            "✅ Commercial Use",
            "✅ 1,000 Nodes (Premium)",
        ],
        "disabled_features": [
            "White-Label Branding",
            "Dedicated Support",
        ],
        "color": "#C0C0C0",
        "stripe_id_monthly": Config.STRIPE_PRICES["silver_monthly"],
        "stripe_id_yearly": Config.STRIPE_PRICES["silver_yearly"],
    },
    {
        "id": "gold",
        "name": "Gold",
        "emoji": "🥇",
        "price_monthly": 20000,
        "price_label": "¥20,000",
        "popular": False,
        "features": [
            "ทุกอย่างใน Silver",
            "✅ White-Label Ready",
            "✅ Custom Feature (1 เรื่อง/เดือน)",
            "✅ SLA 99.9%",
            "✅ Priority Support Queue",
            "✅ 10,000 Nodes",
        ],
        "disabled_features": [
            "Dedicated Support Engineer",
        ],
        "color": "#FFD700",
        "stripe_id_monthly": Config.STRIPE_PRICES["gold_monthly"],
        "stripe_id_yearly": Config.STRIPE_PRICES["gold_yearly"],
    },
    {
        "id": "platinum",
        "name": "Platinum",
        "emoji": "💎",
        "price_monthly": 50000,
        "price_label": "¥50,000",
        "popular": False,
        "is_once": True,
        "features": [
            "ทุกอย่างใน Gold",
            "✅ Full IP Transfer (ตลอดชีพ)",
            "✅ Dedicated Support Engineer",
            "✅ On-Premise License Server",
            "✅ Custom Integration",
            "✅ Source Code Escrow",
            "✅ Named Commercial License",
            "✅ Unlimited Nodes",
        ],
        "disabled_features": [],
        "color": "#B9F2FF",
        "stripe_id": Config.STRIPE_PRICES["platinum"],
    },
]

# ==========================================================================
# Routes: Core Pages
# ==========================================================================

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html", tiers=TIERS, 
                         stripe_key=Config.STRIPE_PUBLIC_KEY)


@app.route("/pricing")
def pricing():
    """Pricing page."""
    return render_template("pricing.html", tiers=TIERS,
                         stripe_key=Config.STRIPE_PUBLIC_KEY)


@app.route("/success")
def success():
    """Payment success — show license key.
    
    Supports two flows:
    1. Demo mode: license_key in session (from demo_checkout)
    2. Stripe mode: session_id in query string (from Stripe redirect)
    """
    # Flow 1: Demo mode (session already has key)
    license_key = session.pop("license_key", None)
    tier = session.pop("license_tier", None)
    customer = session.pop("license_customer", None)
    expiry = session.pop("license_expiry", None)

    # Flow 2: Stripe mode — retrieve session and generate license
    session_id = request.args.get("session_id")
    if not license_key and session_id and stripe:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            email = checkout_session.get("customer_details", {}).get("email", "customer@stripe.com")
            metadata = checkout_session.get("metadata", {})
            pay_tier = metadata.get("tier", "silver")
            pay_interval = metadata.get("interval", "monthly")

            days = 30 if pay_interval == "monthly" else 365
            if pay_tier == "platinum":
                days = 3650

            # Generate license from the webhook-compatible function
            result = generate_license(customer_id=email, tier=pay_tier, expiry_days=days)
            license_key = result["license_key"]
            tier = pay_tier
            customer = email
            expiry = result["expiry"]

            logger.info(f"💳 Stripe payment completed: {email} ({pay_tier})")
        except Exception as e:
            logger.error(f"Stripe session retrieval error: {e}")
            return redirect(url_for("pricing"))

    if not license_key:
        return redirect(url_for("pricing"))
    
    return render_template("success.html",
                         license_key=license_key,
                         tier=tier,
                         customer=customer,
                         expiry=expiry)


@app.route("/validate")
def validate_page():
    """License validation page."""
    return render_template("validate.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "omega-license-store",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

# ==========================================================================
# Routes: Stripe Checkout
# ==========================================================================

@app.route("/checkout/<tier>")
def checkout(tier):
    """Create Stripe Checkout Session."""
    if not stripe:
        flash("Stripe not configured. Contact admin.", "error")
        return redirect(url_for("pricing"))

    interval = request.args.get("interval", "monthly")
    price_id = None
    
    # Find the tier config
    tier_config = next((t for t in TIERS if t["id"] == tier), None)
    if not tier_config:
        flash("Invalid tier", "error")
        return redirect(url_for("pricing"))

    # Get Stripe price ID
    if tier == "platinum":
        price_id = Config.STRIPE_PRICES["platinum"]
    elif interval == "yearly":
        price_id = Config.STRIPE_PRICES.get(f"{tier}_yearly")
    else:
        price_id = Config.STRIPE_PRICES.get(f"{tier}_monthly")

    if not price_id or price_id.startswith("price_"):
        # Demo mode — generate license directly without Stripe
        return demo_checkout(tier, interval, tier_config)

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription" if tier != "platinum" else "payment",
            success_url=request.host_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url + "pricing",
            metadata={"tier": tier, "interval": interval},
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        flash(f"Payment error: {e}", "error")
        return redirect(url_for("pricing"))


def demo_checkout(tier, interval, tier_config):
    """Demo mode — generate license without real payment."""
    if not Config.OMEGA_SECRET_KEY:
        Config.OMEGA_SECRET_KEY = "DemoSecretKey12345"

    # Determine duration
    days = 30 if interval == "monthly" else 365
    if tier == "platinum":
        days = 3650  # 10 years

    email = request.args.get("email", f"demo-{uuid.uuid4().hex[:8]}@omegaprime.dev")

    # Generate license
    result = generate_license(
        customer_id=email,
        tier=tier,
        expiry_days=days,
    )

    session["license_key"] = result["license_key"]
    session["license_tier"] = tier
    session["license_customer"] = email
    session["license_expiry"] = result["expiry"]

    logger.info(f"🔑 Demo license generated for {email} ({tier})")
    return redirect(url_for("success"))


# ==========================================================================
# Routes: Stripe Webhook
# ==========================================================================

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    """Receive Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    if webhook_secret and stripe:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe.error.SignatureVerificationError:
            return jsonify({"error": "Invalid signature"}), 400
    else:
        event = request.get_json()

    event_type = event.get("type", "unknown")
    logger.info(f"📩 Stripe event: {event_type}")

    if event_type == "checkout.session.completed":
        session_data = event["data"]["object"]
        email = session_data.get("customer_details", {}).get("email", "unknown")
        metadata = session_data.get("metadata", {})
        tier = metadata.get("tier", "silver")
        interval = metadata.get("interval", "monthly")

        days = 30 if interval == "monthly" else 365
        if tier == "platinum":
            days = 3650

        result = generate_license(customer_id=email, tier=tier, expiry_days=days)
        logger.info(f"✅ License delivered to {email} ({tier})")

        # TODO: Send email with license key
        return jsonify({"status": "success", "license": result["license_key"]}), 200

    return jsonify({"status": "ignored"}), 200


# ==========================================================================
# Routes: API Endpoints
# ==========================================================================

@app.route("/api/validate", methods=["POST"])
def api_validate():
    """Validate a license key."""
    data = request.get_json()
    if not data or "license_key" not in data:
        return jsonify({"valid": False, "error": "Missing license_key"}), 400

    result = py_validate(data["license_key"])
    return jsonify(result)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate a license (admin only)."""
    api_key = request.headers.get("X-API-Key", "")
    if api_key != Config.LICENSE_API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    customer = data.get("customer", request.remote_addr)
    tier = data.get("tier", "silver")
    days = data.get("days", 365)

    if not Config.OMEGA_SECRET_KEY:
        return jsonify({"error": "OMEGA_SECRET_KEY not configured"}), 500

    result = generate_license(customer_id=customer, tier=tier, expiry_days=days)

    return jsonify({
        "license_key": result["license_key"],
        "customer": customer,
        "tier": tier,
        "expiry": result["expiry"],
        "features": result["features"],
    })


@app.route("/api/license-info", methods=["POST"])
def api_license_info():
    """Get info about a license key (no secret key needed for parse only)."""
    data = request.get_json()
    if not data or "license_key" not in data:
        return jsonify({"error": "Missing license_key"}), 400

    try:
        parts = data["license_key"].split("-")
        if len(parts) != 3 or parts[0] != "OMEGA":
            return jsonify({"error": "Invalid format"}), 400

        json_bytes = base64.b64decode(parts[1])
        payload = json.loads(json_bytes.decode("utf-8"))

        return jsonify({
            "customer_id": payload.get("customer_id"),
            "tier": payload.get("tier", "free"),
            "issued_at": payload.get("issued_at"),
            "expiry": payload.get("expiry"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================================================================
# Routes: Admin Dashboard
# ==========================================================================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin dashboard."""
    # Simple auth
    auth_error = None
    authenticated = False

    if request.method == "POST":
        if request.form.get("api_key") == Config.LICENSE_API_KEY:
            authenticated = True
            session["admin_auth"] = True
        else:
            auth_error = "Invalid API Key"

    if session.get("admin_auth"):
        authenticated = True

    if not authenticated:
        return render_template("admin.html", auth_error=auth_error)

    return render_template("admin.html", authenticated=True, tiers=TIERS,
                         license_api_key=Config.LICENSE_API_KEY,
                         stripe_configured=bool(Config.STRIPE_API_KEY),
                         omega_key_set=bool(Config.OMEGA_SECRET_KEY))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_auth", None)
    return redirect(url_for("admin"))


# ==========================================================================
# Error Handlers
# ==========================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", error_code=404,
                         error_msg="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("base.html", error_code=500,
                         error_msg="Internal server error"), 500


# ==========================================================================
# Main
# ==========================================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║     OMEGA PRIME — License Store v2.0            ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"  🚀  http://localhost:{Config.PORT}")
    print(f"  📋  Pages:")
    print(f"      /                — Landing / Hero")
    print(f"      /pricing         — Pricing tiers")
    print(f"      /checkout/<tier> — Buy license")
    print(f"      /success         — License key delivery")
    print(f"      /validate        — Check license")
    print(f"      /admin           — Dashboard")
    print(f"      /health          — Health check")
    print()
    print(f"  🔑  OMEGA_SECRET_KEY: {'✅ Set' if Config.OMEGA_SECRET_KEY else '❌ Not set'}")
    print(f"  💳  Stripe: {'✅ Configured' if Config.STRIPE_API_KEY else '⚡ Demo mode'}")
    print()

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
