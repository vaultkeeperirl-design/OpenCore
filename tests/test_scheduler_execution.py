import unittest
import asyncio
from unittest.mock import AsyncMock
from opencore.core.scheduler import AsyncScheduler

class TestSchedulerExecution(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.scheduler = AsyncScheduler()

    async def asyncTearDown(self):
        self.scheduler.stop()

    async def test_job_execution(self):
        # Setup
        mock_job = AsyncMock()
        self.scheduler.add_job(mock_job, 0.1, "test_job")

        # Start
        self.scheduler.start()

        # Wait for initial run + 1 interval
        await asyncio.sleep(0.15)

        # Verify
        # Should be called at least twice (initial + 1 interval)
        self.assertGreaterEqual(mock_job.call_count, 2)

    async def test_job_failure_logging(self):
        # Setup
        mock_job = AsyncMock(side_effect=Exception("Test Error"))
        self.scheduler.add_job(mock_job, 0.1, "failing_job")

        with self.assertLogs("opencore.scheduler", level="ERROR") as cm:
            self.scheduler.start()
            await asyncio.sleep(0.05) # Allow initial run

        # Verify initial failure log
        self.assertTrue(any("Error in job failing_job (initial): Test Error" in log for log in cm.output))

        # Wait for next failure
        with self.assertLogs("opencore.scheduler", level="ERROR") as cm:
            await asyncio.sleep(0.15)

        # Verify subsequent failure log
        self.assertTrue(any("Error in job failing_job: Test Error" in log for log in cm.output))

if __name__ == "__main__":
    unittest.main()
