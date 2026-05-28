<#
==================================================================================
OMEGA PRIME — Auto-Start System (1 Click)
==================================================================================
Start everything with one command:
  - Web License Store (port 5000) 
  - License Server (port 8080) 
  - Auto-open browser
  - Auto-setup Stripe webhook

Usage:
  .\start.ps1            # Start everything (interactive)
  .\start.ps1 -Daemon    # Start as background service (no window)
  .\start.ps1 -Install   # Install as Windows startup task
  .\start.ps1 -Status    # Check if running
  .\start.ps1 -Stop      # Stop all services

Requirements:
  - Python 3.8+
  - PowerShell 5.1+
==================================================================================
#>

param(
    [switch]$Daemon,
    [switch]$Install,
    [switch]$Status,
    [switch]$Stop,
    [switch]$Help
)

$ROOT_DIR = Split-Path -Parent $PSCommandPath
$WEB_DIR = Join-Path $ROOT_DIR "web"
$MONETIZATION_DIR = Join-Path $ROOT_DIR "monetization"
$LOG_DIR = Join-Path $ROOT_DIR "logs"
$PID_FILE = Join-Path $ROOT_DIR ".omega_pids"

# Ensure log directory
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }

function Show-Banner {
    Write-Host @"

╔══════════════════════════════════════════════════╗
║        OMEGA PRIME — AUTO-START SYSTEM           ║
╚══════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $color = @{
        "INFO" = "Cyan"
        "OK" = "Green"
        "ERROR" = "Red"
        "WARN" = "Yellow"
    }
    Write-Host "[$($color[$Status])$Status$($color[$Status])] $Message" -ForegroundColor $color[$Status]
}

function Test-Dependencies {
    Write-Status "Checking dependencies..." "INFO"
    
    # Check Python
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Status "Python not found! Install Python 3.8+" "ERROR"
        return $false
    }
    Write-Status "Python: $(python --version 2>&1)" "OK"
    
    # Check Flask
    $flask = python -c "import flask; print(flask.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Installing Flask dependencies..." "WARN"
        pip install flask flask-cors stripe python-dotenv -q
    }
    Write-Status "Flask: $(python -c 'import flask; print(flask.__version__)')" "OK"
    
    return $true
}

function Load-Env {
    # Source .env.local
    $envFile = Join-Path $ROOT_DIR ".env.local"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            $line = $_.Trim()
            if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
                $parts = $line.Split("=", 2)
                [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
            }
        }
        Write-Status "Loaded .env.local" "OK"
    } else {
        Write-Status ".env.local not found — creating from .env.example..." "WARN"
        Copy-Item (Join-Path $ROOT_DIR ".env.example") $envFile
        Write-Status "Edit .env.local with your keys and re-run" "WARN"
        return $false
    }
    return $true
}

function Save-Pid {
    param([string]$Name, [int]$Pid)
    $pids = @{}
    if (Test-Path $PID_FILE) {
        $pids = Get-Content $PID_FILE | ConvertFrom-Json
    }
    $pids.$Name = $Pid
    $pids | ConvertTo-Json | Set-Content $PID_FILE
}

function Remove-Pid {
    param([string]$Name)
    if (Test-Path $PID_FILE) {
        $pids = Get-Content $PID_FILE | ConvertFrom-Json
        $pids.PSObject.Properties.Remove($Name)
        if ($pids.PSObject.Properties.Count -eq 0) {
            Remove-Item $PID_FILE -Force
        } else {
            $pids | ConvertTo-Json | Set-Content $PID_FILE
        }
    }
}

function Start-LicenseServer {
    Write-Status "Starting License Server (port 8080)..." "INFO"
    
    $logFile = Join-Path $LOG_DIR "license_server.log"
    $script = Join-Path $MONETIZATION_DIR "stripe_webhook.py"
    
    if (Test-Path $script) {
        $proc = Start-Process -NoNewWindow -FilePath "python" -ArgumentList @($script, "--port", "8080") `
            -RedirectStandardOutput $logFile -RedirectStandardError $logFile -PassThru
        Save-Pid -Name "license_server" -Pid $proc.Id
        Write-Status "License Server started (PID: $($proc.Id))" "OK"
        return $true
    } else {
        Write-Status "License server script not found — skipping" "WARN"
        return $false
    }
}

function Start-WebStore {
    Write-Status "Starting Web License Store (port 5000)..." "INFO"
    
    $logFile = Join-Path $LOG_DIR "web_store.log"
    $script = Join-Path $WEB_DIR "app.py"
    
    $proc = Start-Process -NoNewWindow -FilePath "python" -ArgumentList @($script) `
        -RedirectStandardOutput $logFile -RedirectStandardError $logFile -PassThru
    Save-Pid -Name "web_store" -Pid $proc.Id
    Write-Status "Web Store started (PID: $($proc.Id))" "OK"
    return $true
}

function Wait-For-Web {
    param([string]$Url, [int]$Timeout = 15)
    
    $elapsed = 0
    while ($elapsed -lt $Timeout) {
        try {
            $request = [System.Net.WebRequest]::Create($Url)
            $request.Timeout = 1000
            $response = $request.GetResponse()
            $response.Close()
            return $true
        } catch {
            Start-Sleep -Seconds 1
            $elapsed++
        }
    }
    return $false
}

function Start-Browser {
    $url = "http://localhost:5000"
    Write-Status "Opening browser: $url" "INFO"
    Start-Process $url
}

# ============================================================================
# COMMANDS
# ============================================================================

if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

if ($Install) {
    # Install as Windows startup task
    Write-Status "Installing as Windows startup task..." "INFO"
    
    $taskName = "OmegaPrime-AutoStart"
    $scriptPath = $PSCommandPath
    
    # Remove existing task if any
    schtasks /Delete /F /TN $taskName 2>$null
    
    # Create scheduled task (run at user login)
    schtasks /Create /TN $taskName /TR "powershell.exe -WindowStyle Hidden -File '$scriptPath' -Daemon" /SC ONLOGON /DELAY 0000:30 /F
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "✅ Startup task installed! Will auto-start on next login." "OK"
        Write-Status "   Task: $taskName" "INFO"
        Write-Status "   Run:  schtasks /Run /TN $taskName (to start now)" "INFO"
    } else {
        Write-Status "Failed to install startup task (run as Admin?)" "ERROR"
    }
    exit
}

