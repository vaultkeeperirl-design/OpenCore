import uvicorn
from opencore.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "opencore.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_dev
    )
