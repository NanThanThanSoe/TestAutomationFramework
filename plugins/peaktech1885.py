import pytest
import logging
from serial.tools import list_ports
from src.lib.peaktech1885 import Peaktech1885

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.configuration",
]


@pytest.fixture(scope="module")
def peaktech1885(configuration):
    peaktech1885 = peaktech1885_open(configuration)
    yield peaktech1885
    peaktech1885_close(peaktech1885)

@pytest.fixture(scope="session")
def peaktech1885_default(configuration_default):
    peaktech1885 = peaktech1885_open(configuration_default)
    yield peaktech1885
    peaktech1885_close(peaktech1885)

def peaktech1885_open(configuration):
    comport = None
    
    if 'peaktech1885_comport' in configuration and configuration['peaktech1885_comport'] is not None:
        comport = configuration['peaktech1885_comport']
    else:
        LOGGER.info("Searching Peaktech1885 com port")
        ports = list_ports.comports()

        for port in ports:
            if port.vid == "9999" and port.pid == "99999" and port.serial_number.startswith("XX"):
                LOGGER.info(f"Peaktech1885 found at {port.device}")
                comport = port.device

    if comport is None:
        pytest.skip("The comport for the Peaktech1885 module was not specified and could not be determined automatically")
    
    LOGGER.info(f"Open Peaktech1885 connection using port {comport}")
    peaktech1885 = Peaktech1885(comport)
    peaktech1885.openCom()
    LOGGER.info(f"Peaktech1885 COM Port: {peaktech1885.comport}")
    if peaktech1885.comport != comport:
        pytest.skip("Failed to open Peaktech1885 connection")

    peaktech1885.init()

    return peaktech1885

def peaktech1885_close(peaktech1885):
    LOGGER.info(f"Close Peaktech1885 connection using port {peaktech1885.comport}")
    peaktech1885.closeCom()
    LOGGER.info(f"Peaktech1885 COM Port: {peaktech1885.comport}")
    if peaktech1885.comport != -1:
        LOGGER.error("Failed to close Peaktech1885 connection")
