import os
import logging
from typing import Optional

logger = logging.getLogger("opencore.audio")

_WHISPER_MODEL = None

def get_whisper_model(model_name: str = "base"):
    """
    Lazy loads the Whisper model.
    """
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import whisper
            logger.info(f"Loading Whisper model: {model_name}")
            _WHISPER_MODEL = whisper.load_model(model_name)
        except ImportError:
            logger.error("Whisper library not found. Please install openai-whisper.")
            raise ImportError("openai-whisper is required for audio transcription.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise e
    return _WHISPER_MODEL

def transcribe_audio(file_path: str, model_name: str = "base") -> str:
    """
    Transcribes audio from a file path using OpenAI Whisper.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        model = get_whisper_model(model_name)
        result = model.transcribe(file_path)
        return result["text"].strip()
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise e
