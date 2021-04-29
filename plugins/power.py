import pytest
import logging

LOGGER = logging.getLogger(__name__)

pytest_plugins = [
    "plugins.configuration",
    "plugins.usbopto4out",
    "plugins.th085"
]


@pytest.fixture(scope="session")
def turned_on(request, configuration_default):
    if 'usbopto4out_output' not in configuration_default or configuration_default['usbopto4out_output'] is None:
        LOGGER.warn("Power Control is not available. Missing usbopto4out_output.")
        yield False
        return
    usbopto4out = request.getfixturevalue('usbopto4out_default')
    output = int(configuration_default["usbopto4out_output"])

    changed = False
    changed = power_set(usbopto4out, output, 1)

    yield changed

    if changed:
        changed = power_set(usbopto4out, output, 0)

@pytest.fixture(scope="function")
def battery_disconnect(request, configuration, th085):
    th085.write(port=3, pin=7, state=0)
    yield
    th085.write(port=3, pin=7, state=1)

@pytest.fixture(scope="function")
def ignition_off(request, configuration):
    iginition_set(request, 0, configuration['usbopto4out_output'])
    yield
    iginition_set(request, 1, configuration['usbopto4out_output'])

@pytest.fixture(scope="module")
def ignition(request, configuration):
    def _iginition(on):
        return iginition_set(request, on, configuration['usbopto4out_output'])

    yield _iginition

@pytest.fixture(scope="session")
def ignition_default(request, configuration_default):
    def _iginition(on):
        return iginition_set(request, on, configuration_default['usbopto4out_output'])

    yield _iginition

def iginition_set(request, on, usbopto4out_output):
    LOGGER.info(f"Switch ignition {'on' if on else 'off'}")
    try:
        usbopto4out = request.getfixturevalue("usbopto4out")
        power_set(usbopto4out, usbopto4out_output, 1 if on else 0)
    except:
        th085 = request.getfixturevalue("th085")
        th085.write(port=4, pin=7, state=1 if on else 0)

def power_set(usbopto4out, usbopto4out_output, state):
    usbopto4out.read()
    if usbopto4out.output & (1 << (usbopto4out_output - 1)) == state:
        # power state already matches
        return False
    else:
        LOGGER.info(f"OPTO: {'Activate' if state == 1 else 'Deactivate'} O{usbopto4out_output}")
        usbopto4out.iocontrol(f"{'set' if state == 1 else 'clr'}Out{usbopto4out_output}")
        usbopto4out.read()
        if usbopto4out.output & (1 << (usbopto4out_output - 1)) != state:
            LOGGER.error("Power Control Failure.")
        return True
