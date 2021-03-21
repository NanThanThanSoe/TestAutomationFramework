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

@pytest.fixture(scope="session")
def ping_until():
    def rhost_port_is_open(ip, port, delay = 2, timeout = 300, count = 2):
        n = 0
        started_at = time.time()
        while time.time() - started_at < timeout:
            begin_at = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(delay)
                    s.connect((ip, int(port)))
                    s.shutdown(2)
                    LOGGER.info(f"Ping: Received {ip}:{port}")
                    n += 1
                    if n >= count:
                        return True
                except:
                    LOGGER.info(f"Ping: Lost {ip}:{port}")
                    n = 0
            delay_remaining = max(0, delay - (time.time() - begin_at))
            if time.time() + delay_remaining >= started_at + timeout:
                break
            time.sleep(delay_remaining)
        return False

    return rhost_port_is_open

@pytest.fixture(scope="session")
def ping_timeout():
    def rhost_port_is_open(ip, port, delay = 2, timeout = 300, count = 2):
        n = 0
        started_at = time.time()
        while time.time() - started_at < timeout:
            begin_at = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(delay)
                    s.connect((ip, int(port)))
                    s.shutdown(2)
                    LOGGER.info(f"The box still up")
                    n = 0
                except:
                    LOGGER.info(f"The box shut down")
                    n += 1
                    if n >= count:
                        return True
            delay_remaining = max(0, delay - (time.time() - begin_at))
            if time.time() + delay_remaining >= started_at + timeout:
                break
            time.sleep(delay_remaining)
        return False

    return rhost_port_is_open