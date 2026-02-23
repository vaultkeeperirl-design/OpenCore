import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from opencore.interface.heartbeat import HeartbeatManager

class TestHeartbeatManager(unittest.TestCase):
    def setUp(self):
        self.manager = HeartbeatManager()

    def test_start_time_set_on_init(self):
        self.assertIsNotNone(self.manager.start_time)
        self.assertIsInstance(self.manager.start_time, datetime)

    def test_get_status_includes_uptime(self):
        # Initial check
        status = self.manager.get_status()
        self.assertIn("uptime", status)
        self.assertIsNotNone(status["uptime"])

    @patch('opencore.interface.heartbeat.datetime')
    def test_uptime_calculation(self, mock_datetime):
        # Set a fixed start time
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        self.manager.start_time = start_time

        # Mock now() to be 1 hour later
        mock_datetime.now.return_value = datetime(2023, 1, 1, 11, 0, 0)

        status = self.manager.get_status()
        self.assertEqual(status["uptime"], "1:00:00")

        # Mock now() to be 1 hour, 30 mins, 45 secs later
        mock_datetime.now.return_value = datetime(2023, 1, 1, 11, 30, 45)

        status = self.manager.get_status()
        self.assertEqual(status["uptime"], "1:30:45")

    def test_status_update_on_log_heartbeat(self):
        # Initially stopped
        self.assertEqual(self.manager.status, "stopped")
        self.assertIsNone(self.manager.last_heartbeat)

        # Log heartbeat
        import asyncio
        asyncio.run(self.manager.log_heartbeat())

        self.assertEqual(self.manager.status, "running")
        self.assertIsNotNone(self.manager.last_heartbeat)

if __name__ == "__main__":
    unittest.main()
