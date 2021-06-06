#!/usr/bin/env python3

# This has to be at the top to allow the script to be run standalone
if __name__ == "__main__":
    import sys
    import pytest
    pytest.main(sys.argv)

import pytest
import sys
from os import urandom

from serialtestutil.serialtester import rs232_fixture  # noqa: F401

# The bounce test uses 80-byte payloads,
# sent back and forth for 10 seconds
bounce_data = urandom(80)
bounce_duration = 10


class Test_RS232_Endurance:
    """Runs endurance tests on the RS-232 port."""

    # We do not do the bounce test on all data lengths,
    # it takes way too long
    def test_bounce(self, rs232_fixture):  # noqa: F811
        # If the data bits are smaller than 8, crop/mask the test data accordingly
        data = rs232_fixture.crop_data(bounce_data)
        rs232_fixture.bounce_data(data, duration=bounce_duration)
