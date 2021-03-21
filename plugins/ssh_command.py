import pytest
import logging

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.ssh",
]

@pytest.fixture(scope="module")
def ssh_command(ssh):
    return lambda *args, **kwargs: exec_command(ssh, *args, **kwargs)

@pytest.fixture(scope="session")
def ssh_command_default(ssh_default):
    return lambda *args, **kwargs: exec_command(ssh_default, *args, **kwargs)

def exec_command(client, command, encoding='utf-8', timeout=30):
    assert client.check_health() == True, "No SSH Connection"
    LOGGER.info(f"SSH command: {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode(encoding).strip("\n")
    LOGGER.info(f"SSH output: {output}")
    error = stderr.read().decode(encoding).strip("\n")
    LOGGER.info(f"SSH error: {error}")
    return output, error