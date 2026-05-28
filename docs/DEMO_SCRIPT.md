# 🎬 OMEGA PRIME — Demo Script for Client Calls

> ใช้เวลา 10-15 นาที โชว์ให้ลูกค้าเห็นของจริง

---

## 📹 Part 1: Setup (1 min)

### สิ่งที่ต้องเตรียมก่อน Demo
```bash
# Terminal 1: รัน License Server
cd web
python app.py

# Terminal 2: รัน OMEGA PRIME
dotnet run --project src/OmegaPrime.csproj
```

### เปิด Browser Tab:
1. http://localhost:8080 — License Store Web UI
2. http://localhost:5000 — Health check

---

## 🎯 Part 2: Opening (2 min)

**คุณ:** "สวัสดีครับ [ชื่อลูกค้า] ขอบคุณที่สละเวลามาดู Demo วันนี้"

"ผมอยากโชว์ให้เห็นว่า OMEGA PRIME คืออะไร ใน 10 นาที"

"เราจะดู 3 อย่าง:
1. **ระบบทำงานยังไง** — เห็นของจริง
2. **License / ซื้อขายยังไง** — เอาไปใช้เชิงพาณิชย์
3. **Deploy ยังไง** — เอาขึ้น Production ได้เลย"

---

## ⚡ Part 3: Live Demo (5 min)

### Step 1: โชว์ System Boot
```bash
# พิมพ์ใน terminal
dotnet run --project src/OmegaPrime.csproj
```

**พูด:** "สังเกตว่ามี License Validation — ถ้าไม่มี License ก็ยังใช้ได้ แต่จะเตือนว่าเป็น Free tier"

### Step 2: ทดสอบ Query
```
Ω> status
Ω> health
```

**พูด:** "ระบบพร้อมทำงานทันที มี monitoring และ health check"

### Step 3: โชว์ AI จริง
```
Ω> what is the weather like today?
Ω> analyze the current situation
```

**พูด:** "เห็นไหมครับ — ระบบวิเคราะห์และสังเคราะห์ผลลัพธ์ออกมาให้เลย"

### Step 4: โชว์ License Store
(เปิด browser ที่ localhost:8080)

**พูด:** "นี่คือ Web Store สำหรับขาย License — ลูกค้าสามารถซื้อได้เองอัตโนมัติ"

"เมื่อจ่ายเงินผ่าน Stripe — License Key ถูกสร้างและส่งให้ทันที"

---

## 💰 Part 4: Pricing Talk (3 min)

### สำหรับลูกค้าที่ต้องการใช้เอง:
```
🆓 Free — ใช้ก่อนได้เลย ไม่เสียตัง
🥈 Silver ¥5,000/เดือน — ได้ License Key, ใช้เชิงพาณิชย์
🥇 Gold ¥20,000/เดือน — ขายต่อได้, White-label
```

### สำหรับ Agency ที่อยากขายต่อ:
**พูด:** "ข้อเสนอพิเศษสำหรับคุณ:
- คุณได้ White-label license — เปลี่ยนชื่อเป็นแบรนด์คุณได้
- คุณสามารถขายต่อให้ลูกค้าคุณในราคาที่คุณตั้งเอง
- ผมดูแล technical support ให้
- คุณเก็บกำไร 100% — จ่ายแค่ license รายเดือน"

**ตัวอย่าง:** 
"Agency จ่าย ¥20,000/เดือน (≈10,000฿)  
ขายต่อให้ลูกค้า ¥50,000-100,000/เดือน (≈25,000-50,000฿)  
**กำไร 150-400%**"

---

## ✅ Part 5: Closing (2 min)

**ถาม:** "คุณคิดว่า OMEGA PRIME เหมาะกับโปรเจกต์ของคุณไหมครับ?"

**รับมือข้อกังวล:**

| ข้อกังวล | คำตอบ |
|---------|--------|
| "แพงไป" | "เริ่มที่ Free tier ก่อนครับ พอเห็นว่ามันใช้ได้จริง ค่อย upgrade" |
| "กลัว不安全" | "ระบบ security-first: non-root container, HMAC license, rate limiting — source code เปิดให้ตรวจสอบได้" |
| "ต้องการ custom feature" | "Gold tier รวม custom dev 1 เรื่อง/เดือน Platinum มี dedicated support" |
| "ต้องดู source code ก่อน" | "ได้เลยครับ! GitHub public ทั้งหมด: github.com/chaiyaphop/omegaprime" |

**ปิดการขาย:**
- "พร้อมเริ่ม? ผมขอเสนอ Silver tier ให้คุณลองก่อน 1 เดือน — ถ้าไม่พอใจ บอกภายใน 7 วันได้เงินคืน"
- "หรือถ้าคุณเป็น Agency — Gold tier คุ้มที่สุด เพราะเอาไปขายต่อได้เลย"

---

## 📋 Demo Checklist (ก่อนโทร)

- [ ] รัน License Server (`python web/app.py`)
- [ ] รัน OMEGA PRIME (`dotnet run`)
- [ ] เปิด Web Store (localhost:8080)
- [ ] เปิด GitHub repo ไว้
- [ ] เปิด Pricing page
- [ ] เตรียมตัวอย่าง License Key สำหรับโชว์
- [ ] ทดสอบ Stripe Payment Link ว่ายังใช้ได้
- [ ] ปิดเสียงแจ้งเตือนในเครื่อง
- [ ] เตรียมน้ำไว้ข้างๆ

---

> 💡 **Pro Tip:** ถ้าลูกค้าเป็นคนไทย — ใช้ภาษาไทยคุย business ก่อน
> แล้วค่อยสลับโชว์ technical เป็นภาษาอังกฤษเพื่อความ professional
