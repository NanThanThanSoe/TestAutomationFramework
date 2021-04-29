import logging
import time
import pytest

LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class Test_TUXT_82:
    """
    TUXT-82

    Test:
        In diesem Testfal wird geprüft, ob die Ursache eines Reboos aus den Dateien im sysfs gelesen weren können.
    Configuration:
        path_reason               - Pfad zum abfragen des Boot Grundes
        path_code                 - Pfad zum abfragen des Boot Grund Code
    Preconditions:
        Lauffähige IVU.ticket.box G3R Linux mit Anbindung per SSH - Shell.
        Verbindung zum USB Opto 4 Out oder zum TH085 Board
    """

    def test_tuxt_82_0(self, configuration, ignition, ping_until, ping_timeout):
        """
        Gerät einschalten, hochfahren lassen und wieder ausschalten. Warten, bis es komplett abgeschaltet ist.
        """
        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available by now, but it is not. The host is down"

        ignition(False)

        rhost_is_up = ping_timeout(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be down by now, but it is not. The host is still up"

        time.sleep(10)

    def test_tuxt_82_1(self, configuration, ignition, ping_until):
        """
        Gerät einschalten und warten, bis es hochgefahren ist und man sich per SSH - Shell mit dem Gerät verbinden kann.
        """
        ignition(True)

        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available again by now, but it is not. The host is still down"

    def test_tuxt_82_2(self, configuration, ssh_command):
        """
        Boot reason abfragen und sicherstellen, dass der Grund passt
        """
        output, error = ssh_command(f"cat {configuration['path_reason']}")

        if error != "":
            LOGGER.error(f"{error}")

        assert output == "unknown_or_hw"

    def test_tuxt_82_3(self, configuration, ssh_command):
        """
        Boot code abfragen und sicherstellen, dass der Code zum Grund passt
        """
        output, error = ssh_command(f"cat {configuration['path_code']}")

        if error != "":
            LOGGER.error(f"{error}")

        assert output == "0"
