import json
import httpx

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

OLLAMA_URL = "http://127.0.0.1:11434"

app = FastAPI(title="Ollama CORS Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "ollama-proxy",
        "ollama": OLLAMA_URL,
    }


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")

        return {
            "proxy": "ok",
            "ollama": "ok",
            "ollama_status": r.status_code,
        }

    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "proxy": "ok",
                "ollama": "unreachable",
                "error": str(e),
            },
        )


async def get_models():
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.get(f"{OLLAMA_URL}/v1/models")


@app.get("/models")
async def models():
    r = await get_models()

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type="application/json",
    )


@app.get("/v1/models")
async def v1_models():
    r = await get_models()

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type="application/json",
    )


async def send_to_ollama(data):
    """
    Send a clean JSON object to Ollama's OpenAI-compatible endpoint.
    """
    streaming = bool(data.get("stream", False))

    # Disable thinking/reasoning
    data["think"] = False

    if not streaming:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                r = await client.post(
                    f"{OLLAMA_URL}/v1/chat/completions",
                    json=data,
                )

            return Response(
                content=r.content,
                status_code=r.status_code,
                media_type=r.headers.get(
                    "content-type",
                    "application/json",
                ),
            )

        except Exception as e:
            return JSONResponse(
                status_code=502,
                content={
                    "error": {
                        "message": f"Ollama connection error: {str(e)}",
                        "type": "proxy_error",
                    }
                },
            )

    async def generate():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/v1/chat/completions",
                    json=data,
                ) as r:

                    async for chunk in r.aiter_raw():
                        yield chunk

        except Exception as e:
            error = {
                "error": {
                    "message": str(e),
                    "type": "proxy_error",
                }
            }

            yield (
                "data: " +
                json.dumps(error) +
                "\n\n"
            ).encode()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


async def handle_chat(request: Request):
    try:
        data = await request.json()

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": f"Invalid JSON: {str(e)}",
                    "type": "invalid_request_error",
                }
            },
        )

    if not isinstance(data, dict):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": "Request body must be a JSON object.",
                    "type": "invalid_request_error",
                }
            },
        )

    return await send_to_ollama(data)


# Standard OpenAI-compatible endpoint
@app.post("/chat/completions")
async def chat_completions(request: Request):
    return await handle_chat(request)


# Ollama OpenAI-compatible endpoint
@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    return await handle_chat(request)


# Some clients send directly to /v1
@app.post("/v1")
async def v1_post(request: Request):
    return await handle_chat(request)


# Some proxy configurations effectively send the request to the
# configured base URL itself.
@app.post("/")
async def root_post(request: Request):
    return await handle_chat(request)


# Handle browser CORS preflight requests.
@app.options("/")
@app.options("/v1")
@app.options("/models")
@app.options("/v1/models")
@app.options("/chat/completions")
@app.options("/v1/chat/completions")
async def options():
    return Response(status_code=204)


@app.on_event("shutdown")
async def shutdown():
    pass
