import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys

# Mock whisper module globally before it is imported anywhere
mock_whisper = MagicMock()
sys.modules["whisper"] = mock_whisper

from fastapi.testclient import TestClient
from opencore.interface.api import app
from opencore.audio.transcriber import transcribe_audio, get_whisper_model, _WHISPER_MODEL

class TestAudioTranscription(unittest.TestCase):

    def setUp(self):
        # Reset the global model variable to force reload if needed
        import opencore.audio.transcriber
        opencore.audio.transcriber._WHISPER_MODEL = None

    def test_transcribe_audio_success(self):
        # Setup mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello world"}
        mock_whisper.load_model.return_value = mock_model

        # Create a dummy file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"audio data")
            tmp_path = tmp.name

        try:
            text = transcribe_audio(tmp_path)
            self.assertEqual(text, "Hello world")
            mock_whisper.load_model.assert_called_with("base")
            mock_model.transcribe.assert_called_with(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_transcribe_audio_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            transcribe_audio("non_existent_file.wav")

class TestTranscribeEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("opencore.interface.api.transcribe_audio")
    def test_transcribe_endpoint_success(self, mock_transcribe):
        mock_transcribe.return_value = "Test transcription"

        # Simulate file upload
        files = {"file": ("test.webm", b"dummy audio content", "audio/webm")}
        response = self.client.post("/transcribe", files=files)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"text": "Test transcription"})

        # Verify mock was called
        mock_transcribe.assert_called_once()

    @patch("opencore.interface.api.transcribe_audio")
    def test_transcribe_endpoint_error(self, mock_transcribe):
        mock_transcribe.side_effect = Exception("Transcription error")

        files = {"file": ("test.webm", b"dummy audio content", "audio/webm")}
        response = self.client.post("/transcribe", files=files)

        # Expect 200 OK but with generic error message to prevent leakage
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"error": "Transcription failed due to an internal error.", "text": ""})

    def test_transcribe_endpoint_invalid_extension(self):
        files = {"file": ("test.txt", b"dummy content", "text/plain")}
        response = self.client.post("/transcribe", files=files)

        # Expect 200 OK with error message (API contract)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid file type", response.json()["error"])

    def test_transcribe_endpoint_too_large(self):
        # We mock the constant in the api module for the test context.
        with patch("opencore.interface.api.MAX_AUDIO_SIZE", 10): # Set limit to 10 bytes
             files = {"file": ("test.webm", b"this is definitely more than 10 bytes", "audio/webm")}
             response = self.client.post("/transcribe", files=files)

             # Expect 200 OK with error message (API contract)
             self.assertEqual(response.status_code, 200)
             self.assertIn("File too large", response.json()["error"])
