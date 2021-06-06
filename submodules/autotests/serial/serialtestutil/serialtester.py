import serial
import time
import pytest
from serialtestutil import rs232_profiles

# The actual tested port
_tested_rs232_port = "/dev/ttyCTX-RS232"
# The loopback port used in testing
_loopback_rs232_port = "/dev/ttymxc2"

# The actual tested port
_tested_ibis_port = "/dev/ttyCTX-IBIS"
# The loopback port (IBIS Slave) used in testing
_loopback_ibis_port = "/dev/ibis-slave"


class SerialTester:
    """Tester help class/fixture base for serial ports."""

    port = None
    loopback = None

    _baudrate = None
    _databits = None
    _parity = None
    _stopbits = None

    def __init__(self, tested_port, loopback_port, rate, databits, parity, stopbits):
        self.port = serial.Serial(port=tested_port, baudrate=rate, bytesize=databits, parity=parity, stopbits=stopbits, timeout=1.0)
        self.loopback = serial.Serial(port=loopback_port, baudrate=rate, bytesize=databits, parity=parity, stopbits=stopbits, timeout=1.0)

        self._baudrate = rate
        self._databits = databits
        self._parity = parity
        self._stopbits = stopbits

        # Reset RTS on both ports
        self.port.rts = False
        self.loopback.rts = False

        # Flush and clear everything first
        # self.reset_buffers()
        # self.flush()
        # This is needed for unknown reasons. It seems that flushing takes a while
        # time.sleep(0.050)

    def send_bytes(self, sent_data):
        """Sends the given bytes on the tested port and checks that they are received on the loopback port."""
        # Set a timeout that is adapted to the baudrate and data length
        self._set_timeouts(len(sent_data))

        sent_length = self.port.write(sent_data)
        assert len(sent_data) == sent_length

        received_data = self.loopback.read(sent_length)
        assert len(received_data) == sent_length
        assert received_data == sent_data

        # Check that there is nothing left in the receive buffer
        assert self.loopback.in_waiting == 0

    def receive_bytes(self, sent_data):
        """Sends the given bytes on the loopback port and checks that they are received on the tested port."""
        # Set a timeout that is adapted to the baudrate and data length
        self._set_timeouts(len(sent_data))

        sent_length = self.loopback.write(sent_data)
        assert len(sent_data) == sent_length

        received_data = self.port.read(sent_length)
        assert len(received_data) == sent_length
        assert received_data == sent_data

        # Check that there is nothing left in the receive buffer
        assert self.port.in_waiting == 0

    def bounce_data(self, sent_data, duration=None, cycles=None):
        """Sends the data back and forth between the two ports for the given duration or number of cycles, whichever happens first.

        Either the duration or the cycles may be None, in which case it is ignored.
        """
        if duration is None and cycles is None:
            raise ValueError('At least one of the "duration" or "cycles" arguments must be set')

        end_time = None
        max_cycles = None

        if duration is not None:
            end_time = time.time() + duration
        if cycles is not None:
            max_cycles = cycles

        cycle_count = 0

        # Set a timeout that is adapted to the baudrate and data length
        self._set_timeouts(len(sent_data))

        while True:
            # Do we have a reason to break? If yes, do so.
            if end_time is not None and time.time() >= end_time:
                break
            if max_cycles is not None and cycle_count >= max_cycles:
                break

            # Forth...
            sent_length = self.port.write(sent_data)
            assert len(sent_data) == sent_length
            received_data = self.loopback.read(sent_length)
            assert len(received_data) == sent_length
            assert received_data == sent_data

            # And back...
            sent_length = self.loopback.write(sent_data)
            assert len(sent_data) == sent_length
            received_data = self.port.read(sent_length)

            assert len(received_data) == sent_length
            assert received_data == sent_data

            cycle_count += 1

    def set_rts(self):
        """Sets RTS on the port and checks whether the loopback port receives it as CTS."""
        # Initial check - is everything set to zero?
        assert self.port.rts is False
        assert self.loopback.cts is False

        # Set RTS on the tested port
        self.port.rts = True

        # Wait for the drivers to react
        time.sleep(0.2)

        # Check CTS on the loopback port
        assert self.loopback.cts is True

        # Reset RTS on the tested port
        self.port.rts = False

    def read_cts(self):
        """Sets RTS on the loopback port and checks whether the tested port receives it as CTS."""
        # Initial check - is everything set to zero?
        assert self.port.rts is False
        assert self.loopback.cts is False

        # Set RTS on the loopback port
        self.loopback.rts = True

        # Wait for the drivers to react
        time.sleep(0.2)

        # Check CTS on the tested port
        assert self.port.cts is True

        # Reset RTS on the loopback port
        self.loopback.rts = False

    def close(self):
        """Flushes and closes all ports."""
        self.flush()
        self.reset_buffers()
        self.port.close()
        self.loopback.close()

    def reset_buffers(self):
        """Resets input and output buffers on both ports."""
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.loopback.reset_input_buffer()
        self.loopback.reset_output_buffer()

    def flush(self):
        """Flushes both ports."""
        self.port.flush()
        self.loopback.flush()

    def crop_data(self, data):
        """Crops the given data if the byte length of the ports is smaller than 8."""
        output = data
        if (self._databits < 8):
            mask = 0xff >> (8 - self._databits)
            output = bytes([x & mask for x in data])

        return output

    def _set_timeouts(self, data_length):
        """Set a timeout that is adapted to the baudrate and data length."""
        # Computed simply as data * 8 / baudrate, e.g. 4096 bytes should
        # take 3.41 seconds @ 9600 bauds. Plus one second for very small
        # data lengths and 10% extra as a safety margin, because this
        # computation does not take e.g. start and stop bits into account.

        timeout = (((data_length * 8) / self.port.baudrate) + 1) * 1.10

        self.port.timeout = timeout
        self.loopback.timeout = timeout


