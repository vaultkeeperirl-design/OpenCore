import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from opencore.interface.api import run_proactive_heartbeat, scheduler, lifespan, app

class TestHeartbeatScheduler(unittest.TestCase):

    @patch('opencore.interface.api.swarm')
    @patch('opencore.interface.api.heartbeat_manager')
    def test_proactive_heartbeat_calls_chat(self, mock_heartbeat_manager, mock_swarm):
        # Setup mocks
        mock_heartbeat_manager.log_heartbeat = AsyncMock()
        mock_swarm.chat = MagicMock(return_value="Acknowledged.")

        # Run the async function
        asyncio.run(run_proactive_heartbeat())

        # Verify heartbeat logged
        mock_heartbeat_manager.log_heartbeat.assert_called_once()

        # Verify swarm chat called with expected system prompt
        mock_swarm.chat.assert_called_once()
        args, _ = mock_swarm.chat.call_args
        self.assertIn("SYSTEM HEARTBEAT", args[0])

    def test_scheduler_registration(self):
        # Run lifespan context
        async def run_lifespan():
            async with lifespan(app):
                # Check if job is registered
                self.assertIn("system_heartbeat", scheduler._jobs)
                job = scheduler._jobs["system_heartbeat"]
                self.assertEqual(job["interval"], 3600)
                self.assertEqual(job["func"], run_proactive_heartbeat)

        asyncio.run(run_lifespan())

if __name__ == "__main__":
    unittest.main()
