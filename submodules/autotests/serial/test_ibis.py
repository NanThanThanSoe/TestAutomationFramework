#!/usr/bin/env python3

# This has to be at the top to allow the script to be run standalone
if __name__ == "__main__":
    import sys
    import pytest
    pytest.main(sys.argv)

import pytest
import time
import sys
from os import urandom

from serialtestutil.serialtester import ibis_loopback, active_ibis_master_loopback  # noqa: F401
from serialtestutil import ibis_config

# XXX pytest.IBIS_MAX_DATA_SIZE is defined dynamically by the serialutils plugin
test_data_lengths = range(1, ibis_config.max_data_size + 1)
test_data = [urandom(x) for x in test_data_lengths]


@pytest.fixture(scope="class", params=test_data, ids=[str(len(x)) for x in test_data])
def ibis_testdata(request, ibis_loopback):  # noqa: F811
    """Produces random test data of increasing length."""
    # If the data bits are smaller than 8, crop/mask the test data accordingly
    data = ibis_loopback.crop_data(request.param)

    yield data

    # Flush and clear buffers after testing
    ibis_loopback.flush()
    ibis_loopback.reset_buffers()
    # This is needed for unknown reasons. It seems that flushing takes a while
    time.sleep(0.100)


class Test_IBIS:
    """Runs various short tests on the Cortex IBIS port, using the slave port on the Mainboard A as a loopback."""

    # TUXT-1 (disabled sender part)
    def test_disable_sender(self, ibis_loopback):  # noqa: F811
        # The sender is disabled by default in the fixture we use,
        # but check it to be sure.
        assert ibis_loopback.port.rts is False

        # Sending anything does... absolutely nothing, as expected.
        test_data = b"1234"
        test_data_length = len(test_data)
        assert ibis_loopback.port.write(test_data) == test_data_length

        ibis_loopback.loopback.timeout = 0.5
        assert ibis_loopback.loopback.read(test_data_length) == b""

    # TUXT-1 (enabled sender part) + TUXT-5 + TUXT-7
    def test_send(self, active_ibis_master_loopback, ibis_testdata):  # noqa: F811
        active_ibis_master_loopback.send_bytes(ibis_testdata)

    # TUXT-1 (enabled sender part) + TUXT-6 + TUXT-8
    def test_receive(self, active_ibis_master_loopback, ibis_testdata):  # noqa: F811
        active_ibis_master_loopback.receive_bytes(ibis_testdata)
