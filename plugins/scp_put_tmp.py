import pytest
import logging

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.configuration",
    "plugins.scp",
    "plugins.ssh_command",
]


@pytest.fixture(scope="module")
def scp_put_tmp(configuration, scp, ssh_command):
    upload(configuration, scp)
    yield
    remove(configuration, ssh_command)

@pytest.fixture(scope="session")
def scp_put_tmp_default(configuration_default, scp_default, ssh_command_default):
    upload(configuration_default, scp_default)
    yield
    remove(configuration_default, ssh_command_default)

def upload(configuration, scp):
    """
    This fixtrue copies the selected folder to the desired location for the execution of a test function and deletes it again when the function is finished.
    It is required to set the source (path_src) and destination (path_dst) path in the configuration file.
    """
    if 'path_src' not in configuration or configuration['path_src'] == "":
        pytest.skip("It is necessary to specify the source as path_src in the configuration")
    if 'path_dst' not in configuration or configuration['path_dst'] == "":
        pytest.skip("It is necessary to specify the destination as path_dst in the configuration")

    LOGGER.info(f"Upload {configuration['path_src']} to device")
    # _, _ = ssh_command(f"mkdir -p {configuration['path_dst']}") # Wenn man den Ordner erstellt verschiebt scp aus irgendeinem Grund das Ziel in den Unterordner
    LOGGER.info(f"SCP put: {configuration['path_src']} > {configuration['path_dst']}")
    scp.put(configuration['path_src'], recursive=True, remote_path=configuration['path_dst'])

def remove(configuration, ssh_command):
    LOGGER.info(f"Remove {configuration['path_dst']} from device")
    _, _ = ssh_command(f"rm -R {configuration['path_dst']}")