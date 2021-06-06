import pytest 
import logging
import paramiko
import socket
from pathlib import Path
import glob, json
from serial.tools import list_ports

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function") 
def check_scp_put_tmp_after_setup(scp_put_tmp, configuration, ssh_command):
    LOGGER.info(f'received json data in check_scp_put_tmp_after_setup {configuration}')

    if 'path_dst' in configuration and 'path_src' in configuration:
        LOGGER.info(f"configuration path dst {configuration['path_dst']} and configuration path src {configuration['path_src']}")

        output, error = ssh_command(f"ls {configuration['path_dst']}")

        if error != "":
            LOGGER.info(f'File(s) not found in the directory')
            pytest.skip("Precondition checking prior test execution: Required file not found in the directory")

    else:
        pytest.skip("Precondition checking prior test execution: Path or source not specified")


def get_ssh_keyfile(configuration):
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

    return pkey, key_filename


def capabilitiy_lists(fixtures):
    """provide list of fixtures which use in tests
    """
    capability = ['ping', 'ssh_command', 'scp', 'th085', 'battery_disconnect', 'usbopto4out', 'ignition', 'ignition_off', 
                    'peaktech1885', 'serial_phycard']

    platforms = ['usbopto4out', 'ignition', 'ignition_off', 'th085', 'battery_disconnect', 'peaktech1885'] 

    return capability, platforms


def show_info_about_fixture(found_fixture):
    return LOGGER.info(f'Found {found_fixture} fixture')


def show_skipping_reasons(fixture):
    return (f'Precondition for checking {fixture} is not fulfilled')


def perform_preconditions(chosen_operation):
    """execute operation according to fixture
    """
    operations = {
        'ping': lambda: check_ping_capability(),
        'scp': lambda: check_scp_capability(),
        'ssh_command': lambda: check_ssh_capability(),
        'peaktech1885': lambda: check_peaktech1885_capability(),
        **dict.fromkeys(['th085', 'ignition', 'battery_disconnect'], lambda: check_th085_capability()),
        **dict.fromkeys(['usbopto4out', 'ignition', 'ignition_off', 'turned_on'], lambda: check_usboptocoupler_capability()),
    }

    return operations.get(chosen_operation)()


def filter_unexecutable_items(fixtures_require_preconditions, item):

    _, platforms = capabilitiy_lists(fixtures_require_preconditions)
    deselected_items = []
    for fix in fixtures_require_preconditions:
        show_info_about_fixture(fix)
        if fix not in platforms:
            value = perform_preconditions(chosen_operation=fix)
            if value is True:
                LOGGER.info(f'Successful {fix} the ticket box')
            else:
                LOGGER.info(f'Fail {fix} the ticket box')
                deselected_items.append(item)
                item.add_marker(pytest.mark.skip(reason=show_skipping_reasons(fix)))
        else:
            port = perform_preconditions(chosen_operation = fix)
            print(f'return port {port} with corresponding fixture {fix}')
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


def load_default_json_file():
    """read data from default.json for checking predefined platforms' values
    """
    json_files = list(Path('.').glob('**/default.json'))
    for jfile in json_files:
        jopen = open(jfile)
        jdata = json.load(jopen)
    
    return jdata
    

def check_usboptocoupler_capability():
    """check whether usboptocoupler port is in the environmnet 
    """
    comport = None
    configuration = load_default_json_file()
    if 'usbopto4out_comport' in configuration and configuration['usbopto4out_comport'] is not None:
        comport = configuration['usbopto4out_comport']
    else:
        ports = list_ports.comports()
        for port in ports:
            if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number == "12345678A":
                LOGGER.info(f"Usbopto4out found at {port.device}")
                comport = port.device
    print(f'usboptocoupler port {comport}')
    return comport


def check_th085_capability():
    """check whether th085 port is in the environmnet 
    """
    comport = None
    configuration = load_default_json_file()
    if 'th085_comport' in configuration and configuration['th085_comport'] is not None:
        comport = configuration['th085_comport']
        print(f'in if th085_comport statement {comport}')
    else:
        ports = list_ports.comports()
        for port in ports:
            if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number.startswith("SM"):
                LOGGER.info(f"TH085 found at {port.device}")
                comport = port.device

    print(f'th085 port {comport}')
    return comport


def check_peaktech1885_capability():
    """check whether peaktech1885 port is in the environmnet 
    """
    comport = None
    configuration = load_default_json_file()
    if 'peaktech1885_comport' in configuration and configuration['peaktech1885_comport'] is not None:
        comport = configuration['peaktech1885_comport']
    else:
        ports = list_ports.comports()
        for port in ports:
            if port.vid == "9999" and port.pid == "99999" and port.serial_number.startswith("XX"):
                LOGGER.info(f"Peaktech1885 found at {port.device}")
                comport = port.device

    print(f'peaktech port {comport}')
    return comport


def check_ping_capability():
    """
    function for checking ping connection
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            configuration = load_default_json_file()
            s.settimeout(5)
            s.connect((configuration["rhost"], configuration["ssh_port"]))
            s.shutdown(2)
            LOGGER.info(f"Pre_pinging success")
            return True
        except:
            LOGGER.info(f"Pre_pinging fail")
            return False

    
def check_ssh_capability():
    """
    function for ssh connection to check with ssh key
    """
    try:
        configuration = load_default_json_file()
        _, keyfile = get_ssh_keyfile(configuration)
        LOGGER.info(f'check ssh capability keyfile {keyfile}')
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(configuration["rhost"], port=configuration["ssh_port"], username=configuration["ssh_username"], allow_agent=True, key_filename=keyfile)
        ssh_client = True
    except:
        ssh_client = False

    LOGGER.info(f'return ssh_client value in check ssh capability {ssh_client}')
    return ssh_client
