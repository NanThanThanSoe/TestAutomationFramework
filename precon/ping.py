import pytest
import logging
import socket
import time

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
]

@pytest.fixture(scope="session")
def ping():
    def open_rhost_port(ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)
                s.connect((ip, int(port)))
                s.shutdown(2)
                LOGGER.info(f"Ping: Received {ip}:{port}")
                return True
            except:
                LOGGER.info(f"Ping: Lost {ip}:{port}")
                return False
    return open_rhost_port
