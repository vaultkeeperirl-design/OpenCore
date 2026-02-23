import unittest
import logging
import json
import sys
from unittest.mock import patch
from opencore.core.logging import configure_logging, JSONFormatter


class TestLogging(unittest.TestCase):
    def setUp(self):
        # Reset logging configuration before each test
        logging.getLogger().handlers = []

    @patch("opencore.core.logging.settings")
    def test_production_logging(self, mock_settings):
        # Mock settings to simulate production
        mock_settings.app_env = "production"
        mock_settings.log_level = "INFO"

        configure_logging()

        root_logger = logging.getLogger()
        self.assertTrue(len(root_logger.handlers) > 0)

        # Check if the handler uses JSONFormatter
        handler = root_logger.handlers[0]
        self.assertIsInstance(handler.formatter, JSONFormatter)

        # Test formatting logic
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        formatted = handler.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test_logger")
        self.assertTrue("timestamp" in log_data)

    @patch("opencore.core.logging.settings")
    def test_development_logging(self, mock_settings):
        # Mock settings to simulate development
        mock_settings.app_env = "development"
        mock_settings.log_level = "DEBUG"

        configure_logging()

        root_logger = logging.getLogger()
        self.assertTrue(len(root_logger.handlers) > 0)

        # Check if the handler uses standard Formatter, not JSONFormatter
        handler = root_logger.handlers[0]
        self.assertNotIsInstance(handler.formatter, JSONFormatter)
        self.assertIsInstance(handler.formatter, logging.Formatter)

    def test_json_formatter_exception(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("Test Error")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname=__file__,
            lineno=20,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        self.assertTrue("exception" in log_data)
        self.assertIn("ValueError: Test Error", log_data["exception"])

    def test_extra_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=30,
            msg="User action",
            args=(),
            exc_info=None
        )
        # Manually add extra fields as if passed via extra={}
        record.request_id = "req-123"
        record.user_id = "user-456"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        self.assertEqual(log_data.get("request_id"), "req-123")
        self.assertEqual(log_data.get("user_id"), "user-456")


if __name__ == "__main__":
    unittest.main()
