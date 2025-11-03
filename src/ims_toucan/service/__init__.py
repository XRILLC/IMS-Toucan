"""REST API microservice for IMS-Toucan TTS."""

import io
import logging
import sys
from pathlib import Path
from typing import Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global TTS instance (lazy loaded)
_tts_instance = None
_device = "cpu"
_default_language = "eng"


class TTSRequest(BaseModel):
    """Request model for TTS synthesis."""
    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=10000)
    language: Optional[str] = Field("eng", description="Language code (ISO 639-3)")
    speed: Optional[float] = Field(1.0, description="Speech speed multiplier", ge=0.5, le=2.0)
    reference_audio: Optional[str] = Field(None, description="Base64-encoded reference audio for voice cloning")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    device: str
    model_loaded: bool
    version: str


class LanguagesResponse(BaseModel):
    """Supported languages response."""
    count: int
    languages: list[str]
    note: str


def get_tts():
    """Get or create TTS instance (singleton pattern)."""
    global _tts_instance

    if _tts_instance is None:
        logger.info(f"Initializing ToucanTTS (device: {_device}, language: {_default_language})")
        try:
            from InferenceInterfaces.ToucanTTSInterface import ToucanTTSInterface
            _tts_instance = ToucanTTSInterface(
                device=_device,
                language=_default_language
            )
            logger.info("ToucanTTS initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ToucanTTS: {e}")
            raise

    return _tts_instance


# FastAPI app
app = FastAPI(
    title="IMS-Toucan TTS API",
    description="REST API for massively multilingual text-to-speech synthesis supporting 7000+ languages",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "IMS-Toucan TTS API",
        "version": "0.1.0",
        "endpoints": {
            "/synthesize": "POST - Generate speech from text",
            "/health": "GET - Health check",
            "/languages": "GET - List supported languages",
            "/docs": "GET - OpenAPI documentation",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if _tts_instance is not None else "initializing",
        device=_device,
        model_loaded=_tts_instance is not None,
        version="0.1.0"
    )


@app.get("/languages", response_model=LanguagesResponse)
async def list_languages():
    """List supported languages."""
    return LanguagesResponse(
        count=7000,
        languages=["eng", "deu", "fra", "spa", "ita", "por", "rus", "jpn", "kor", "cmn", "..."],
        note="See full list at /docs or Utility/language_list.md"
    )


@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """
    Synthesize speech from text.

    Returns WAV audio file.

    Example:
        curl -X POST "http://localhost:8000/synthesize" \\
             -H "Content-Type: application/json" \\
             -d '{"text": "Hello world", "language": "eng"}' \\
             --output output.wav
    """
    try:
        tts = get_tts()

        # Change language if different from current
        if request.language != _default_language:
            logger.info(f"Changing language to: {request.language}")
            tts.set_language(request.language)

        # Handle voice cloning if reference provided
        if request.reference_audio:
            import base64
            audio_data = base64.b64decode(request.reference_audio)
            # Save temporarily and load
            temp_path = Path("/tmp/tts_reference.wav")
            temp_path.write_bytes(audio_data)
            tts.set_utterance_embedding(str(temp_path))
            temp_path.unlink()

        # Generate audio
        logger.info(f"Synthesizing: {request.text[:50]}...")

        # Use in-memory buffer instead of file
        output_buffer = io.BytesIO()

        # Generate audio to temporary file first
        temp_output = Path("/tmp/tts_output.wav")
        tts.read_to_file(
            text_list=[request.text],
            file_location=str(temp_output),
            duration_scaling_factor=1.0 / request.speed
        )

        # Read the file into buffer
        with open(temp_output, "rb") as f:
            output_buffer.write(f.read())

        temp_output.unlink()  # Clean up

        output_buffer.seek(0)

        return StreamingResponse(
            output_buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            }
        )

    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synthesize-with-reference")
async def synthesize_with_reference(
    text: str,
    language: str = "eng",
    reference: UploadFile = File(...),
    speed: float = 1.0
):
    """
    Synthesize speech with voice cloning from uploaded reference audio.

    Example:
        curl -X POST "http://localhost:8000/synthesize-with-reference" \\
             -F "text=Hello world" \\
             -F "language=eng" \\
             -F "reference=@voice.wav" \\
             --output output.wav
    """
    try:
        tts = get_tts()

        # Change language if different
        if language != _default_language:
            tts.set_language(language)

        # Load reference audio
        reference_path = Path(f"/tmp/tts_ref_{reference.filename}")
        with open(reference_path, "wb") as f:
            f.write(await reference.read())

        tts.set_utterance_embedding(str(reference_path))
        reference_path.unlink()

        # Generate audio
        temp_output = Path("/tmp/tts_output.wav")
        tts.read_to_file(
            text_list=[text],
            file_location=str(temp_output),
            duration_scaling_factor=1.0 / speed
        )

        # Read and return
        with open(temp_output, "rb") as f:
            audio_data = f.read()

        temp_output.unlink()

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=output.wav"}
        )

    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def serve(host: str = "0.0.0.0", port: int = 8000, device: str = "cpu", language: str = "eng"):
    """
    Start the TTS API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        device: Device to use (cpu or cuda)
        language: Default language
    """
    global _device, _default_language
    _device = device
    _default_language = language

    logger.info(f"Starting TTS API server on {host}:{port}")
    logger.info(f"Device: {device}, Default language: {language}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


def main():
    """CLI entry point for toucan-serve."""
    import argparse

    parser = argparse.ArgumentParser(
        description="IMS-Toucan TTS REST API Server"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to use (default: cpu)"
    )

    parser.add_argument(
        "--language", "-l",
        type=str,
        default="eng",
        help="Default language (default: eng)"
    )

    args = parser.parse_args()

    serve(
        host=args.host,
        port=args.port,
        device=args.device,
        language=args.language
    )


if __name__ == "__main__":
    main()
