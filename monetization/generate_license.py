#!/usr/bin/env python3
"""
==================================================================================
OMEGA PRIME — License Key Generator
==================================================================================
Generate HMAC-SHA256 signed license keys for OMEGA PRIME.

Compatible with SecurityValidator.GenerateLicense() / ValidateLicense() in C#.

Usage:
    python generate_license.py --customer "Acme Corp" --tier gold --days 365

    Or with environment variable:
    set OMEGA_SECRET_KEY=your-secret-key-here
    python generate_license.py --customer "Acme Corp" --tier gold --days 365

Tiers:
    🆓 free       — MIT license, community support, no warranty
    🥉 bronze     — ¥1,000/month  — Priority support
    🥈 silver     — ¥5,000/month  — Custom license + API access
    🥇 gold       — ¥20,000/month — Commercial license + white-label
    💎 platinum   — ¥50,000       — Enterprise + dedicated support
==================================================================================
"""

import os
import sys
import json
import base64
import hmac
import hashlib
import uuid
import argparse
from datetime import datetime, timedelta, timezone


# ==================================================================================
# CONFIGURATION
# ==================================================================================

TIER_PRICES = {
    "free": 0,
    "bronze": 1000,     # ¥/month
    "silver": 5000,     # ¥/month
    "gold": 20000,      # ¥/month
    "platinum": 50000,  # ¥ one-time
}

TIER_FEATURES = {
    "free": ["source_code", "community_support"],
    "bronze": ["source_code", "priority_support", "discord_role"],
    "silver": ["source_code", "priority_support", "license_key", "api_access"],
    "gold": ["source_code", "priority_support", "license_key", "api_access",
             "commercial_license", "white_label"],
    "platinum": ["source_code", "dedicated_support", "license_key", "api_access",
                 "commercial_license", "white_label", "custom_features", "sla"],
}


# ==================================================================================
# LICENSE GENERATION
# ==================================================================================

def get_secret_key():
    """Get OMEGA_SECRET_KEY from environment."""
    key = os.environ.get("OMEGA_SECRET_KEY")
    if not key:
        print("❌ ERROR: OMEGA_SECRET_KEY environment variable not set!")
        print("   set OMEGA_SECRET_KEY=your-secret-key-here")
        sys.exit(1)
    return key


