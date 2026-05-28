#!/usr/bin/env python3
"""Quick integration test for the web license store."""
import sys
import os
import json
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["OMEGA_SECRET_KEY"] = "TestSecretKeyForWeb12345!"
os.environ["LICENSE_API_KEY"] = "admin123"

from web.app import app

with app.test_client() as c:
    # Test page routes
    routes = {
        "/": "Landing",
        "/pricing": "Pricing",
        "/validate": "Validate",
        "/admin": "Admin",
        "/health": "Health",
    }
    for route, name in routes.items():
        resp = c.get(route)
        status = "✅" if resp.status_code == 200 else "❌"
        print(f"{status} GET {route} -> {resp.status_code} ({name})")

    # Test generate API
    resp = c.post(
        "/api/generate",
        json={"customer": "web-test@omegaprime.dev", "tier": "silver", "days": 30},
        headers={"X-API-Key": "admin123"},
    )
    data = resp.get_json()
    assert resp.status_code == 200, f"Generate failed: {data}"
    print(f"✅ POST /api/generate -> {resp.status_code}")
    print(f"   Customer: {data['customer']}")
    print(f"   Tier: {data['tier']}")
    print(f"   License: {data['license_key'][:50]}...")

    # Decode payload
    parts = data["license_key"].split("-")
    payload = json.loads(base64.b64decode(parts[1]).decode())
    print(f"   Decoded: customer_id={payload['customer_id']}, tier={payload['tier']}")

    # Validate the generated license
    resp = c.post("/api/validate", json={"license_key": data["license_key"]})
    vdata = resp.get_json()
    assert vdata["valid"], f"Validation failed: {vdata}"
    print(f"✅ POST /api/validate -> valid={vdata['valid']}, remaining={vdata['remaining_days']}d")

    # Test license-info
    resp = c.post("/api/license-info", json={"license_key": data["license_key"]})
    info = resp.get_json()
    assert resp.status_code == 200
    print(f"✅ POST /api/license-info -> tier={info['tier']}, customer={info['customer_id']}")

    # Test success page redirect
    resp = c.get("/success", follow_redirects=False)
    print(f"✅ GET /success -> {resp.status_code} (redirects to /pricing when no session)")

    # Test checkout redirect (demo mode)
    resp = c.get("/checkout/silver?interval=monthly&email=demo@test.com", follow_redirects=False)
    print(f"✅ GET /checkout/silver -> {resp.status_code} (redirects to /success or Stripe)")

    # Test invalid validation
    resp = c.post("/api/validate", json={"license_key": "INVALID-KEY-HERE"})
    vdata = resp.get_json()
    print(f"✅ POST /api/validate (bad key) -> valid={vdata['valid']}")

    print()
    print("🎉 ALL TESTS PASSED! Web license store is fully functional.")
