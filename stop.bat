@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /F /PID %%a >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1