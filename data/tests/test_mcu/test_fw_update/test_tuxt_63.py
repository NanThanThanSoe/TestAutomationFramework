import logging

LOGGER = logging.getLogger(__name__)


class Test_TUXT_63:
    """
    TUXT-63

    Test:
        Nach dem Update ist die neue Versionsnummer auslesbar
    Input:
        path        - Pfad zum Ort der FW-Version
        fw_version  - Zu erwartende FW-Version
    Preconditions:
        Man ist über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_63_0(self, configuration, ssh_command):
        """
        Ausgabe der Versionsnummer entsprechend der Version die zuvor installiert wurde
        """
        output, error = ssh_command(f"cat {configuration['path']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        assert output.strip() == configuration["fw_version"], "The MCU FW version is not an exact match"
