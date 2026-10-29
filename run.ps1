# ConstructIQ Launch Script for PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🏗️ ConstructIQ: Multimodal Construction Intelligence" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit Application on http://localhost:8501..." -ForegroundColor Green

streamlit run app.py