if ($Status) {
    Write-Host @"

=== OMEGA PRIME — Status ===

"@
    if (Test-Path $PID_FILE) {
        $pids = Get-Content $PID_FILE | ConvertFrom-Json
        foreach ($prop in $pids.PSObject.Properties) {
            $proc = Get-Process -Id $prop.Value -ErrorAction SilentlyContinue
            if ($proc) {
                $mem = [math]::Round($proc.WorkingSet64 / 1MB, 1)
                $cpu = $proc.CPU
                Write-Host "  ✅ $($prop.Name): running (PID $($prop.Value), Mem: ${mem}MB)" -ForegroundColor Green
            } else {
                Write-Host "  ❌ $($prop.Name): NOT running (stale PID $($prop.Value))" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  ⚠️  No services running" -ForegroundColor Yellow
    }
    
    # Check port status
    $port5000 = netstat -ano | Select-String ":5000.*LISTENING"
    $port8080 = netstat -ano | Select-String ":8080.*LISTENING"
    if ($port5000) { Write-Host "  🌐 Port 5000 (Web Store): LISTENING" -ForegroundColor Green }
    if ($port8080) { Write-Host "  🌐 Port 8080 (License): LISTENING" -ForegroundColor Green }
    
    exit
}

if ($Stop) {
    Write-Status "Stopping all services..." "INFO"
    
    if (Test-Path $PID_FILE) {
        $pids = Get-Content $PID_FILE | ConvertFrom-Json
        foreach ($prop in $pids.PSObject.Properties) {
            $proc = Get-Process -Id $prop.Value -ErrorAction SilentlyContinue
            if ($proc) {
                Stop-Process -Id $prop.Value -Force
                Write-Status "Stopped $($prop.Name) (PID $($prop.Value))" "OK"
            }
        }
        Remove-Item $PID_FILE -Force
    }
    
    # Kill any remaining python processes on our ports
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
        if ($cmd -match "omega|stripe_webhook|web.app") {
            Stop-Process -Id $_.Id -Force
            Write-Status "Cleaned up orphan: $_" "OK"
        }
    }
    
    Write-Status "All services stopped" "OK"
    exit
}

# ============================================================================
# MAIN START
# ============================================================================

Show-Banner

# Step 1: Check dependencies
if (-not (Test-Dependencies)) { exit 1 }

# Step 2: Load environment
if (-not (Load-Env)) { exit 1 }

# Step 3: Stop any existing instances
Write-Status "Checking for existing instances..." "INFO"
& $PSCommandPath -Stop 2>$null

# Step 4: Start services
Start-LicenseServer
Start-WebStore

# Step 5: Wait for ready
Write-Status "Waiting for services to start..." "INFO"
$webReady = Wait-For-Web "http://localhost:5000/health"
$licenseReady = Wait-For-Web "http://localhost:8080/health" -Timeout 10

# Step 6: Show results
Write-Host @"

╔══════════════════════════════════════════════════╗
║              SERVICES STATUS                     ║
╠══════════════════════════════════════════════════╣
"@

if ($webReady) {
    Write-Host "║  🌐  Web License Store    http://localhost:5000   ✅   ║" -ForegroundColor Green
} else {
    Write-Host "║  🌐  Web License Store    http://localhost:5000   ❌   ║" -ForegroundColor Red
}

if ($licenseReady) {
    Write-Host "║  🔑  License Server       http://localhost:8080   ✅   ║" -ForegroundColor Green
} else {
    Write-Host "║  🔑  License Server       http://localhost:8080   ❌   ║" -ForegroundColor Red
}

Write-Host "╚══════════════════════════════════════════════════╝"
Write-Host @"

  📋  Commands:
       .\start.ps1           — Start everything
       .\start.ps1 -Status   — Check status
       .\start.ps1 -Stop     — Stop all services
       .\start.ps1 -Install  — Auto-start on boot
       .\start.ps1 -Daemon   — Silent background mode

  Logs: $LOG_DIR
"@

# Step 7: Open browser (unless daemon mode)
if (-not $Daemon) {
    Start-Browser
}

Write-Status "System ready! 🚀" "OK"

# In daemon mode, keep process alive
if ($Daemon) {
    Write-Status "Running in background mode — press Ctrl+C to stop" "INFO"
    while ($true) { Start-Sleep -Seconds 60 }
}
