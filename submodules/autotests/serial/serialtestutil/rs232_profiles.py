import serial
from itertools import product
from operator import itemgetter

# Test profile: full
_fullprofile = {
    "description": "Full test. All supported setting combinations.",
    "baudrates": [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400],
    "dataBits": [serial.EIGHTBITS, serial.SEVENBITS],  # six and five bytes do not work at all
    "parities": serial.PARITY_NAMES.keys(),
    "stopBits": [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]
}

# Test profile: spec (only the combinations in the official spec)
_specprofile = {
    "description": "Officially supported settings as listed in 'UART2 - RS232 Architektur IVU.box'.",
    "baudrates": [9600, 38400, 57600, 115200, 230400],
    "dataBits": [serial.EIGHTBITS],
    "parities": [serial.PARITY_NONE],
    "stopBits": [serial.STOPBITS_ONE]
}

# Test profile: abnahme (configurations used in SpecAbnahmetest_WinCE6.0_7.0)
_abnahmeprofile = {
    "description": "Test settings as listed in 'IVU.box.familie Testspezifikation Abnahmetest'.",
    "baudrates": [1200, 9600, 19200, 57600, 115200],
    "dataBits": [serial.EIGHTBITS],
    "parities": [serial.PARITY_NONE],
    "stopBits": [serial.STOPBITS_ONE]
}

# Test profile: common (most common combinations with fast bitrates)
_commonprofile = {
    "description": "Common setting combinations with fast bitrates.",
    "baudrates": [19200, 57600, 115200, 230400],
    "dataBits": [serial.EIGHTBITS, serial.SEVENBITS],
    "parities": [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD],
    "stopBits": [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
}

# Test profile: quick (115200,8,N,1)
_quickprofile = {
    "description": "Quick test. 115200 Baud, 8 data bits, no parity, 1 stop bit.",
    "baudrates": [115200],
    "dataBits": [serial.EIGHTBITS],
    "parities": [serial.PARITY_NONE],
    "stopBits": [serial.STOPBITS_ONE]
}

_profiles = {
    "quick": _quickprofile,
    "abnahme": _abnahmeprofile,
    "common": _commonprofile,
    "spec": _specprofile,
    "full": _fullprofile
}

DEFAULT_PROFILE_NAME = "common"

_selectedprofile = _profiles[DEFAULT_PROFILE_NAME]


def get_available_profiles():
    """Returns the names of all available profiles."""
    return _profiles.keys()


def get_selected_profile():
    """Returns the selected profile."""
    return _selectedprofile


def get_selected_port_configurations():
    """Returns all RS232 port configurations for the selected profile as the cartesian product of all port parameters."""
    return product(*itemgetter("baudrates", "dataBits", "parities", "stopBits")(_selectedprofile))


def set_selected_profile(profilename):
    """Sets the selected profile. Used in conftest.py."""
    global _selectedprofile

    try:
        _selectedprofile = _profiles[profilename]
    except KeyError:
        raise ValueError("invalid profile name:", profilename)

