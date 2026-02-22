import logging
from datetime import datetime

logger = logging.getLogger("opencore.heartbeat")

class HeartbeatManager:
    def __init__(self):
        self.last_heartbeat = None
        self.status = "stopped"

    async def log_heartbeat(self):
        self.last_heartbeat = datetime.now()
        self.status = "running"
        logger.info(f"Heartbeat: System is operational. Last check: {self.last_heartbeat}")

    def get_status(self):
        return {
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }

heartbeat_manager = HeartbeatManager()
