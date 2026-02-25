import os
import tempfile
import logging
import asyncio
from typing import Optional
from starlette.datastructures import UploadFile
from opencore.audio.transcriber import transcribe_audio

logger = logging.getLogger("opencore.audio.service")

MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".webm", ".m4a", ".flac", ".mpga"}

class AudioServiceError(Exception):
    """Base exception for audio service errors."""
    pass

class AudioValidationError(AudioServiceError):
    """Raised when file validation fails (type, format, etc.)."""
    pass

class AudioSizeError(AudioServiceError):
    """Raised when file exceeds size limit."""
    pass

class AudioService:
    async def process_upload(self, file: UploadFile) -> str:
        """
        Validates, saves, and transcribes an uploaded audio file.

        Args:
            file: The UploadFile object from the request.

        Returns:
            The transcribed text.

        Raises:
            AudioValidationError: If the file type is invalid.
            AudioSizeError: If the file is too large.
            Exception: For other errors.
        """
        filename = file.filename or "audio.tmp"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise AudioValidationError(
                f"Invalid file type. Allowed extensions: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
            )

        tmp_path = None
        try:
            # Create a temporary file to save the upload
            # We read in chunks to avoid loading the entire file into memory and check size limit
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp_path = tmp.name
                total_size = 0
                CHUNK_SIZE = 1024 * 1024  # 1MB

                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > MAX_AUDIO_SIZE:
                        raise AudioSizeError(
                            f"File too large. Maximum size is {MAX_AUDIO_SIZE // (1024 * 1024)}MB."
                        )
                    tmp.write(chunk)

            # Run transcription in a threadpool to avoid blocking event loop
            # Using asyncio.to_thread for cleaner async execution (Python 3.9+)
            text = await asyncio.to_thread(transcribe_audio, tmp_path)
            return text

        except (AudioValidationError, AudioSizeError):
            raise
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise e
        finally:
            # Ensure cleanup happens even if exceptions occur
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file {tmp_path}: {cleanup_error}")
