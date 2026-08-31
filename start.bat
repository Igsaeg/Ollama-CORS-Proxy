@echo off
set PROJECT_DIR=C:\Users\igsaeg\Projects\ollama proxy
 
wt -w 0 new-tab --title "Uvicorn" -d "%PROJECT_DIR%" cmd /k ".\.venv\Scripts\python.exe -m uvicorn proxy:app --host 0.0.0.0 --port 8000" ; new-tab --title "Ngrok" -d "%PROJECT_DIR%" cmd /k "ngrok http 8000"
 