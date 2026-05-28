#!/usr/bin/env python3
"""
=================================================================
OMEGA PRIME - Stripe Products & Prices Setup
=================================================================
Creates products and pricing tiers in Stripe automatically.

Usage:
    python scripts/setup_stripe_products.py

Environment:
    STRIPE_API_KEY - Stripe secret key (required)
    
This script will:
    1. Create Products (Bronze, Silver, Gold, Platinum)
    2. Create Prices (monthly + yearly for each)
    3. Update .env.local with real Price IDs
    4. Print summary
=================================================================
"""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env.local
env_path = Path(".env.local")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

try:
    import stripe
except ImportError:
    print("❌ Stripe not installed! Run: pip install stripe")
    sys.exit(1)

# ==================================================================
# Configuration
# ==================================================================

PRODUCTS = [
    {
        "name": "OMEGA PRIME - Bronze",
        "description": "Support tier with priority support and Discord role",
        "tier": "bronze",
        "emoji": "🥉",
        "prices": [
            {"nickname": "Bronze Monthly", "interval": "month", "amount": 1000},
            {"nickname": "Bronze Yearly", "interval": "year", "amount": 10000},
        ],
    },
    {
        "name": "OMEGA PRIME - Silver",
        "description": "License Key + API Access + Commercial Use",
        "tier": "silver",
        "emoji": "🥈",
        "prices": [
            {"nickname": "Silver Monthly", "interval": "month", "amount": 5000},
            {"nickname": "Silver Yearly", "interval": "year", "amount": 50000},
        ],
    },
    {
        "name": "OMEGA PRIME - Gold",
        "description": "White-Label + SLA + Custom Feature Development",
        "tier": "gold",
        "emoji": "🥇",
        "prices": [
            {"nickname": "Gold Monthly", "interval": "month", "amount": 20000},
            {"nickname": "Gold Yearly", "interval": "year", "amount": 200000},
        ],
    },
    {
        "name": "OMEGA PRIME - Platinum",
        "description": "Full IP Transfer + Dedicated Support + On-Premise",
        "tier": "platinum",
        "emoji": "💎",
        "prices": [
            {"nickname": "Platinum One-Time", "interval": None, "amount": 50000},
        ],
    },
]


def create_stripe_products():
    """Create products and prices in Stripe."""
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        print("❌ STRIPE_API_KEY not set!")
        print("   Set it in .env.local or as environment variable")
        sys.exit(1)

    stripe.api_key = api_key

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║   Stripe Products & Prices Setup                ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"🔑 Using API Key: {api_key[:12]}...{api_key[-4:]}")
    print()

    results = {}

    for product_def in PRODUCTS:
        print(f"{'─' * 55}")
        print(f"  {product_def['emoji']}  Creating: {product_def['name']}")
        print(f"{'─' * 55}")

        # Create product
        try:
            product = stripe.Product.create(
                name=product_def["name"],
                description=product_def["description"],
                metadata={"tier": product_def["tier"]},
            )
            print(f"   ✅ Product: {product.id}")
        except Exception as e:
            print(f"   ❌ Product error: {e}")
            continue

        # Create prices
        price_ids = {}
        for price_def in product_def["prices"]:
            params = {
                "product": product.id,
                "currency": "jpy",  # Using JPY (¥) as primary
                "unit_amount": price_def["amount"],
                "nickname": price_def["nickname"],
            }

            if price_def["interval"]:
                params["recurring"] = {"interval": price_def["interval"]}
                interval_key = price_def["interval"]
            else:
                interval_key = "once"

            try:
                price = stripe.Price.create(**params)
                price_ids[interval_key] = price.id
                interval_label = (
                    f"({price_def['interval']}ly)"
                    if price_def["interval"]
                    else "(one-time)"
                )
                print(
                    f"   ✅ Price {interval_label}: {price.id}"
                    f"  ¥{price_def['amount']:,}"
                )
            except Exception as e:
                print(f"   ❌ Price error: {e}")

        results[product_def["tier"]] = price_ids
        print()

    print(f"{'=' * 55}")
    print(f"  📋  SUMMARY - Add these to .env.local:")
    print(f"{'=' * 55}")
    print()

    env_updates = []
    for tier, prices in results.items():
        for interval, price_id in prices.items():
            if interval == "month":
                key = f"STRIPE_{tier.upper()}_MONTHLY"
            elif interval == "year":
                key = f"STRIPE_{tier.upper()}_YEARLY"
            else:
                key = f"STRIPE_{tier.upper()}"

            env_updates.append((key, price_id))
            print(f"  {key}={price_id}")

    print()
    print(f"{'=' * 55}")

    # Update .env.local
    update_env_file(env_updates)

    return results


def update_env_file(updates: list):
    """Update .env.local with real Price IDs."""
    env_path = Path(".env.local")
    if not env_path.exists():
        print("❌ .env.local not found!")
        return

    content = env_path.read_text(encoding="utf-8")
    updated = False

    for key, value in updates:
        old_line = f"{key}=price_{key.split('_', 1)[1].lower()}"
        new_line = f"{key}={value}"

        # Try exact match first
        if old_line in content:
            content = content.replace(old_line, new_line)
            updated = True
            print(f"   🔄 Updated: {key}={value[:20]}...")

    if updated:
        env_path.write_text(content, encoding="utf-8")
        print(f"\n   ✅ .env.local updated with real Price IDs!")
    else:
        print(f"\n   ⚠️  No placeholder values found to replace.")
        print(f"   📝  Please manually add the Price IDs above to .env.local")

    print()


if __name__ == "__main__":
    create_stripe_products()
