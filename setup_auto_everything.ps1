#!/usr/bin/env pwsh
<#
╔══════════════════════════════════════════════════════════════╗
║   OMEGA PRIME — Auto Money Setup (Complete)                ║
║   ตั้งค่าทุกอย่างอัตโนมัติ — ไม่ต้องทำอะไรเลย!             ║
╚══════════════════════════════════════════════════════════════╝
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$StripeCli = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Stripe.StripeCli_Microsoft.Winget.Source_8wekyb3d8bbwe\stripe.exe"

# ============================================================
# 1. ตรวจสอบของที่ต้องใช้
# ============================================================
Write-Host "`n[1/5] ตรวจสอบระบบ..." -ForegroundColor Cyan

# ตรวจสอบ Python libs
$hasFlask = python -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> ติดตั้ง Flask..."
    pip install flask stripe 2>&1 | Out-Null
}

# ตรวจสอบ Stripe CLI
if (-not (Test-Path $StripeCli)) {
    Write-Host "  -> กำลังติดตั้ง Stripe CLI..."
    winget install Stripe.StripeCli --silent --accept-package-agreements 2>&1 | Out-Null
}
Write-Host "  -> พร้อม!" -ForegroundColor Green

# ============================================================
# 2. โหลด Environment Variables
# ============================================================
Write-Host "`n[2/5] โหลด Environment Variables..." -ForegroundColor Cyan
$envFile = Join-Path $ProjectRoot ".env.local"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)=(.+)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

# ตรวจสอบคีย์สำคัญ
if (-not $env:OMEGA_SECRET_KEY) { $env:OMEGA_SECRET_KEY = "MyOmegaSuperSecretKey2026!" }
if (-not $env:STRIPE_API_KEY) { 
    Write-Host "  [ERROR] STRIPE_API_KEY not found in .env.local!" -ForegroundColor Red
    Write-Host "  ใส่ STRIPE_API_KEY ของคุณในไฟล์ .env.local แล้วรันใหม่"
    exit 1
}
Write-Host "  -> OMEGA_SECRET_KEY: พร้อม" -ForegroundColor Green
Write-Host "  -> STRIPE_API_KEY: พร้อม" -ForegroundColor Green

# ============================================================
# 3. Kill กระบวนการเก่า
# ============================================================
Write-Host "`n[3/5] Cleanup ระบบเก่า..." -ForegroundColor Cyan
Get-Process -Name python, stripe -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "  -> Done!" -ForegroundColor Green

# ============================================================
# 4. สตาร์ท Flask Webhook Server
# ============================================================
Write-Host "`n[4/5] เริ่ม License Server..." -ForegroundColor Cyan
$webhookDir = Join-Path $ProjectRoot "monetization"
$flaskLog = Join-Path $ProjectRoot "server_log.txt"

# สตาร์ท Flask (ใช้ Start-Process ในหน้าต่างใหม่)
$env:STRIPE_WEBHOOK_SECRET = ""  # จะได้จาก Stripe listen
Start-Process -FilePath "python" -ArgumentList "stripe_webhook.py --port 8080" -WorkingDirectory $webhookDir -WindowStyle Minimized
Start-Sleep -Seconds 3

# ตรวจสอบ
$portCheck = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if (-not $portCheck) {
    Write-Host "  [ERROR] Flask ไม่สตาร์ท!" -ForegroundColor Red
    exit 1
}
Write-Host "  -> License Server ทำงานที่ port 8080 (PID: $($portCheck.OwningProcess))" -ForegroundColor Green

# ============================================================
# 5. เริ่ม Stripe Listen (เชื่อม Stripe → Local)
# ============================================================
Write-Host "`n[5/5] เริ่ม Stripe Webhook Forward..." -ForegroundColor Cyan
$stripeLog = Join-Path $ProjectRoot "stripe_listen_output.txt"

# สตาร์ท stripe listen
$env:STRIPE_API_KEY = $env:STRIPE_API_KEY
Start-Process -FilePath $StripeCli -ArgumentList "listen", "--forward-to", "http://localhost:8080/webhook/stripe" -WindowStyle Minimized
Start-Sleep -Seconds 5

Write-Host "  -> Stripe Listen started!" -ForegroundColor Green

# ============================================================
# แสดงผลลัพธ์
# ============================================================
Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ ระบบ Auto Money ทำงานแล้ว!          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  🔗 Stripe → Local Webhook: localhost:8080/webhook/stripe"
Write-Host "  🔗 Health Check: http://localhost:8080/health"
Write-Host ""
Write-Host "  💰 เมื่อลูกค้าจ่ายเงิน → License สร้างอัตโนมัติ!"
Write-Host ""
Write-Host "  ⚡ ทดสอบ: เปิด PowerShell อีกอันแล้วรัน:"
Write-Host "     stripe trigger checkout.session.completed"
Write-Host ""
Write-Host "  ❌ ปิดระบบ: กด Ctrl+C หรือรัน:"
Write-Host "     Get-Process python,stripe | Stop-Process -Force"
Write-Host ""

# รอ
while ($true) {
    Start-Sleep -Seconds 30
    # ตรวจสอบว่า Flask ยังรันอยู่
    $p = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if (-not $p) {
        Write-Host "[ERROR] Flask server หยุดทำงาน!" -ForegroundColor Red
        break
    }
}
