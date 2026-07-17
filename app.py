
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import edge_tts
import asyncio
import io
import os

app = FastAPI(title="FREE Edge TTS - OpenAI Compatible", version="1.0")

# Best voices for cat content
VOICES = {
    "en-US-JennyNeural": "Female, Educational - BEST",
    "en-US-AriaNeural": "Female, Friendly",
    "en-US-GuyNeural": "Male, Calm Vet",
    "en-GB-SoniaNeural": "Female, British Premium",
    "en-US-EmmaNeural": "Female, Cute"
}

class TTSRequest(BaseModel):
    model: str = "edge-tts"
    input: str = ""  # OpenAI format
    text: str = ""   # Alternative
    voice: str = "en-US-JennyNeural"
    speed: str = "+0%"

@app.get("/")
async def root():
    return {
        "status": "FREE Edge TTS Server Running ✅",
        "cost": "0$ forever",
        "voices": VOICES,
        "usage": "POST /v1/audio/speech with {input: 'text', voice: 'en-US-JennyNeural'}",
        "n8n_url": "Use this server URL in n8n: https://YOUR-APP.onrender.com/v1/audio/speech"
    }

@app.get("/voices")
async def list_voices():
    return VOICES

@app.post("/v1/audio/speech")
async def tts_openai_compatible(req: TTSRequest):
    # Support both OpenAI format (input) and simple format (text)
    text = req.input or req.text
    if not text:
        raise HTTPException(status_code=400, detail="Missing text/input")
    if len(text) > 5000:
        text = text[:5000]  # Edge limit

    voice = req.voice or "en-US-JennyNeural"

    # Map speed to edge format
    rate = req.speed if "%" in req.speed else "+0%"

    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=voice.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple endpoint for n8n HTTP Request node
@app.post("/tts")
async def tts_simple(req: TTSRequest):
    return await tts_openai_compatible(req)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
