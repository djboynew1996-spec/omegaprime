#!/usr/bin/env pwsh
<#
╔══════════════════════════════════════════════════════════════╗
║      OMEGA PRIME — Auto Money Engine v2.0                   ║
║      ระบบรับเงินอัตโนมัติ — ไม่ต้องรันเซิร์ฟเวอร์            ║
╚══════════════════════════════════════════════════════════════╝

เลือกวิธีที่ต้องการ:

  [1] PIPEDREAM (แนะนำ) — 100% Serverless ฟรี ตลอดไป
      ใช้ Pipedream รับ Stripe Webhook → สร้าง License → ส่งถึงลูกค้า
      ไม่ต้องรันอะไรเลยบนเครื่องคุณ!

  [2] LOCAL TUNNEL — ใช้ localhost.run (ฟรี ไม่ต้องสมัคร)
      เปิด Terminal ทิ้งไว้ รับเงิน Auto จนกว่าจะปิด
      เหมาะสำหรับทดสอบ หรือใช้ระหว่างวัน

#>
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║      OMEGA PRIME — Auto Money Engine v2.0                   ║
╚══════════════════════════════════════════════════════════════╝

เลือกวิธี:

  [1] PIPEDREAM (แนะนำ) — 100% Serverless ฟรี ตลอดไป

  [2] LOCAL TUNNEL — ทดสอบทันที ใช้ localhost.run

  [3] อ่านคู่มือ
"@ -ForegroundColor Cyan

$choice = Read-Host "`nเลือก (1, 2, หรือ 3)"

switch ($choice) {
    "1" {
        Write-Host "`n[OK] ไปที่ https://pipedream.com สมัครฟรี (ใช้ Google/GitHub) แล้วทำตาม:"
        Write-Host "`n  1. New Workflow -> HTTP / Webhook -> Instant Response"
        Write-Host "  2. ก็อป URL -> ไป Stripe Dashboard -> Webhooks -> Add endpoint"
        Write-Host "  3. ใน Pipedream เพิ่ม step 'Run Python' -> วางโค้ดจาก:"
        Write-Host "     monetization/auto_license_webhook.py"
        Write-Host "  4. ตั้ง Environment Variables: OMEGA_SECRET_KEY + STRIPE_API_KEY"
        Write-Host "`n[GUIDE] ดูรายละเอียดใน monetization/AUTO_MONEY_GUIDE.md" -ForegroundColor Green
    }
    "2" {
        # === LOCAL TUNNEL METHOD ===
        $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
        
        # Load env
        $envFile = Join-Path $ProjectRoot ".env.local"
        if (Test-Path $envFile) {
            Get-Content $envFile | ForEach-Object {
                if ($_ -match "^\s*([^#=]+)=(.+)$") {
                    [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
                }
            }
        }
        
        if (-not $env:OMEGA_SECRET_KEY) {
            Write-Host "[ERROR] OMEGA_SECRET_KEY not set!" -ForegroundColor Red
            exit 1
        }
        
        # Start Flask webhook server
        $webhookDir = Join-Path $ProjectRoot "monetization"
        $logFile = Join-Path $ProjectRoot "auto_money.log"
        
        Write-Host "[START] Starting license server on port 8080..." -ForegroundColor Green
        $job = Start-Job -ScriptBlock {
            param($dir, $log)
            Set-Location $dir
            python stripe_webhook.py --port 8080 *>> $log
        } -ArgumentList $webhookDir, $logFile
        Start-Sleep -Seconds 3
        
        # Create SSH tunnel
        Write-Host "[TUNNEL] Creating public URL (no account needed)..." -ForegroundColor Yellow
        $tunnelLog = Join-Path $ProjectRoot "tunnel_url.txt"
        ssh -o StrictHostKeyChecking=no -R 80:localhost:8080 nokey@localhost.run 2>&1 | Tee-Object -FilePath $tunnelLog
        
        # Cleanup on exit
        Get-Job -Name "OmegaWebhook*" | Stop-Job
    }
    "3" {
        Write-Host "`n[GUIDE] อ่านคู่มือ: monetization/AUTO_MONEY_GUIDE.md" -ForegroundColor Green
        Write-Host "[CODE] โค้ด Pipedream: monetization/auto_license_webhook.py"
        Write-Host "[WEB] Flask Server: monetization/stripe_webhook.py"
    }
}
