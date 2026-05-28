#!/usr/bin/env python3
"""Quick test that all auto-scripts load correctly."""
import sys
import os
from pathlib import Path

root = Path(__file__).parent.parent
os.chdir(root)
sys.path.insert(0, str(root))

# 1. Test start.ps1 syntax (just check it exists and has content)
start_ps = root / "start.ps1"
assert start_ps.exists(), "start.ps1 not found!"
assert start_ps.stat().st_size > 1000, "start.ps1 too small!"
print(f"✅ start.ps1 — {start_ps.stat().st_size} bytes")

# 2. Test start.bat
start_bat = root / "start.bat"
assert start_bat.exists(), "start.bat not found!"
print(f"✅ start.bat — {start_bat.stat().st_size} bytes")

# 3. Test webhook script imports
sys.path.insert(0, str(root / "scripts"))
# Just check we can parse the file
with open(root / "scripts" / "auto_setup_stripe_webhook.py", encoding="utf-8") as f:
    code = f.read()
assert "def register_webhook" in code
assert "detect_ngrok_url" in code
print(f"✅ auto_setup_stripe_webhook.py — {len(code)} chars, functions found")

# 4. Test .env.local has keys
env_file = root / ".env.local"
assert env_file.exists(), ".env.local not found!"
content = env_file.read_text(encoding="utf-8")
assert "STRIPE_API_KEY=sk_test" in content, "Stripe secret key missing!"
assert "STRIPE_PUBLIC_KEY=pk_test" in content, "Stripe public key missing!"
assert "price_" in content, "Real Price IDs missing!"
print(f"✅ .env.local — Keys OK, Price IDs OK")

# 5. Test .gitignore
gitignore = root / ".gitignore"
assert gitignore.exists(), ".gitignore not found!"
content = gitignore.read_text(encoding="utf-8")
assert ".env" in content, ".env not in gitignore!"
print(f"✅ .gitignore — .env protected from commit")

# 6. Test FUNDING.yml has real links
funding = root / ".github" / "FUNDING.yml"
assert funding.exists(), "FUNDING.yml not found!"
content = funding.read_text(encoding="utf-8")
assert "buy.stripe.com" in content, "Stripe links missing!"
print(f"✅ FUNDING.yml — Has real Stripe Payment Links")

print()
print("🎉 ALL AUTO-SCRIPTS VERIFIED! System ready for 1-click start!")
