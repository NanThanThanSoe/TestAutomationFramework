import logging
import re

LOGGER = logging.getLogger(__name__)


class Test_TUXT_66:
    """
    TUXT-66

    Test:
        Die Schnittstellen können ausgelesen werden und enthalten sinnvolle Werte
    Input:
        path                - Pfad zum Ort
        val                 - Expected value
    Preconditions:
        Über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_66_0(self, configuration, ssh_command):
        """
        Aktuelle Bordnetzspannung auslesen 
        """
        output, error = ssh_command(f"cat {configuration['path1']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueExpected_min = int(configuration["val1.0"])
        valueExpected_max = int(configuration["val1.1"])
        valueSeen = int(output.strip())
        
        assert valueSeen >= valueExpected_min and valueSeen <= valueExpected_max, "The dc voltage value is not as expected"

    def test_tuxt_66_1(self, configuration, ssh_command):
        """
        Überprüfen ob der Akku korrekt erkannt wurde
        """
        output, error = ssh_command(f"cat {configuration['path2']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueSeen = int(output.strip())
        
        assert valueSeen == 1, "The ntc_present battery value is not an exact match"

    def test_tuxt_66_2(self, configuration, ssh_command):
        """
        Überprüfen ob der Akku korrekt erkannt wurde
        """
        output, error = ssh_command(f"cat {configuration['path3']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueSeen = int(output.strip())
        
        assert valueSeen == 1, "The present battery value is not an exact match"

    def test_tuxt_66_3(self, configuration, ssh_command):
        """
        Aktuelle Batteriespannung auslesen
        """
        output, error = ssh_command(f"cat {configuration['path4']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueExpected = int(configuration["val4"])
        valueSeen = int(output.strip())
        
        assert valueSeen >= valueExpected, "The current battery voltage is not an exact match"

    def test_tuxt_66_4(self, configuration, ssh_command):
        """
        Aktuelle Batteriespannung auslesen
        """
        output, error = ssh_command(f"cat {configuration['path5']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        valueExpected_min = int(configuration["val5.0"])
        valueExpected_max = int(configuration["val5.1"])
        valueSeen = int(output.strip())
        
        assert valueSeen >= valueExpected_min and valueSeen <= valueExpected_max, "The current battery temperature is not an exact match"