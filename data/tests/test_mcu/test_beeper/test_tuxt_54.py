import pytest
import logging
import time
from threading import Thread

LOGGER = logging.getLogger(__name__)


class Test_TUXT_54:
    """
    TUXT-54

    Test:
        Der Beeper kann über eine Schnittstelle angesteuert werden (Es ertönt ein Signal)
        Ein Signal mit Frequenz 440Hz, 50% Lautstärke und 200ms Dauer wird abgespielt.
    Input:
    Preconditions:
        aktive Konsolen-Sitzung
        Anwendung läuft nicht
    """

    @pytest.mark.semi_automated
    @pytest.mark.incomplete
    def test_tuxt_54_0(self, configuration, ssh_command):
        def main_test():
            #time.sleep(5)
            output, error = ssh_command("beep")

            assert output == ""
            assert error == ""

        beep_thread = Thread(target=main_test)
        LOGGER.info("Initialize beep")
        started_at = time.time()
        beep_thread.start()

        time.sleep(5)

        response = True# microphone.waitForBeep()
        # Record Audio and listen for beep while blocking the thread

        assert response, "The microphone could not pick up the beep sound"

        assert abs(time.time() - (started_at + 5)) < 3, "Time offset too high. Check Audio recording."
