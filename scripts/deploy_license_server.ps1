#!/usr/bin/env pwsh
<#
==================================================================================
OMEGA PRIME — Deploy License Server
==================================================================================
One-click deploy of the OMEGA PRIME monetization system.

Usage:
    # Deploy locally (development)
    .\deploy_license_server.ps1 -Mode local
    
    # Deploy to Docker (production)
    .\deploy_license_server.ps1 -Mode docker
    
    # Deploy to cloud (coming soon)
    .\deploy_license_server.ps1 -Mode cloud -Provider azure

Requirements:
    - PowerShell 7+
    - Python 3.8+ (for local mode)
    - Docker (for docker mode)
==================================================================================
#>

param(
    [ValidateSet("local", "docker", "cloud")]
    [string]$Mode = "local",
    
    [string]$Provider = "",
    [string]$Port = "8080",
    [string]$SecretKey = "",
    [switch]$Help
)

if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$MONETIZATION_DIR = Join-Path $PROJECT_ROOT "monetization"
$SECRET_KEY = if ($SecretKey) { $SecretKey } else { [System.Guid]::NewGuid().ToString() }

Write-Host @"

╔══════════════════════════════════════════════════╗
║     OMEGA PRIME — License Server Deployer        ║
╚══════════════════════════════════════════════════╝

  Mode      : $Mode
  Port      : $Port
  Secret    : $($SECRET_KEY.Substring(0, 8))...
  Directory : $MONETIZATION_DIR

"@ -ForegroundColor Cyan

# ------------------------------------------------------------------
# Mode: Local (Python Flask)
# ------------------------------------------------------------------
if ($Mode -eq "local") {
    Write-Host "🔧 Setting up local license server..." -ForegroundColor Yellow
    
    # Check Python
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install flask stripe -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    # Set environment
    $env:OMEGA_SECRET_KEY = $SECRET_KEY
    $env:LICENSE_API_KEY = [System.Guid]::NewGuid().ToString()
    
    Write-Host @"

✅ Setup complete!

  🔑 OMEGA_SECRET_KEY  : $($SECRET_KEY.Substring(0, 16))...
  🔑 LICENSE_API_KEY   : $($env:LICENSE_API_KEY)
  
  🚀 Starting server on http://localhost:$Port
  
  📋 Endpoints:
     POST http://localhost:$Port/webhook/stripe  — Stripe webhook
     POST http://localhost:$Port/api/validate     — Validate license
     POST http://localhost:$Port/api/generate     — Generate license (admin)
     GET  http://localhost:$Port/health           — Health check
  
  Press Ctrl+C to stop.

"@ -ForegroundColor Green
    
    # Start server
    python "$MONETIZATION_DIR/stripe_webhook.py" --port $Port
}

# ------------------------------------------------------------------
# Mode: Docker
# ------------------------------------------------------------------
elseif ($Mode -eq "docker") {
    Write-Host "🐳 Building Docker image..." -ForegroundColor Yellow
    
    # Create Dockerfile for license server
    $dockerfile = @"
FROM python:3.11-slim

WORKDIR /app

COPY monetization/ /app/
RUN pip install flask stripe

ENV OMEGA_SECRET_KEY=$SECRET_KEY
ENV LICENSE_API_KEY=$( [System.Guid]::NewGuid().ToString() )

EXPOSE $Port

CMD ["python", "stripe_webhook.py", "--port", $Port]
"@
    
    $dockerfile | Set-Content -Path (Join-Path $PROJECT_ROOT "Dockerfile.license-server")
    
    Write-Host "🔨 Building license-server image..." -ForegroundColor Yellow
    docker build -f "$PROJECT_ROOT/Dockerfile.license-server" -t "omega-license-server:latest" "$PROJECT_ROOT"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🚀 Starting container..." -ForegroundColor Yellow
    docker run -d `
        --name omega-license-server `
        -p ${Port}:${Port} `
        -e OMEGA_SECRET_KEY=$SECRET_KEY `
        -e LICENSE_API_KEY=$env:LICENSE_API_KEY `
        --restart unless-stopped `
        omega-license-server:latest
    
    Write-Host @"

✅ License server deployed on Docker!

  🐳 Container : omega-license-server
  🔗 URL       : http://localhost:$Port
  🔑 API Key   : $env:LICENSE_API_KEY
  
  📋 Commands:
     docker logs omega-license-server    — View logs
     docker stop omega-license-server    — Stop server
     docker start omega-license-server   — Start server
  
  🔐 Set this in your app:
     set LICENSE_SERVER_URL=http://localhost:$Port

"@ -ForegroundColor Green
}

# ------------------------------------------------------------------
# Mode: Cloud (Coming Soon)
# ------------------------------------------------------------------
elseif ($Mode -eq "cloud") {
    Write-Host @"
    
🌤️  Cloud deployment coming soon!

  Supported providers (planned):
  - Azure Container Instances
  - AWS ECS / Fargate
  - Google Cloud Run
  - Railway / Render / Fly.io

  For now, use -Mode docker to deploy on your own server.

"@ -ForegroundColor Yellow
}

# ------------------------------------------------------------------
# Generate test license after deploy
# ------------------------------------------------------------------
Write-Host "🔑 Generating test license..." -ForegroundColor Yellow
python "$MONETIZATION_DIR/generate_license.py" --customer "test@omegaprime.dev" --tier silver --days 30

Write-Host @"

  📝  Next Steps:
  1. Set your Stripe webhook in Stripe Dashboard
     → https://dashboard.stripe.com/webhooks
     → URL: http://your-server:$Port/webhook/stripe
  
  2. Test payment flow
  3. Update FUNDING.yml with your Stripe links
  
  🎉  Your OMEGA PRIME monetization system is LIVE!

"@ -ForegroundColor Green
