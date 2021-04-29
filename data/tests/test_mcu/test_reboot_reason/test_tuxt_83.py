import logging
import pytest

LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class Test_TUXT_83:
    """
    TUXT-83

    Test:
        In diesem Testfal wird geprüft, ob die Ursache eines Reboos aus den Dateien im sysfs gelesen werden können.
    Configuration:
        path_reason               - Pfad zum abfragen des Boot Grundes
        path_code                 - Pfad zum abfragen des Boot Grund Code
    Preconditions:
        Lauffähige IVU.ticket.box G3R Linux mit Anbindung per SSH - Shell.
    """

    def test_tuxt_83_0(self, configuration, ping_until):
        """
        Gerät einschalten und warten, bis es hochgefahren ist und man sich per SSH - Shell mit dem Gerät verbinden kann.
        """
        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available by now, but it is not. The host is down"

    def test_tuxt_83_1(self, configuration, ssh_command, ping_timeout):
        """
        Reboot ausführen
        """
        try:
            _, _ = ssh_command(f"echo c > /proc/sysrq-trigger")
        except:
            pass

        rhost_is_down = ping_timeout(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_down, "The system should be shutdown by now, but it is not. The host is still up"

    def test_tuxt_83_2(self, configuration, ping_until):
        """
        Warten, bis das Gerät hochgefahren ist und man sich per SSH - Shell mit dem Gerät verbinden kann.
        """
        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available by now, but it is not. The host is down"

    def test_tuxt_83_3(self, configuration, ssh_command):
        """
        Boot reason abfragen und sicherstellen, dass der Grund passt
        """
        output, error = ssh_command(f"cat {configuration['path_reason']}")

        if error != "":
            LOGGER.error(f"{error}")

        assert output == "wdog_api"

    def test_tuxt_83_4(self, configuration, ssh_command):
        """
        Boot code abfragen und sicherstellen, dass der Code zum Grund passt
        """
        output, error = ssh_command(f"cat {configuration['path_code']}")

        if error != "":
            LOGGER.error(f"{error}")

        assert output == "7"
