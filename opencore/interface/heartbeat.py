import logging
from datetime import datetime
from opencore import __version__

logger = logging.getLogger("opencore.heartbeat")

class HeartbeatManager:
    def __init__(self):
        self.start_time = datetime.now()
        self.last_heartbeat = None
        self.status = "stopped"

    async def log_heartbeat(self):
        self.last_heartbeat = datetime.now()
        self.status = "running"
        logger.info(f"Heartbeat: System is operational. Last check: {self.last_heartbeat}")

    def get_status(self):
        uptime_str = "00:00:00"
        if self.start_time:
             delta = datetime.now() - self.start_time
             # Format delta
             uptime_str = str(delta).split('.')[0] # remove microseconds

        return {
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "uptime": uptime_str,
            "version": __version__,
            "start_time": self.start_time.isoformat()
        }

heartbeat_manager = HeartbeatManager()
