import logging
import os

import py_eureka_client.eureka_client as eureka_client

logger = logging.getLogger(__name__)

_EUREKA_SERVER_URL = os.environ.get("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
_APP_NAME = "ai-service"
_INSTANCE_PORT = int(os.environ.get("AI_SERVICE_PORT", "8000"))


async def start_eureka_client() -> None:
    await eureka_client.init_async(
        eureka_server=_EUREKA_SERVER_URL,
        app_name=_APP_NAME,
        instance_port=_INSTANCE_PORT,
    )
    logger.info("Registered with Eureka as %s on port %s", _APP_NAME, _INSTANCE_PORT)


async def stop_eureka_client() -> None:
    await eureka_client.stop_async()
    logger.info("Deregistered from Eureka")
