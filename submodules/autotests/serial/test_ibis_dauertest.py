#!/usr/bin/env python3

# This has to be at the top to allow the script to be run standalone
if __name__ == "__main__":
    import sys
    import pytest
    pytest.main(sys.argv)

import pytest
import sys
from os import urandom

from serialtestutil.serialtester import ibis_loopback, active_ibis_master_loopback  # noqa: F401
from serialtestutil import ibis_config


class Test_IBIS_Endurance:
    """Runs endurance tests on the IBIS ports."""

    # The bounce test uses 20-byte payloads,
    # sent back and forth for as many cycles as the configuration
    # requires
    bounce_data = urandom(20)

    # We do not do the bounce test on all data lengths,
    # it takes way too long
    def test_bounce(self, active_ibis_master_loopback, pytestconfig):  # noqa: F811
        # If the data bits are smaller than 8, crop/mask the test data accordingly
        data = active_ibis_master_loopback.crop_data(self.bounce_data)
        active_ibis_master_loopback.bounce_data(data, cycles=ibis_config.endurance_cycle_count)
