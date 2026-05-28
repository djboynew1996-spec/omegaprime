# 🤖 OMEGA PRIME — Auto Money Setup Guide
# ระบบทำเงินอัตโนมัติ 100% ไม่ต้องรันเซิร์ฟเวอร์!

---

## 🎯 ระบบนี้ทำงานยังไง

```
ลูกค้าคลิกจ่าย → Stripe → Pipedream (ฟรี) → สร้าง License → ส่งถึงเมล
                        ↓
           คุณได้เงินเข้ากระเป๋าอัตโนมัติ
```

**คุณไม่ต้องทำอะไรเลย!** ระบบทำงานเอง 24/7

---

## ⚡ Setup ใช้เวลา 10 นาที

### ขั้นตอนที่ 1: สมัคร Pipedream (ฟรี)

| ทำ | ลิงก์ |
|----|-------|
| ไปที่ | https://pipedream.com |
| สมัคร | ใช้ Google หรือ GitHub ก็ได้ |
| ไม่ต้องใส่บัตร | ฟรีตลอด ไม่ต้องใช้บัตรเครดิต |

### ขั้นตอนที่ 2: สร้าง Workflow

```
1. คลิก "New Workflow"
2. เลือก HTTP → Webhook → "Instant Response"
3. ก็อป URL ที่ได้ → จะใช้ในขั้นตอนถัดไป
4. คลิก + ต่อด้วย "Run Python"
5. ก็อปโค้ดนี้ไปวาง:
```

**ก็อปโค้ดนี้ไปวางใน Pipedream:**

```python
import os, json, hmac, hashlib, base64, uuid
from datetime import datetime, timedelta, timezone

OMEGA_SECRET_KEY = os.environ["OMEGA_SECRET_KEY"]
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

PRICE_TIERS = {
    "price_1Tbs7U0TLJQM7Q1AYMR6Dc2h": ("bronze", 30),
    "price_1Tbs7U0TLJQM7Q1AutYfI0wz": ("bronze", 365),
    "price_1Tbs7V0TLJQM7Q1AkArimQYh": ("silver", 30),
    "price_1Tbs7V0TLJQM7Q1AgU8mmkvi": ("silver", 365),
    "price_1Tbs7W0TLJQM7Q1AeSWRXGUH": ("gold", 30),
    "price_1Tbs7X0TLJQM7Q1AMIapGGXB": ("gold", 365),
    "price_1Tbs7X0TLJQM7Q1AYaywJO9v": ("platinum", 3650),
}

def generate_license(customer_id, tier, days):
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=days)
    payload = {
        "customer_id": customer_id, "tier": tier,
        "issued_at": now.isoformat(), "expiry": expiry.isoformat(),
        "nonce": uuid.uuid4().hex[:16],
    }
    json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    sig = hmac.new(OMEGA_SECRET_KEY.encode(), json_str.encode(), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig).decode()[:16]
    json_b64 = base64.b64encode(json_str.encode()).decode()
    return f"OMEGA-{json_b64}-{sig_b64}", payload

def handler(event):
    if event.get("type") != "checkout.session.completed":
        return {"status": "ignored"}
    
    session = event["data"]["object"]
    email = session.get("customer_details", {}).get("email", "")
    
    # Get price ID from line items
    items = session.get("line_items", {}).get("data", [])
    price_id = items[0]["price"]["id"] if items else ""
    tier, days = PRICE_TIERS.get(price_id, ("bronze", 30))
    
    license_key, payload = generate_license(email, tier, days)
    print(f"✅ {email} bought {tier}")
    print(f"🔑 License: {license_key}")
    
    return {"status": "success", "license_key": license_key,
            "customer": email, "tier": tier, "expiry": payload["expiry"]}
```

### ขั้นตอนที่ 3: ตั้งค่า Environment Variables ใน Pipedream

| Variable | ค่า |
|----------|-----|
| `OMEGA_SECRET_KEY` | `MyOmegaSuperSecretKey2026!` |
| `STRIPE_API_KEY` | `sk_test_YOUR_STRIPE_SECRET_KEY` |

### ขั้นตอนที่ 4: ตั้งค่า Stripe Webhook

```
1. ไปที่ Stripe Dashboard → https://dashboard.stripe.com/webhooks
2. คลิก "Add endpoint"
3. ใส่ URL จาก Pipedream (ขั้นตอนที่ 2)
4. เลือก event: checkout.session.completed
5. คลิก "Add endpoint"
6. ก็อป "Signing secret" (whsec_...) → เก็บไว้ใช้
```

### ขั้นตอนที่ 5: (Optional) ส่ง Email Auto

เพิ่ม Action "Send Email" ต่อจาก Python step ใน Pipedream:
- **To:** `{{steps.python.$return_value.customer}}`
- **Subject:** 🎉 Your OMEGA PRIME License Key
- **Body:**
```
Thank you for purchasing OMEGA PRIME!

Your License Key:
{{steps.python.$return_value.license_key}}

Tier: {{steps.python.$return_value.tier}}
Expires: {{steps.python.$return_value.expiry}}

How to use:
set OMEGA_LICENSE_KEY={{steps.python.$return_value.license_key}}
dotnet run --project src/OmegaPrime.csproj

Support: chaiyaphop@omegaprime.dev
```

---

## ✅ เสร็จ! ระบบ Auto ทำงานแล้ว

```
💰 ลูกค้าจ่าย → 🔑 License สร้างอัตโนมัติ → 📧 ส่งถึงเมล
                         ↓
             คุณนอนหลับได้ — เงินเข้า Stripe Auto!
```

**ทดสอบ:** ซื้อจริงผ่าน Payment Link:
- 🥉 https://buy.stripe.com/test_dRmcMXaswbwF30oaG93Ru00
- 🥈 https://buy.stripe.com/test_7sYaEP0RWcAJcAY01v3Ru02
- 🥇 https://buy.stripe.com/test_cNi14fgQUfMVbwU4hL3Ru04
- 💎 https://buy.stripe.com/test_aFaeV59osbwF7gEg0t3Ru06

---

## 💰 รายได้ที่คาดหวัง (แบบ Auto)

| ขายได้ | รายได้ | เกิดขึ้น |
|--------|-------|---------|
| Silver 1 ราย/เดือน | ¥5,000/เดือน | Auto |
| Gold 1 ราย/เดือน | ¥20,000/เดือน | Auto |
| Platinum 1 ราย | ¥50,000 | Auto |
| รวม | **¥75,000+/เดือน** (~37,500฿) | **คุณไม่ต้องทำอะไร!** |

---

> 🚀 **เริ่มตอนนี้:** สมัคร Pipedream → ก็อปโค้ด → ตั้ง Webhook → เสร็จ!
> ใช้เวลาแค่ 10 นาที ระบบทำงานเองตลอดไป!
