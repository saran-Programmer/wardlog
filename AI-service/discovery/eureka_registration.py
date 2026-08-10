import logging
import os
import socket

import py_eureka_client.eureka_client as eureka_client

logger = logging.getLogger(__name__)

_EUREKA_SERVER_URL = os.environ.get("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
_APP_NAME = "ai-service"
_INSTANCE_PORT = int(os.environ.get("AI_SERVICE_PORT", "8000"))


def get_private_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


async def start_eureka_client() -> None:
    instance_ip = get_private_ip()
    await eureka_client.init_async(
        eureka_server=_EUREKA_SERVER_URL,
        app_name=_APP_NAME,
        instance_port=_INSTANCE_PORT,
        instance_ip=instance_ip,
        instance_host=instance_ip,
    )
    logger.info("Registered with Eureka as %s at %s on port %s", _APP_NAME, instance_ip, _INSTANCE_PORT)


async def stop_eureka_client() -> None:
    await eureka_client.stop_async()
    logger.info("Deregistered from Eureka")