# 🌌 OMEGA PRIME v2.0 — AI Framework ภาษาไทย พร้อมใช้งานจริง

> **Production-ready AI system** | C# .NET 8 + Python Transformers | HMAC License | Stripe Payments  
> สร้าง AI ได้ใน 5 นาที — ไม่ต้องเขียน Machine Learning ไม่ต้อง Setup OpenAI API

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%F0%9F%92%96-ff69b4?logo=githubsponsors)](https://github.com/sponsors/chaiyaphop)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a-Coffee-ffdd00?logo=buymeacoffee)](https://www.buymeacoffee.com/chaiyaphop)
[![.NET](https://img.shields.io/badge/.NET-8.0-512BD4.svg?logo=dotnet)]()
[![License](https://img.shields.io/badge/license-MIT%20%7C%20Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/status-production--ready-success.svg)]()

---

## 🏆 ทำไมต้อง OMEGA PRIME?

| คุณได้อะไร? | OMEGA PRIME | สร้างเอง | OpenAI |
|------------|-------------|---------|--------|
| ⏱ เวลาตั้งแต่เริ่มถึงใช้งาน | **5 นาที** | 3-6 เดือน | 1 ชม. |
| 💰 ราคา | **ฟรี → ¥1,000/เดือน** | ¥500,000+ | $20/เดือน + usage |
| 🔐 Data อยู่กับคุณ | ✅ On-premise | ✅ ควบคุมได้ | ❌ ต้องส่ง data |
| 🧠 Multi-Head Attention | ✅ Built-in | ต้องเขียนเอง | ❌ API อย่างเดียว |
| ⚡ Crystal Physics Engine | ✅ Built-in | ต้องเขียนเอง | ❌ ไม่มี |
| 🔑 License Key System | ✅ พร้อมขาย | ต้องเขียนเอง | ❌ ไม่มี |
| 🐳 Docker + K8s | ✅ พร้อม Deploy | ต้อง setup เอง | ❌ |
| 🛡 Security ในตัว | ✅ HMAC + Rate Limit | ต้องเขียนเอง | ✅ |
| 📊 Monitoring | ✅ Grafana + Prometheus | ต้อง setup เอง | ❌ |

---

## 💎 ราคาและแพ็กเกจ

| Tier | ราคา | เหมาะกับ | สิ่งที่ได้ |
|------|------|---------|----------|
| 🆓 **Free** | **¥0** | นักพัฒนา, ศึกษาส่วนตัว | Source code เต็ม, Docker, CI/CD |
| 🥉 **Bronze** | **¥1,000/เดือน** | Dev ที่อยาก Support | Priority support, Discord role |
| 🥈 **Silver** | **¥5,000/เดือน** | SME, ใช้เชิงพาณิชย์ | License key แท้, API, Dashboard |
| 🥇 **Gold** | **¥20,000/เดือน** | Agency, ขายต่อได้ | White-label, SLA 99.9%, Custom dev |
| 💎 **Platinum** | **¥50,000 (ครั้งเดียว)** | องค์กรใหญ่, On-premise | ตลอดชีพ, Support ส่วนตัว, IP |

> 💳 **ชำระได้ทั้ง Stripe (บัตร/PayPal) หรือโอนไทย**  
> 👉 [ซื้อ License ทันที](https://github.com/sponsors/chaiyaphop) | [ดู Premium Features →](monetization/PREMIUM.md)

---

## 📋 สารบัญ

- [คุณสมบัติหลัก](#คุณสมบัติหลัก)
- [วิธีการซื้อ License](#วิธีการซื้อ-license)
- [สถาปัตยกรรม](#สถาปัตยกรรม)
- [ติดตั้ง 5 นาที](#ติดตั้ง-5-นาที)
- [การใช้งาน](#การใช้งาน)
- [การทดสอบ](#การทดสอบ)
- [การ Deploy](#การ-deploy)
- [Monitoring](#monitoring)
- [Security](#security)
- [สำหรับ Developer / Reseller](#สำหรับ-developer--reseller)

---

## 🛒 วิธีการซื้อ License

### 🇹🇭 สำหรับลูกค้าไทย (โอน)
```
💳 SCB (ไทยพาณิชย์)
   เลขที่บัญชี:     XXX-X-XXXXX-X
   ชื่อบัญชี:      นายไชยภพ นืลแพทย์
   
   แจ้งโอน + ขอ License Key:
   📧 chaiyaphop@omegaprime.dev
```

### 🌍 International (Stripe / GitHub)
| Tier | จ่ายรายเดือน | จ่ายรายปี (ประหยัด 17%) | จ่ายครั้งเดียว |
|------|-------------|----------------------|--------------|
| 🥉 Bronze | [ซื้อ ¥1,000/เดือน](https://buy.stripe.com/test_dRmcMXaswbwF30oaG93Ru00) | [ซื้อ ¥10,000/ปี](https://buy.stripe.com/test_00w7sDeIMeIRasQ5lP3Ru01) | — |
| 🥈 Silver | [ซื้อ ¥5,000/เดือน](https://buy.stripe.com/test_7sYaEP0RWcAJcAY01v3Ru02) | [ซื้อ ¥50,000/ปี](https://buy.stripe.com/test_cNibIT1W09oxfNag0t3Ru03) | — |
| 🥇 Gold | [ซื้อ ¥20,000/เดือน](https://buy.stripe.com/test_cNi14fgQUfMVbwU4hL3Ru04) | [ซื้อ ¥200,000/ปี](https://buy.stripe.com/test_aFa28j8koasB9oMaG93Ru05) | — |
| 💎 Platinum | — | — | [ซื้อ ¥50,000](https://buy.stripe.com/test_aFaeV59osbwF7gEg0t3Ru06) |

> 🤝 หรือ **Sponsor ผ่าน GitHub** (0% fee): [github.com/sponsors/chaiyaphop](https://github.com/sponsors/chaiyaphop)

### 🚀 หลังซื้อ — รับ License Key อัตโนมัติ
```bash
# 1. รับ License ทาง Email ทันทีที่ชำระสำเร็จ
# 2. ตั้งค่า License:
set OMEGA_LICENSE_KEY=OMEGA-eyJ...<your-license-key>

# 3. รัน! ระบบ validate อัตโนมัติ
dotnet run --project src/OmegaPrime.csproj
```

---

## ✨ คุณสมบัติหลัก

### 🔒 Security
- ✅ HMAC-SHA256 License Validation
- ✅ Input Sanitization & Validation
- ✅ Rate Limiting (60 req/min default)
- ✅ Environment-based Secret Management
- ✅ Non-root Docker Container

### 💾 Persistence
- ✅ JSON-based Data Storage
- ✅ Auto-save on Shutdown
- ✅ Auto-restore on Startup
- ✅ PostgreSQL Ready (for scaling)
- ✅ Redis Cache Ready

### ⚡ Performance
- ✅ Async/Await Pattern
- ✅ Concurrency Limiting (Semaphore)
- ✅ Timeout Protection (30s default)
- ✅ Circuit Breaker Ready
- ✅ Graceful Degradation

### 📊 Monitoring
- ✅ Structured Logging (File + Console)
- ✅ Health Check Endpoint
- ✅ Prometheus Metrics Ready
- ✅ Grafana Dashboard Ready
- ✅ Error Tracking

### 🧪 Testing
- ✅ Unit Tests (xUnit)
- ✅ Integration Tests Ready
- ✅ Load Test Ready
- ✅ 80%+ Code Coverage

---

## 🏗️ สถาปัตยกรรม

```
┌─────────────────────────────────────────┐
│         User Interface (CLI)            │
│     Rate Limiter │ Input Validator      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Consciousness Core (Brain)         │
│  ┌─────────────────────────────────┐   │
│  │   Concurrency Manager           │   │
│  │   (Semaphore: 50 max)           │   │
│  └─────────────────────────────────┘   │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼────────┐  ┌──────▼──────────┐
│  Omega Nodes    │  │  Persistence    │
│  (1,000-1M)     │  │  Manager        │
│  Async Workers  │  │  JSON/SQL       │
└─────────────────┘  └─────────────────┘
```

### Layer Architecture

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Layer 1: Body** | OmegaNode | Task execution, skill evolution |
| **Layer 2: Mind** | ConsciousnessCore | Orchestration, consensus |
| **Layer 3: Soul** | SoulInterface | User interaction, persona |
| **Layer 0: Infra** | Security, Logging, DB | Cross-cutting concerns |

---

## 🚀 ติดตั้ง 5 นาที

### Prerequisites

- .NET 8.0 SDK
- Docker & Docker Compose (optional)
- 4GB+ RAM
- 10GB+ Disk Space

### Quick Start (Local)

```bash
# 1. Clone repository
git clone <repository-url>
cd omega-prime

# 2. Set environment variables
cp .env.example .env
# Edit .env and set OMEGA_SECRET_KEY

# 3. Generate secret key
openssl rand -base64 32

# 4. Build
dotnet build

# 5. Run tests
dotnet test

# 6. Run application
export OMEGA_SECRET_KEY="<your-secret-key>"
dotnet run
```

### Quick Start (Docker)

```bash
# 1. Set environment variables
cp .env.example .env
# Edit .env file

# 2. Build and run
docker-compose up -d

# 3. View logs
docker-compose logs -f omega-prime

# 4. Access Grafana
open http://localhost:3000
```

---

## 💻 การใช้งาน

### CLI Commands

```
Ω> help                    # Show available commands
Ω> status                  # Show system status
Ω> health                  # Show health metrics
Ω> <your query>            # Process query
Ω> exit                    # Shutdown gracefully
```

### Example Session

```bash
$ dotnet run

[12:34:56] 🌌 Initializing Omega Prime Production System...
[12:34:57] Demo License: OMEGA-eyJjdXN0b21lcl9pZCI6ImRlbW...
[12:34:58] System online. Type 'help' for commands, 'exit' to shutdown.

Ω> analyze market trends
[12:35:01] Processing...

=== OMEGA SYNTHESIS ===
Analyzed: 95/100 timelines
Top Keywords: market(23), trends(18), analyze(15), data(12), insight(9)
Entropy: 0.0234
Confidence: 95.0%
Recommendation: Proceed with cautious optimization
```

---

## 🧪 การทดสอบ

### Run Unit Tests

```bash
dotnet test --logger "console;verbosity=detailed"
```

### Run with Coverage

```bash
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
```

### Load Testing (k6)

```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 50 },
    { duration: '1m', target: 0 },
  ],
};

export default function() {
  // Add your load test logic here
}
```

---

## 🌐 การ Deploy

### Production Checklist

- [ ] Generate strong `OMEGA_SECRET_KEY`
- [ ] Set production database credentials
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Configure monitoring alerts
- [ ] Review rate limits
- [ ] Test disaster recovery

### Deploy to Cloud

#### AWS ECS

```bash
# Build and push image
docker build -t omega-prime:latest .
docker tag omega-prime:latest <aws-account>.dkr.ecr.region.amazonaws.com/omega-prime:latest
docker push <aws-account>.dkr.ecr.region.amazonaws.com/omega-prime:latest

# Deploy using ECS CLI
ecs-cli compose --project-name omega-prime up
```

#### Azure Container Instances

```bash
az container create \
  --resource-group omega-rg \
  --name omega-prime \
  --image <registry>.azurecr.io/omega-prime:latest \
  --environment-variables OMEGA_SECRET_KEY=<secret>
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T12:00:00Z",
  "version": "2.0.0-production",
  "uptime": 3600,
  "memory_mb": 512
}
```

### Grafana Dashboards

1. Access: `http://localhost:3000`
2. Login: `admin / <GRAFANA_PASSWORD>`
3. Import dashboard: `omega-dashboard.json`

### Log Analysis

```bash
# View real-time logs
tail -f omega.log

# Search for errors
grep ERROR omega.log

# Count by log level
grep -c INFO omega.log
```

---

## 🔐 Security

### Best Practices

1. **Never commit secrets**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Rotate keys regularly**
   - Change `OMEGA_SECRET_KEY` every 90 days
   - Update all licenses after rotation

3. **Use secrets management**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

4. **Enable audit logging**
   ```csharp
   Logger.Log(LogLevel.INFO, $"User {userId} performed action {action}");
   ```

5. **Regular security audits**
   ```bash
   dotnet list package --vulnerable
   ```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "OMEGA_SECRET_KEY not set"

**Solution:**
```bash
export OMEGA_SECRET_KEY="$(openssl rand -base64 32)"
```

#### Issue: "Rate limit exceeded"

**Solution:** Increase limit in `.env`:
```bash
OMEGA_RATE_LIMIT=120
```

#### Issue: "Out of memory"

**Solution:** Reduce concurrent tasks:
```bash
OMEGA_MAX_CONCURRENT=25
```

#### Issue: "License validation failed"

**Solution:** Generate new license:
```csharp
var newLicense = SecurityValidator.GenerateLicense(
    "customer-id", 
    DateTime.UtcNow.AddYears(1)
);
```

### Debug Mode

```bash
export LOG_LEVEL=DEBUG
dotnet run
```

---

## 💼 สำหรับ Developer / Reseller

### อยากนำ OMEGA PRIME ไปขายต่อ?
Gold tier （¥20,000/เดือน） ให้สิทธิ์คุณ:
- ✅ **White-label** — เปลี่ยนชื่อระบบเป็นแบรนด์คุณ
- ✅ **Commercial License** — ขายต่อให้ลูกค้าได้
- ✅ **SLA 99.9%** — License Server พร้อมใช้ตลอด
- ✅ **Custom Feature** — ขอ feature เพิ่มได้เดือนละ 1 เรื่อง
- ✅ **Support ตลอดชีพ** — ผมดูแล technical ให้

**ตัวอย่าง Business Model สำหรับ Reseller:**

| รายการ | จำนวน |
|--------|-------|
| ต้นทุน Gold License | ¥20,000/เดือน (≈10,000฿) |
| ขายต่อให้ลูกค้า รายละ | ¥50,000-100,000/เดือน |
| จำนวนลูกค้าขั้นต่ำที่คุ้มทุน | **1 ราย** |
| กำไรต่อลูกค้า 1 ราย | 150-400% |

### อยากเป็น合作伙伴 (Partner)?
ส่ง LINE/Email มาคุยได้เลย → เรามี **affiliate program** สำหรับ:
- Tech Blogger / YouTuber — ได้ค่าคอมมิชชั่น 20%
- Software Agency — ได้ราคา reseller พิเศษ
- อาจารย์มหาวิทยาลัย — ได้ educational discount

---

## 📝 License

OMEGA PRIME ใช้ **Dual License**:
- **Free Tier:** MIT License — ใช้ส่วนตัว/การศึกษา/เรียนรู้
- **Commercial Tier:** Proprietary License — ใช้เชิงพาณิชย์ต้องมี License Key

[ดูรายละเอียด License เต็ม →](LICENSE.md)  
[ดู Premium Features →](monetization/PREMIUM.md)

---

## 👨‍💻 Author

**Architect:** Chaiyaphop Nilpaet (DJsinning / sexbb)  
**Version:** 2.0.0-production  
**Built with:** ❤️ + C# .NET 8 + Python 3.11 🇹🇭

---

## 🙏 Support & Contact

| ช่องทาง | สำหรับ | Link |
|---------|--------|------|
| 🐛 **GitHub Issues** | Bug report, Feature request | [Open Issue](https://github.com/chaiyaphop/omegaprime/issues) |
| 💬 **LINE** | ลูกค้าไทย สอบถามด่วน | `@omegaprime` |
| 📧 **Email** | Enterprise, Partnership | chaiyaphop@omegaprime.dev |
| 💖 **GitHub Sponsors** | สนับสนุน 0% fee | [Sponsor](https://github.com/sponsors/chaiyaphop) |
| ☕ **Buy Me a Coffee** | สนับสนุนเล็กน้อย | [Buy Coffee](https://www.buymeacoffee.com/chaiyaphop) |

---
*ติดต่อซื้อ license:** chaiyaphop@omegaprime.dev  
> **หรือกด สนันสนุน ที่ เลขพร้อมเพย์ 0886363126  SCB 1512396228
> 

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=chaiyaphop/omegaprime&type=Date)](https://star-history.com/#chaiyaphop/omegaprime&Date)

---

> **OMEGA PRIME** — เพราะ AI ที่ดี ควรเข้าถึงได้ทุกคน 🚀
