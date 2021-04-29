import logging

LOGGER = logging.getLogger(__name__)


class Test_TUXT_53:
    """
    TUXT-53

    Test:
        Im sysfs ist die Schnittstelle für den Beeper vorhanden
    Input:
        path        - Pfad unter dem der Beeper vorhanden sein sollte
    Preconditions:
        aktive Konsolensitzung
    """

    def test_tuxt_53_0(self, configuration, ssh_command):
        """
        Prüfen ob der Pfad /dev/input/beeper0 vorhanden ist
        """
        output, error = ssh_command(f"ls {configuration['path']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        assert(output.strip() == f"{configuration['path']}")
