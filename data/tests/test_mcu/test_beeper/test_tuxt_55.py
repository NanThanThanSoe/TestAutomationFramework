import pytest
import logging
from data.tests.test_mcu.test_beeper.test_tuxt_54 import Test_TUXT_54

LOGGER = logging.getLogger(__name__)


class Test_TUXT_55:
    """
    TUXT-55

    Test:
        Die Funktion des Beepers konnte 10 mal wiederholt werden
        Jedes mal ist der Beep erfolgreich und gleich laut, lang und hat die gleiche Frequenz
    Input:
    Preconditions:
        aktive Konsolen-Sitzung
        Anwendung läuft nicht
    """

    @pytest.mark.semi_automated
    @pytest.mark.incomplete
    @pytest.mark.repeat(10)
    def test_tuxt_55_0(self, configuration, ssh_command):
        LOGGER.info("invoking test_tuxt_54_0")
        Test_TUXT_54().test_tuxt_54_0(configuration, ssh_command)
