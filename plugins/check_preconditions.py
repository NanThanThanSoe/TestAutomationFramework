import pytest 
import logging
import paramiko
from pathlib import Path
from tcping import Ping
import glob, json, re
from serial.tools import list_ports

LOGGER = logging.getLogger(__name__)

  
def pytest_collection_modifyitems(session, config, items):

    fixtures = list(set([fixture for item in items for fixture in item.fixturenames]))
    scope, _ = capabilitiy_lists(fixtures)
    selected_items = []
    deselected_items = []
    for item in items:
        fixtures_require_preconditions = [operation for operation in item.fixturenames if operation in scope]
        deselect_items = filter_deselected_items(fixtures_require_preconditions, item)
        deselected_items.append(deselect_items)

    deselected_lst = filter_empty_lists(deselected_items)
    LOGGER.info(f'Deselected items {deselected_lst}')
    config.hook.pytest_deselected(items=deselected_lst)


def capabilitiy_lists(fixtures):
    """provide list of fixtures which use in tests
    """
    capability = ['ping', 'ssh_command', 'scp', 'scp_put_tmp', 'th085', 'battery_disconnect', 'usbopto4out', 'ignition', 'ignition_off', 
                    'turned_on', 'peaktech1885', 'serial_phycard']

    platforms = ['usbopto4out', 'ignition', 'ignition_off', 'turned_on', 'th085', 'battery_disconnect', 'peaktech1885'] 

    return capability, platforms


def show_info_about_fixture(found_fixture):
    return LOGGER.info(f'Found {found_fixture} fixture')


def show_skipping_reasons(fixture):
    return (f'Precondition for checking {fixture} is not fulfilled')


def perform_preconditions(chosen_operation):
    """execute operation according to fixture
    """
    operations = {
        'ping': check_ping_capability(),
        'scp': check_scp_capability(),
        'ssh_command': check_ssh_capability(),
        'peaktech1885': check_peaktech1885_capability(),
        ('th085', 'ignition', 'battery_disconnect'): check_th085_capability(),
        ('usbopto4out', 'ignition', 'ignition_off', 'turned_on'): check_usboptocoupler_capability(),
    }

    return operations.get(chosen_operation)


def filter_deselected_items(fixtures_require_preconditions, item):

    _, platforms = capabilitiy_lists(fixtures_require_preconditions)
    deselected_items = []
    for fix in fixtures_require_preconditions:
        show_info_about_fixture(fix)
        if fix not in platforms:
            try:
                perform_preconditions(chosen_operation=fix)
                LOGGER.info(f'Successful {fix} the ticket box')
            except:
                LOGGER.info(f'Fail {fix} the ticket box')
                deselected_items.append(item)
                item.add_marker(pytest.mark.skip(reason=show_skipping_reasons(fix)))
        else:
            port = perform_preconditions(chosen_operation = fix)
            if port is not None:
                LOGGER.info(f'Found the {fix} in the environment')
            else:
                LOGGER.info(f'Could not find the {fix} in the environment')
                deselected_items.append(item)
                item.add_marker(pytest.mark.skip(reason=show_skipping_reasons(fix)))

    return deselected_items


def filter_empty_lists(item_list):
    """remove empty list from list
    """
    return list(filter(lambda item: item, item_list))


def check_scp_capability():
    """scp uses the ssh connection. So in general, if the ssh connection is active scp should work as well
    """
    scp = check_ssh_capability()
        
    return scp

def check_usboptocoupler_capability():
    """check whether usboptocoupler port is in the environmnet 
    """
    comport = None
    ports = list_ports.comports()
    for port in ports:
        if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number == "12345678A":
            LOGGER.info(f"Usbopto4out found at {port.device}")
            comport = port.device

    return comport


def check_th085_capability():
    """check whether th085 port is in the environmnet 
    """
    comport = None
    ports = list_ports.comports()
    for port in ports:
        if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number.startswith("SM"):
            LOGGER.info(f"TH085 found at {port.device}")
            comport = port.device

    return comport


def check_peaktech1885_capability():
    """check whether peaktech1885 port is in the environmnet 
    """
    comport = None
    ports = list_ports.comports()
    for port in ports:
        if port.vid == "9999" and port.pid == "99999" and port.serial_number.startswith("XX"):
            LOGGER.info(f"Peaktech1885 found at {port.device}")
            comport = port.device

    return comport


def check_ping_capability():
    """
    function for checking ping connection
    """
    ip = '10.13.201.18'
    port = 22
    rhost_is_up = Ping(ip, port)
    
    return rhost_is_up

    
def check_ssh_capability():
    """
    function for ssh connection to check with ssh key
    """
    ssh_client = False
    while ssh_client:
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            keyfile = f"{str(Path.home())}/.ssh/id_root_rsa"
            ssh_client.connect('10.13.201.18', port=22, username="root", allow_agent=True, key_filename=keyfile)
            ssh_client = True
            return ssh_client
        except:
            ssh_client = False
            continue


    
