import logging
import pytest
from data.tests.test_mcu.test_fw_update.test_tuxt_62 import Test_TUXT_62

LOGGER = logging.getLogger(__name__)


class Test_TUXT_64:
    """
    TUXT-64

    Test:
        Der Vorgang kann fehlerfrei 10 mal wiederholt werden
        Testfall TUXT-62 wird 10 mal wiederholt
        Die Updatevorgänge sind erfolgreich und es findet jedes Mal ein Neustart des Systems statt.
    Input:
        fw_bin_source               - Ort an dem die FW-Binary abgelegt ist. Die FW-Binary muss an dem Ort in einem Unterordner liegt, der die Version als Namen trägt
        fw_bin_version              - Version der FW-Binary
        path_fw_bin_destination     - Ort an den die FW-Binary auf dem Gerät abgelegt wird
        fw_bin_rename               - Dateiname, wie die FW-Binary auf dem Gerät umbenannt werden soll
        path_update                 - Pfad zum starten des Update Prozesses
    Preconditions:
        Man ist über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “root” eingeloggt (ggf. erst als User “ivu” einloggen und dann mit “sudo -i” root werden). 
    """

    def test_tuxt_64_0(self, configuration, ssh_command, ping, ping_until, ping_timeout, scp):
        """
        10 mal die Schritte aus TUXT-62 wiederholen.
        Update immer erfolgreich. Verhalten weicht nicht ab
        """
        LOGGER.info("invoking test_tuxt_62_0")
        Test_TUXT_62().test_tuxt_62_0(configuration, ssh_command, scp)
        LOGGER.info("invoking test_tuxt_62_1")
        Test_TUXT_62().test_tuxt_62_1(configuration, ping, ping_until, ping_timeout, ssh_command)
        LOGGER.info("invoking test_tuxt_62_2")
        Test_TUXT_62().test_tuxt_62_2(configuration, ping_until, ssh_command)
