import asyncio
import logging
from typing import Callable, Coroutine, Dict, Any, Optional

logger = logging.getLogger("opencore.scheduler")

class AsyncScheduler:
    """
    A simple asynchronous scheduler for running periodic tasks.
    """
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def add_job(self, func: Callable[[], Coroutine], interval: float, job_id: str):
        """
        Adds a job to be run periodically.

        :param func: An async function to be executed.
        :param interval: Interval in seconds.
        :param job_id: Unique identifier for the job.
        """
        if job_id in self._jobs:
            logger.warning(f"Job {job_id} already exists. Overwriting.")
            if job_id in self.tasks:
                self.tasks[job_id].cancel()

        self._jobs[job_id] = {
            "func": func,
            "interval": interval
        }

        if self.running:
            self._start_job(job_id)

    def _start_job(self, job_id: str):
        job = self._jobs.get(job_id)
        if not job:
            return

        async def loop():
            # Run immediately on start
            try:
                await job["func"]()
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error(f"Error in job {job_id} (initial): {e}")

            while True:
                try:
                    await asyncio.sleep(job["interval"])
                    await job["func"]()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in job {job_id}: {e}")

        self.tasks[job_id] = asyncio.create_task(loop())
        logger.info(f"Started job: {job_id} (interval: {job['interval']}s)")

    def start(self):
        """Starts all registered jobs."""
        if self.running:
            return

        self.running = True
        logger.info("Starting scheduler...")
        for job_id in self._jobs:
            self._start_job(job_id)

    def stop(self):
        """Stops all running jobs."""
        if not self.running:
            return

        logger.info("Stopping scheduler...")
        for job_id, task in self.tasks.items():
            task.cancel()

        self.tasks.clear()
        self.running = False
