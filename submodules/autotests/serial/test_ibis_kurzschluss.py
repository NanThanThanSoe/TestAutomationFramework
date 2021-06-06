#!/usr/bin/env python3

# This has to be at the top to allow the script to be run standalone
if __name__ == "__main__":
    import sys
    import pytest
    pytest.main(sys.argv)

import pytest
import time
import sys

from serialtestutil.serialtester import ibis_loopback_single_config  # noqa: F401


class Test_IBIS_Short_Circuits:
    """Executes short-circuit tests on the IBIS sender (master) and answer (slave) busses.
    
    Shorting the sender bus is not possible without external help. Until some way to automate this becomes available,
    the user is required to cause the short-circuit manually. The "please_short/please_unshort" tests are here to
    leave them time to do so.
    """

    # TUXT-2
    def test_default_cts_dsr_values(self, ibis_loopback_single_config):  # noqa: F811

        # Default state with the sender off
        ibis_loopback_single_config.port.rts = False
        time.sleep(0.1)
        assert ibis_loopback_single_config.port.cts is True
        assert ibis_loopback_single_config.port.dsr is True

        # Same with the sender on
        ibis_loopback_single_config.port.rts = True
        time.sleep(0.1)
        assert ibis_loopback_single_config.port.cts is True
        assert ibis_loopback_single_config.port.dsr is True

    # User action needed for test_master_bus_short_circuit
    def test_please_short_the_sender_bus_within_the_next_20_seconds(self, ibis_loopback_single_config):  # noqa: F811
        # Initial state:
        # Sender is on
        ibis_loopback_single_config.port.rts = True
        time.sleep(0.1)

        # No master short circuit detected (yet)
        assert ibis_loopback_single_config.port.cts is True

        # Wait for the user to do a short circuit...
        time.sleep(20)

        # The short circuit should now be detected
        assert ibis_loopback_single_config.port.cts is False

    # TUXT-3 + TUXT-12
    def test_sender_bus_short_circuit(self, ibis_loopback_single_config):  # noqa: F811
        # This test requires a short-circuit on the master,
        # e.g. by bridging pins 1 and 6 of the IBIS Sub-D9 connector with a paper clip.

        # The short circuit should be visible on CTS
        assert ibis_loopback_single_config.port.cts is False

    # User action needed after test_master_bus_short_circuit
    def test_please_unshort_the_sender_bus_within_the_next_20_seconds(self, ibis_loopback_single_config):  # noqa: F811

        # Precondition: the master is shorted
        assert ibis_loopback_single_config.port.cts is False

        # Wait for the user to remove the short circuit.
        # There is no way to check whether this actually gets done until
        # the next test
        time.sleep(20)

    # TUXT-12 (CTS case)
    def test_master_reset_short_circuit_flag(self, ibis_loopback_single_config):  # noqa: F811
        # Toggle RTS to reset the short-circuit flag
        ibis_loopback_single_config.port.rts = False
        time.sleep(0.050)
        ibis_loopback_single_config.port.rts = True
        assert ibis_loopback_single_config.port.cts is True

    # TUXT-4 + TUXT-12 (DSR case)
    def test_answer_bus_short_circuit(self, ibis_loopback_single_config):  # noqa: F811
        # Initial state:
        # Sender is on
        ibis_loopback_single_config.port.rts = True

        # Wait a bit for the sender to actually be turned on
        time.sleep(0.050)

        # No slave short circuit detected
        assert ibis_loopback_single_config.port.dsr is True

        # Simulate a short-circuit on the slave side
        ibis_loopback_single_config.loopback.send_break(0.2)

        # This should be visible on DSR
        assert ibis_loopback_single_config.port.dsr is False

        # Toggle RTS to reset the short-circuit flag
        ibis_loopback_single_config.port.rts = False
        time.sleep(0.050)
        ibis_loopback_single_config.port.rts = True
        assert ibis_loopback_single_config.port.dsr is True
