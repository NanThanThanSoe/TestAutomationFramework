import pytest
import logging

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "precon.ssh",
]

@pytest.fixture
def ssh_command(ssh):
    def ssh_command(command):
        ssh.check_health()
        LOGGER.info(f"SSH command: {command}")
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        LOGGER.info(f"SSH output: {output}")
        error = stderr.read().decode('utf-8')
        LOGGER.info(f"SSH error: {error}")
        return output, error

    return ssh_command