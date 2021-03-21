import pytest
import logging
from scp import SCPClient

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.ssh",
]


@pytest.fixture(scope="module")
def scp(ssh):
    scp_wrapper = lambda: None
    scp_wrapper.put = lambda *args, **kwargs: put(ssh, *args, **kwargs)
    scp_wrapper.get = lambda *args, **kwargs: get(ssh, *args, **kwargs)
    return scp_wrapper

@pytest.fixture(scope="session")
def scp_default(ssh_default):
    scp_wrapper = lambda: None
    scp_wrapper.put = lambda *args, **kwargs: put(ssh_default, *args, **kwargs)
    scp_wrapper.get = lambda *args, **kwargs: get(ssh_default, *args, **kwargs)
    return scp_wrapper

def put(ssh_client, files, remote_path=b'.', recursive=False, preserve_times=False):
    assert ssh_client.check_health() == True, "No SSH Connection"
    LOGGER.info(f"SCP put: {files} > {remote_path}")
    with SCPClient(ssh_client.get_transport(), socket_timeout=60) as client:
        client.put(files, remote_path, recursive, preserve_times)

def get(ssh_client, remote_path, local_path='', recursive=False, preserve_times=False):
    assert ssh_client.check_health() == True, "No SSH Connection"
    LOGGER.info(f"SCP get: {local_path} < {remote_path}")
    with SCPClient(ssh_client.get_transport(), socket_timeout=60) as client:
        client.put(remote_path, local_path, recursive, preserve_times)