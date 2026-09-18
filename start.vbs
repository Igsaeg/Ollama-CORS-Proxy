Set shell = CreateObject("WScript.Shell")

projectDir = "C:\Users\igsaeg\Projects\ollama proxy"

shell.CurrentDirectory = projectDir

' Start Uvicorn
shell.Run "cmd /c .venv\Scripts\python.exe -m uvicorn proxy:app --host 0.0.0.0 --port 8000", 0, False

' Start ngrok
shell.Run "cmd /c ngrok http 8000", 0, False

' Give the processes a moment to start
WScript.Sleep 100

' Check whether port 8000 is listening
Set exec = shell.Exec("cmd /c netstat -ano | findstr :8000")
output = exec.StdOut.ReadAll()

If InStr(output, "LISTENING") > 0 Then
    shell.Popup "Ollama CORS Proxy started successfully.", 3, "Ollama Proxy", 64
Else
    shell.Popup "Failed to start the Ollama CORS Proxy." & vbCrLf & vbCrLf & _
                "Check your Python environment and configuration.", 5, "Ollama Proxy", 16
End If

Set shell = Nothing