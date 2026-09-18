# Ollama CORS Proxy

A lightweight FastAPI proxy that exposes a local **Ollama** instance through an OpenAI-compatible API with **CORS support**.

This makes locally hosted Ollama models accessible to browser-based applications and other services that support OpenAI-compatible APIs.

## Architecture

```text
Client / Application
        │
        │ HTTPS
        ▼
      ngrok
        │
        ▼
 FastAPI Proxy :8000
        │
        │ HTTP
        ▼
 Ollama :11434
        │
        ▼
   Local LLM
```

## Features

* OpenAI-compatible `/chat/completions` endpoint
* Ollama `/v1/chat/completions` forwarding
* CORS support
* `/models` and `/v1/models` endpoints
* Streaming response support
* Optional disabling of model thinking/reasoning
* ngrok support for remote access
* Hidden Windows launcher with startup confirmation

## Requirements

* Windows 10/11
* Python 3.10+
* [Ollama](https://ollama.com/)
* [ngrok](https://ngrok.com/)

Verify Ollama is running:

```powershell
ollama list
```

## Installation

Clone the repository:

```powershell
git clone https://github.com/Igsaeg/ollama-cors-proxy.git
cd ollama-cors-proxy
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn httpx
```

## Running

### Manual

Start the FastAPI proxy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn proxy:app --host 0.0.0.0 --port 8000
```

In another terminal, expose the proxy through ngrok:

```powershell
ngrok http 8000
```

ngrok will provide a public HTTPS URL:

```text
https://<your-ngrok-url>.ngrok-free.dev
```

### Windows Launcher

The project includes a `start.vbs` launcher that starts both Uvicorn and ngrok in the background without leaving terminal windows open.

Before using it, set the project directory inside `start.vbs`:

```vbscript
projectDir = "C:\path\to\your\project"
```

Then double-click:

```text
start.vbs
```

The launcher:

1. Starts Uvicorn using the project's `.venv`.
2. Starts ngrok on port `8000`.
3. Waits for the proxy to start.
4. Checks whether the local proxy is responding.
5. Displays a confirmation popup when the proxy starts successfully.

A successful startup will show:

```text
Ollama CORS Proxy is running.
```

If the proxy fails to start, the launcher displays an error instead.

### Stopping the Server

Use:

```text
stop.bat
```

This stops the process listening on port `8000` and terminates ngrok.

## API Endpoints

| Endpoint                    | Purpose                                |
| --------------------------- | -------------------------------------- |
| `GET /`                     | Proxy status                           |
| `GET /health`               | Ollama connectivity check              |
| `GET /models`               | List available models                  |
| `GET /v1/models`            | OpenAI-compatible model list           |
| `POST /chat/completions`    | OpenAI-compatible chat endpoint        |
| `POST /v1/chat/completions` | Ollama/OpenAI-compatible chat endpoint |

The proxy translates:

```text
/chat/completions
        ↓
/v1/chat/completions
        ↓
Ollama
```

## Testing

### Check the proxy

```powershell
curl.exe http://127.0.0.1:8000/
```

### Check available models

```powershell
curl.exe http://127.0.0.1:8000/v1/models
```

### Test a completion

Create `test.json`:

```json
{
  "model": "YOUR_OLLAMA_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Say hello in one sentence."
    }
  ],
  "stream": false
}
```

Send the request:

```powershell
curl.exe http://127.0.0.1:8000/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@test.json"
```

You can test the same endpoint through ngrok:

```powershell
curl.exe https://<your-ngrok-url>.ngrok-free.dev/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@test.json"
```

## Using With OpenAI-Compatible Applications

Applications that support custom OpenAI-compatible API endpoints can use:

```text
Base URL:
https://<your-ngrok-url>.ngrok-free.dev
```

The exact configuration depends on the application.

For clients that expect the OpenAI API structure, the chat endpoint is:

```text
https://<your-ngrok-url>.ngrok-free.dev/v1/chat/completions
```

The proxy also accepts:

```text
https://<your-ngrok-url>.ngrok-free.dev/chat/completions
```

## Disabling Thinking

For Ollama models that support the `think` parameter, add:

```python
data["think"] = False
```

before forwarding the request to Ollama.

For example:

```python
streaming = bool(data.get("stream", False))
data["think"] = False
```

This can prevent supported reasoning models from generating unnecessary reasoning output.

## Project Structure

```text
ollama-cors-proxy/
├── .venv/
├── proxy.py
├── start.vbs
├── stop.bat
├── .gitignore
└── README.md
```

`.venv/` is the project's Python virtual environment and should not be committed to Git.

Add it to `.gitignore`:

```gitignore
.venv/
```

## Security

ngrok exposes the local proxy to the Internet.

Anyone with the public ngrok URL may be able to send requests to your Ollama instance.

For personal use:

* Keep the ngrok URL private.
* Stop ngrok when it is not needed.
* Do not commit API keys or credentials.

For public deployments, add authentication and rate limiting to the proxy.

## License

MIT