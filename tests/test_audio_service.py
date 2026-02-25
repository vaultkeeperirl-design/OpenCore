import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
from starlette.datastructures import UploadFile
from opencore.audio.service import AudioService, AudioValidationError, AudioSizeError

class TestAudioService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.service = AudioService()

    @patch("opencore.audio.service.transcribe_audio")
    async def test_process_upload_success(self, mock_transcribe):
        mock_transcribe.return_value = "Success"

        # Mock UploadFile
        content = b"fake audio content"
        file = MagicMock(spec=UploadFile)
        file.filename = "test.wav"

        # Mock async read
        async def mock_read(size=-1):
            if not hasattr(mock_read, 'called'):
                mock_read.called = True
                return content
            return b""

        file.read = mock_read

        result = await self.service.process_upload(file)

        self.assertEqual(result, "Success")
        mock_transcribe.assert_called_once()

    async def test_process_upload_invalid_extension(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.txt"

        with self.assertRaises(AudioValidationError):
            await self.service.process_upload(file)

    async def test_process_upload_too_large(self):
        # Patch MAX_AUDIO_SIZE within the test context
        with patch("opencore.audio.service.MAX_AUDIO_SIZE", 10):
            file = MagicMock(spec=UploadFile)
            file.filename = "test.wav"

            # Mock async read that returns more than 10 bytes
            async def mock_read(size=-1):
                if not hasattr(mock_read, 'called'):
                    mock_read.called = True
                    return b"12345678901" # 11 bytes
                return b""

            file.read = mock_read

            with self.assertRaises(AudioSizeError):
                await self.service.process_upload(file)
