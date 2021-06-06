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

from serialtestutil.serialtester import rs232_fixture  # noqa: F401

test_data_lengths = [1, 4, 16, 64, 256, 1024, 4096]
test_data = [urandom(x) for x in test_data_lengths]


@pytest.fixture(scope="class", params=test_data, ids=[str(len(x)) for x in test_data])
def testdata_fixture(request, rs232_fixture):  # noqa: F811
    """Produces random test data of increasing length."""
    # If the data bits are smaller than 8, crop/mask the test data accordingly
    data = rs232_fixture.crop_data(request.param)

    yield data

    # Flush and clear buffers after testing
    rs232_fixture.flush()
    rs232_fixture.reset_buffers()
    # This is needed for unknown reasons. It seems that flushing takes a while
    time.sleep(0.100)


class Test_RS232:
    """Runs various short tests on the RS-232 port."""

    def test_rts(self, rs232_fixture):  # noqa: F811
        rs232_fixture.set_rts()

    def test_cts(self, rs232_fixture):  # noqa: F811
        rs232_fixture.read_cts()

    def test_send(self, rs232_fixture, testdata_fixture):  # noqa: F811
        rs232_fixture.send_bytes(testdata_fixture)

    def test_receive(self, rs232_fixture, testdata_fixture):  # noqa: F811
        rs232_fixture.receive_bytes(testdata_fixture)