def generate_license(
    customer_id: str,
    tier: str = "silver",
    expiry_days: int = 365,
    metadata: dict = None
) -> dict:
    """
    Generate an HMAC-SHA256 signed license key.
    
    Format: OMEGA-{base64_json}-{base64_hmac_truncated_16}
    Compatible with: OmegaPrime.Production.SecurityValidator
    
    Args:
        customer_id: Customer name, email, or company
        tier: License tier (free/bronze/silver/gold/platinum)
        expiry_days: Number of days until license expires
        metadata: Optional additional metadata
        
    Returns:
        dict with license_key, raw_payload, and metadata
    """
    secret_key = get_secret_key()
    tier = tier.lower()
    
    if tier not in TIER_PRICES:
        valid_tiers = ", ".join(TIER_PRICES.keys())
        raise ValueError(f"Invalid tier '{tier}'. Valid: {valid_tiers}")
    
    # Build payload
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=expiry_days)
    
    payload = {
        "customer_id": customer_id,
        "tier": tier,
        "issued_at": now.isoformat(),
        "expiry": expiry.isoformat(),
        "nonce": str(uuid.uuid4()),
    }
    
    if metadata:
        payload["metadata"] = metadata
    
    # Sign with HMAC-SHA256
    json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    json_b64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    
    signature = hmac.new(
        secret_key.encode("utf-8"),
        json_str.encode("utf-8"),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.b64encode(signature).decode("utf-8")[:16]
    
    license_key = f"OMEGA-{json_b64}-{sig_b64}"
    
    return {
        "license_key": license_key,
        "customer_id": customer_id,
        "tier": tier,
        "issued_at": payload["issued_at"],
        "expiry": payload["expiry"],
        "price": TIER_PRICES.get(tier, 0),
        "features": TIER_FEATURES.get(tier, []),
    }


def validate_license(license_key: str) -> dict:
    """
    Validate a license key (offline).
    Compatible with C# ValidateLicense().
    
    Returns dict with validation results.
    """
    secret_key = get_secret_key()
    
    try:
        parts = license_key.split("-")
        if len(parts) != 3 or parts[0] != "OMEGA":
            return {"valid": False, "error": "Invalid format"}
        
        json_bytes = base64.b64decode(parts[1])
        json_str = json_bytes.decode("utf-8")
        provided_sig = parts[2]
        
        # Verify signature
        signature = hmac.new(
            secret_key.encode("utf-8"),
            json_str.encode("utf-8"),
            hashlib.sha256
        ).digest()
        computed_sig = base64.b64encode(signature).decode("utf-8")[:16]
        
        if provided_sig != computed_sig:
            return {"valid": False, "error": "Invalid signature — license tampered"}
        
        # Parse payload
        payload = json.loads(json_str)
        customer_id = payload.get("customer_id")
        tier = payload.get("tier", "free")
        expiry_str = payload.get("expiry")
        
        # Check expiry
        expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        
        if expiry < now:
            expired_days = (now - expiry).days
            return {
                "valid": False,
                "error": f"License expired {expired_days} days ago",
                "customer_id": customer_id,
                "tier": tier,
                "expiry": expiry_str,
                "expired_days": expired_days,
            }
        
        remaining_days = (expiry - now).days
        
        return {
            "valid": True,
            "customer_id": customer_id,
            "tier": tier,
            "expiry": expiry_str,
            "remaining_days": remaining_days,
            "features": TIER_FEATURES.get(tier, []),
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}


# ==================================================================================
# CLI INTERFACE
# ==================================================================================

def print_license_info(result: dict):
    """Pretty-print license information."""
    if result.get("valid"):
        print("✅" + "=" * 60)
        print("✅  LICENSE VALID")
        print("✅" + "=" * 60)
        print(f"  Customer : {result['customer_id']}")
        print(f"  Tier     : {result['tier'].upper()}")
        print(f"  Expiry   : {result['expiry']}")
        print(f"  Remaining: {result['remaining_days']} days")
        print(f"  Features : {', '.join(result['features'])}")
        print("=" * 63)
    elif "license_key" in result:
        # Generation result
        print("🔑" + "=" * 60)
        print("🔑  LICENSE KEY GENERATED")
        print("🔑" + "=" * 60)
        print(f"  Customer : {result['customer_id']}")
        print(f"  Tier     : {result['tier'].upper()}")
        print(f"  Price    : ¥{result['price']:,}")
        print(f"  Issued   : {result['issued_at']}")
        print(f"  Expiry   : {result['expiry']}")
        print(f"  Features : {', '.join(result['features'])}")
        print()
        print("  License Key:")
        print(f"  {result['license_key']}")
        print()
        print(f"  Save to file: omega_{result['customer_id'].replace(' ', '_').lower()}.lic")
        print("=" * 63)
    else:
        print("❌" + "=" * 60)
        print("❌  LICENSE INVALID")
        print("❌" + "=" * 60)
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print("=" * 63)


def main():
    parser = argparse.ArgumentParser(
        description="🔑 OMEGA PRIME License Key Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a 1-year Silver license
  python generate_license.py -c "Acme Corp" -t silver -d 365
  
  # Generate and save to file
  python generate_license.py -c "user@email.com" -t gold -d 730 -o license.lic
  
  # Validate an existing license
  python generate_license.py -v "OMEGA-<base64>-<sig>"
  
  # Validate from file
  python generate_license.py -f license.lic
        """
    )
    
    # Generate mode
    parser.add_argument("-c", "--customer", help="Customer ID (name, email, company)")
    parser.add_argument("-t", "--tier", choices=TIER_PRICES.keys(), default="silver",
                        help="License tier (default: silver)")
    parser.add_argument("-d", "--days", type=int, default=365,
                        help="Expiry in days (default: 365)")
    parser.add_argument("-m", "--metadata", help="Additional metadata as JSON string")
    parser.add_argument("-o", "--output", help="Save license key to file")
    
    # Validate mode
    parser.add_argument("-v", "--validate", help="License key to validate")
    parser.add_argument("-f", "--file", help="License file to validate")
    
    args = parser.parse_args()
    
    # --- VALIDATE MODE ---
    if args.validate or args.file:
        license_key = args.validate
        if args.file:
            with open(args.file, "r") as f:
                license_key = f.read().strip()
        
        result = validate_license(license_key)
        print_license_info(result)
        sys.exit(0 if result.get("valid") else 1)
    
    # --- GENERATE MODE ---
    if not args.customer:
        print("❌ ERROR: --customer is required for generation mode")
        print("   Example: python generate_license.py -c 'Acme Corp' -t gold")
        sys.exit(1)
    
    metadata = None
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("❌ ERROR: --metadata must be valid JSON")
            sys.exit(1)
    
    result = generate_license(
        customer_id=args.customer,
        tier=args.tier,
        expiry_days=args.days,
        metadata=metadata,
    )
    
    print_license_info(result)
    
    # Save to file
    if args.output:
        with open(args.output, "w") as f:
            f.write(result["license_key"] + "\n")
        print(f"💾 Saved to: {args.output}")
    
    # Generate filename if not specified
    elif args.customer:
        safe_name = args.customer.replace(" ", "_").lower()
        filename = f"omega_{safe_name}.lic"
        with open(filename, "w") as f:
            f.write(result["license_key"] + "\n")
        print(f"💾 Auto-saved to: {filename}")


if __name__ == "__main__":
    main()
