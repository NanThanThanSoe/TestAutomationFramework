import pytest
import logging
from serial.tools import list_ports
from src.lib.usbopto4out import Usbopto4out

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.configuration",
]


@pytest.fixture(scope="module")
def usbopto4out(configuration):
    usbopto4out = usbopto4out_open(configuration)
    yield usbopto4out
    usbopto4out_close(usbopto4out)


@pytest.fixture(scope="session")
def usbopto4out_default(configuration_default):
    usbopto4out = usbopto4out_open(configuration_default)
    yield usbopto4out
    usbopto4out_close(usbopto4out)


def usbopto4out_open(configuration):
    comport = None

    if 'usbopto4out_comport' in configuration and configuration['usbopto4out_comport'] is not None:
        comport = configuration['usbopto4out_comport']
    else:
        LOGGER.info("Searching Usbopto4out com port")
        ports = list_ports.comports()

        for port in ports:
            if str(port.vid) == "1027" and str(port.pid) == "24577" and port.serial_number == "12345678A":
                LOGGER.info(f"Usbopto4out found at {port.device}")
                comport = port.device

    if comport is None:
        pytest.skip("The comport for the Usbopto4out module was not specified and could not be determined automatically")

    LOGGER.info(f"Open Usbopto4out connection using port {comport}")
    usbopto4out = Usbopto4out(comport)
    usbopto4out.open()
    usbopto4out.init()
    usbopto4out.read()

    return usbopto4out


def usbopto4out_close(usbopto4out):
    LOGGER.info(f"Close Usbopto4out connection using port {usbopto4out.comport}")
    usbopto4out.close()
