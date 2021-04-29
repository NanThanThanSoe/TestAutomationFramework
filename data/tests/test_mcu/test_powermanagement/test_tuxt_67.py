import logging
import pytest
import time

LOGGER = logging.getLogger(__name__)


@pytest.mark.incomplete
class Test_TUXT_67:
    """
    TUXT-67

    Test:
        Manueller Test stellt sicher, dass die jeweilig korrekte Energieschnittstelle ausgegeben wird (Netzspannung oder Akku)
    Input:
        path                - Pfad zum Ort
        val                 - Expected value
    Preconditions:
        Über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_67_0(self, configuration, ssh_command, battery_disconnect):
        """
        Kabel vom Akku aufdem Mainboard ausstecken und anschließend folgenden Befehle ausführen.
        Akku wird nicht mehr erkannt und Spannung ist 0
        """
        output1, error1 = ssh_command(f"cat {configuration['path1.1']}")

        if error1.strip() != "":
            LOGGER.error(f"{error1.strip()}")

        valueSeen1 = int(output1.strip())

        assert valueSeen1 == 0, "The present battery value is not an exact match"

        output2, error2 = ssh_command(f"cat {configuration['path1.2']}")

        if error2.strip() != "":
            LOGGER.error(f"{error2.strip()}")

        valueSeen2 = int(output2.strip())

        assert valueSeen2 == 0, "The current battery voltage value is not an exact match"

    def test_tuxt_67_1(self, configuration, ssh_command, ignition_off):
        """
        Akku wieder einstecken und Bordnetzspannung abschalten. Nun zeitnah folgende Befehle ausführen bevor das System herunterfährt:
        """
        output, error = ssh_command(f"cat {configuration['path2']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueExpected = configuration["val2"]
        valueSeen = output.strip()

        assert valueSeen <= valueExpected, "The dc voltage value is not an exact match"
