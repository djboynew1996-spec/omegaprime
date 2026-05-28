# OMEGA PRIME — Web Store Runner (24/7)
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
Set-Location "D:\ai ทำงาน\OmegaPrime"

# Load .env.local (auto-loaded by web/app.py)
# keys are stored in .env.local (gitignored, no need to set here)

# Run web store
python web/app.py