def _get_id_for_params(p):
    return "{},{},{},{}".format(p[0], p[1], p[2], p[3])


@pytest.fixture(scope="module", params=rs232_profiles.get_selected_port_configurations(), ids=_get_id_for_params) # noqa: ERRCODE
def rs232_fixture(request):
    """Fixture that produces the Serial Port we need, parametrized with in all selected port configurations."""
    rate = request.param[0]
    data_bits = request.param[1]
    parity = request.param[2]
    stop_bits = request.param[3]

    tester = SerialTester(_tested_rs232_port, _loopback_rs232_port, rate, data_bits, parity, stop_bits)

    # Setup done, execute the tests
    yield tester

    # Tests executed, tear-down code
    tester.close()


# The IBIS port configurations are fixed.
_all_ibis_configurations = [
    (1200, serial.SEVENBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE),
    (1200, serial.SEVENBITS, serial.PARITY_EVEN, serial.STOPBITS_TWO)
]


def create_loopback(rate, data_bits, parity, stop_bits):
    """Factory method for the IBIS loopback fixtures."""
    tester = SerialTester(_tested_ibis_port, _loopback_ibis_port, rate, data_bits, parity, stop_bits)

    # Cycle RTS on and off to clear DSR AND CTS lines (short-circuit detection)
    tester.port.rts = False
    time.sleep(0.1)
    tester.port.rts = True
    time.sleep(0.1)
    # Leave the sender turned off by default.
    tester.port.rts = False
    time.sleep(0.1)

    # Turning off the sender is received as a garbage byte on the slave,
    # an artifact of the interface at the electrical level.
    # Expect, but ignore it. Up to twice since we reset RTS twice.
    tester.loopback.timeout = 0.1
    tester.loopback.read(2)

    # The same also happens on the master. Disabling the sender
    # probably also disables the answer bus, with similar glitches.
    tester.port.timeout = 0.1
    tester.port.read(2)

    # Setup done, execute the tests
    yield tester

    # Tests executed, tear-down code
    tester.close()


@pytest.fixture(scope="module")
def ibis_loopback_single_config():
    """Fixture that opens the IBIS Cortex master port and the Mainboard A slave port as a loopback test pair, with a single configuration."""
    yield from create_loopback(*_all_ibis_configurations[0])


@pytest.fixture(scope="module", params=_all_ibis_configurations, ids=_get_id_for_params)
def ibis_loopback(request):
    """Fixture that opens the IBIS Cortex master port and the Mainboard A slave port as a loopback test pair, for all configurations."""
    yield from create_loopback(*request.param)


@pytest.fixture(scope="class")
def active_ibis_master_loopback(request, ibis_loopback):
    """IBIS loopback fixture that turns on the sender and stabilizes the bus."""
    # Turn on the sender
    ibis_loopback.port.rts = True

    # The usual waiting for things to settle
    time.sleep(0.1)

    yield ibis_loopback  # Run the tests

    # Turn off the sender
    ibis_loopback.port.rts = False
    time.sleep(0.1)

