import pytest
import logging
from serial.tools import list_ports
from src.lib.th085 import TH085

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.configuration",
]


@pytest.fixture(scope="module")
def th085(configuration):
    th085 = th085_open(configuration)
    yield th085
    th085_close(th085)

@pytest.fixture(scope="session")
def th085_default(configuration_default):
    th085 = th085_open(configuration_default)
    yield th085
    th085_close(th085)

def th085_open(configuration):
    comport = None
    
    if 'th085_comport' in configuration and configuration['th085_comport'] is not None:
        comport = configuration['th085_comport']
    else:
        LOGGER.info("Searching TH085 com port")
        ports = list_ports.comports()

        for port in ports:
            if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number.startswith("SM"):
                LOGGER.info(f"TH085 found at {port.device}")
                comport = port.device

    if comport is None:
        pytest.skip("The comport for the TH085 module was not specified and could not be determined automatically")
    
    LOGGER.info(f"Open TH085 connection using port {comport}")
    th085 = TH085(comport)
    th085.openCom()
    LOGGER.info(f"TH085 COM Port: {th085.comport}")
    if th085.comport != comport:
        pytest.skip("Failed to open TH085 connection")

    init_val = th085.initModul()
    LOGGER.info(f"TH085 Mode:    {init_val}")
    if init_val != 0:
        LOGGER.error("Failed to turn off TH085 debug mode")

    return th085

def th085_close(th085):
    LOGGER.info(f"Close TH085 connection using port {th085.comport}")
    th085.closeCom()
    LOGGER.info(f"TH085 COM Port: {th085.comport}")
    if th085.comport != -1:
        LOGGER.error("Failed to close TH085 connection")
