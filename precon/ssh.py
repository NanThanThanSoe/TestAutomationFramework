import pytest
import logging
import paramiko
from pathlib import Path

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "precon.configuration",
]


@pytest.fixture(scope="module")
def ssh(configuration):
    client = ssh_open(configuration)
    yield client
    ssh_close(client)

@pytest.fixture(scope="session")
def ssh_default(configuration_default):
    client = ssh_open(configuration_default)
    yield client
    ssh_close(client)

def ssh_open(configuration):
    LOGGER.info("Initialize SSH connection")
    client = paramiko.SSHClient()
    connect(client, configuration)

    client.check_health = lambda: reconnect(client, configuration)

    return client

def ssh_close(ssh):
    ssh.close()
    LOGGER.info("SSH connection disconnected")

def check_health(client):
    LOGGER.info("SSH connection health check")
    if client.get_transport() is None:
        LOGGER.info("No SSH connection")
        return False
    if not client.get_transport().is_active():
        LOGGER.info("SSH connection terminated")
        return False
    LOGGER.info("SSH connection is active")
    return True

def reconnect(client, configuration):
    if check_health(client):
        return True
    
    LOGGER.info("Reconnect SSH")
    connect(client, configuration)
    return check_health(client)

def connect(client, configuration):
    try:
        pkey = None
        key_filename = None
        if 'ssh_key' in configuration and configuration['ssh_key'] != "":
            key_filename = configuration['ssh_key']
        else:
            key_filename = f"{str(Path.home())}/.ssh/id_{configuration['ssh_username']}_rsa"
        
        key_password = None
        if 'ssh_key_password' in configuration and configuration['ssh_key_password'] != "":
            key_password = configuration['ssh_key_password']
        
        key_file = Path(key_filename)
        if key_file.is_file():
            pkey = paramiko.RSAKey.from_private_key_file(key_filename, key_password)
        
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            configuration["rhost"],
            port=configuration["ssh_port"],
            username=configuration["ssh_username"],
            password=configuration["ssh_password"],
            pkey=pkey,
            timeout=configuration["ssh_timeout"],
            look_for_keys=False,
            allow_agent=False
        )
        LOGGER.info("SSH connection established")
    except Exception as err:
        LOGGER.error(f"Failed to establish SSH connection: {err}")