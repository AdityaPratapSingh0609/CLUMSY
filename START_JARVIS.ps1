# DESKBOT // J.A.R.V.I.S. Production Startup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     DESKBOT // J.A.R.V.I.S. FUSION COMMAND CENTER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting local servers and mesh networking on port 8080..." -ForegroundColor White
python scripts/deploy_jarvis.py --port 8080
