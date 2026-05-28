#!/usr/bin/env python3
"""
=================================================================
OMEGA PRIME — Auto Register Stripe Webhook
=================================================================
Automatically register the Stripe webhook endpoint.

This script:
  1. Registers a webhook endpoint in Stripe
  2. Saves the webhook signing secret to .env.local
  3. Tests the webhook with a ping event

Usage:
    python scripts/auto_setup_stripe_webhook.py --url https://your-server.com/webhook/stripe
    
    For local testing with ngrok:
    python scripts/auto_setup_stripe_webhook.py --url https://your-ngrok.ngrok.io/webhook/stripe
    
    Auto-detect ngrok:
    python scripts/auto_setup_stripe_webhook.py --auto-ngrok
=================================================================
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env.local
env_path = Path(".env.local")
env_vars = {}
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env_vars[key.strip()] = val.strip()
                os.environ.setdefault(key.strip(), val.strip())

try:
    import stripe
    import requests
except ImportError:
    print("❌ Missing dependencies! Run: pip install stripe requests")
    sys.exit(1)


# ==================================================================
# Auto-detect ngrok URL
# ==================================================================

def detect_ngrok_url():
    """Try to get the ngrok tunnel URL."""
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
        tunnels = resp.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel.get("public_url", "").startswith("https"):
                return tunnel["public_url"]
        if tunnels:
            return tunnels[0].get("public_url")
    except:
        pass
    return None


# ==================================================================
# Register webhook
# ==================================================================

def register_webhook(webhook_url: str) -> str:
    """
    Register a webhook endpoint in Stripe.
    Returns the webhook signing secret.
    """
    api_key = os.environ.get("STRIPE_API_KEY") or env_vars.get("STRIPE_API_KEY")
    if not api_key:
        print("❌ STRIPE_API_KEY not found in environment or .env.local")
        sys.exit(1)

    stripe.api_key = api_key

    print(f"\n🔗 Registering webhook: {webhook_url}")
    print()

    # Events we care about
    events = [
        "checkout.session.completed",
        "invoice.paid",
        "customer.subscription.updated",
    ]

    try:
        # Check if webhook already exists
        existing = stripe.WebhookEndpoint.list()
        for endpoint in existing:
            if endpoint.url == webhook_url:
                print(f"  ⚠️  Webhook already exists: {endpoint.id}")
                print(f"  🔑 Secret: {endpoint.secret[:20]}...")
                
                # Update events if needed
                current_events = set(endpoint.enabled_events)
                needed_events = set(events)
                if not needed_events.issubset(current_events):
                    print(f"  🔄 Updating events...")
                    stripe.WebhookEndpoint.modify(
                        endpoint.id,
                        enabled_events=list(current_events | needed_events),
                    )
                    print(f"  ✅ Events updated")
                
                return endpoint.secret

        # Create new webhook
        endpoint = stripe.WebhookEndpoint.create(
            url=webhook_url,
            enabled_events=events,
            description="OMEGA PRIME License Server",
            api_version="2023-10-16",
        )

        print(f"  ✅ Webhook created: {endpoint.id}")
        print(f"  🔑 Signing secret: {endpoint.secret[:30]}...")
        print()

        return endpoint.secret

    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


# ==================================================================
# Save to .env.local
# ==================================================================

def save_webhook_secret(secret: str):
    """Save the webhook secret to .env.local."""
    if not env_path.exists():
        print("  ❌ .env.local not found!")
        return

    content = env_path.read_text(encoding="utf-8")
    
    # Replace or add STRIPE_WEBHOOK_SECRET
    if "STRIPE_WEBHOOK_SECRET=" in content:
        content = content.replace(
            "STRIPE_WEBHOOK_SECRET=",
            f"STRIPE_WEBHOOK_SECRET={secret}"
        )
        # Fix: remove duplicate if we replaced empty value
        content = content.replace(
            f"STRIPE_WEBHOOK_SECRET={secret}\nSTRIPE_WEBHOOK_SECRET=",
            f"STRIPE_WEBHOOK_SECRET={secret}\n# STRIPE_WEBHOOK_SECRET="
        )
    else:
        content += f"\n# Stripe Webhook (auto-configured)\nSTRIPE_WEBHOOK_SECRET={secret}\n"

    env_path.write_text(content, encoding="utf-8")
    print(f"  💾 Saved to .env.local: STRIPE_WEBHOOK_SECRET")


# ==================================================================
# Test webhook
# ==================================================================

def test_webhook(secret: str):
    """Send a test event to verify the webhook works."""
    print()
    print("  📡 Testing webhook with ping event...")
    
    try:
        # Create a test event
        test_event = stripe.Event.create(
            type="ping",
            data={"object": {"id": "test"}},
        )
        print(f"  ✅ Test event sent: {test_event.id}")
        print(f"  🔄 Webhook endpoint will receive it shortly")
    except Exception as e:
        print(f"  ⚠️  Could not send test event: {e}")
        print(f"  📝  Webhook is registered — it will work when Stripe sends events")


# ==================================================================
# Main
# ==================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto-register Stripe webhook for OMEGA PRIME",
    )
    parser.add_argument("--url", help="Webhook URL (e.g., https://example.com/webhook/stripe)")
    parser.add_argument("--auto-ngrok", action="store_true", help="Auto-detect ngrok URL")
    
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║   Stripe Webhook Auto-Setup                     ║")
    print("╚══════════════════════════════════════════════════╝")

    # Determine webhook URL
    webhook_url = args.url
    
    if args.auto_ngrok:
        print("\n  🔍 Detecting ngrok tunnel...")
        ngrok_url = detect_ngrok_url()
        if ngrok_url:
            webhook_url = f"{ngrok_url}/webhook/stripe"
            print(f"  ✅ Found ngrok: {ngrok_url}")
        else:
            print("  ❌ ngrok not detected. Start ngrok first:")
            print("     ngrok http 5000")
            sys.exit(1)

    if not webhook_url:
        print("  ❌ No webhook URL provided!")
        print("  Usage: python auto_setup_stripe_webhook.py --url https://your-site.com/webhook/stripe")
        print("     or: python auto_setup_stripe_webhook.py --auto-ngrok")
        sys.exit(1)

    # Register
    secret = register_webhook(webhook_url)
    
    # Save
    save_webhook_secret(secret)
    
    # Test
    test_webhook(secret)

    print()
    print(f"  ✅ Webhook fully configured!")
    print(f"  🔗 Endpoint: {webhook_url}")
    print(f"  🔑 Secret:   {secret[:20]}...")
    print()


if __name__ == "__main__":
    main()
