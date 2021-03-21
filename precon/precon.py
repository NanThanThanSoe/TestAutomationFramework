import pytest 
import logging
import paramiko
from pathlib import Path
import glob

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    'plugins.ping',
    'plugins.configuration'
]

#check ping
def test_check_ping(ping, configuration):
    rhost_is_up = ping(configuration["rhost"], configuration["ssh_port"])
    assert rhost_is_up, "The system is offline"
    
#check ssh
def test_check_ssh(configuration):
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
        
    client = paramiko.SSHClient()
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

    assert client, "Failed to establish SSH connection"

#check scp file
def test_check_scp_file(configuration):
    fw_bin_file = glob.glob(f"{configuration['fw_bin_source']}/{configuration['fw_bin_version']}/*.bin")
    assert len(fw_bin_file) == 1, "FW binary file not found"
     

#check optocoupler
#check th085
#check peaktech1885

