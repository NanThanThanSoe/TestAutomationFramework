import logging
import time
import pytest

LOGGER = logging.getLogger(__name__)


@pytest.mark.debugging
class Test_TH085_1:
    """
    TH085-1

    Test:
        Das TH085 Modul schaltet die Ticketbox nach 2 Sekunden ein und nach weiteren 5 Sekunden wieder aus
    Input:
    Preconditions:
    """
    def test_th085_1_0(self, configuration, th085):
        LOGGER.info(f"TH085 Port open ?:   {th085.ser.is_open}")
        time.sleep(2)
        LOGGER.info(f" WRITE:   {th085.write(port=4, pin=7, state=1)}")
        time.sleep(5)
        LOGGER.info(f" WRITE:   {th085.write(port=4, pin=7, state=0)}")

    def test_peaktech1885_1_0(self, configuration, peaktech1885):
        LOGGER.info(f"peaktech1885 Port open ?:   {peaktech1885.ser.is_open}")
        PWL = "pwl=0,24 5,10 10,10 15,24 20,24"
        peaktech1885.iocontrol(cmd="U=24")
        peaktech1885.iocontrol(cmd="Ein")
        peaktech1885.iocontrol(cmd="DELAY=1.0")
        time.sleep(1)
        peaktech1885.iocontrol(cmd=PWL)

    def test_usbopto4out_1_0(self, configuration, usbopto4out):
        LOGGER.info(f"usbopto4out Port open ?:   {usbopto4out.ser.is_open}")
        usbopto4out.iocontrol("setOut1")
        time.sleep(5)
        usbopto4out.iocontrol("clrOut1")
