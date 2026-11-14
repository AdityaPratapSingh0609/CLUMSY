@echo off
title DESKBOT // J.A.R.V.I.S. Production Hub
color 0B
echo ============================================================
echo      DESKBOT // J.A.R.V.I.S. FUSION COMMAND CENTER
echo ============================================================
echo  Starting local servers and mesh networking on port 8080...
echo.
python scripts/deploy_jarvis.py --port 8080
pause
