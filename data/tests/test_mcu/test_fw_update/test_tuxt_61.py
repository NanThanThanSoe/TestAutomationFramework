import logging
import re

LOGGER = logging.getLogger(__name__)


class Test_TUXT_61:
    """
    TUXT-61

    Test:
        Die aktuelle FW Version kann ausgelesen werden
    Input:
        path                - Pfad zum Ort der FW-Version
        fw_version          - Zu erwartende FW-Version
        allow_newer_version - Wenn True, ist die erwartete FW-Version nur eine Mindestanforderung
    Preconditions:
        Man ist über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_61_0(self, configuration, ssh_command):
        """
        Die aktuelle FW-Version kann ausgelesen werden
        """
        output, error = ssh_command(f"cat {configuration['path']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        versionExpected = configuration["fw_version"]
        versionSeen = output.strip()
        if configuration["allow_newer_version"]:
            versionListExpected = re.findall("\\d*", versionExpected)
            versionListSeen = re.findall("\\d*", versionSeen)

            assert len(versionListExpected) == len(versionListSeen), "The version format is different"

            newer = False
            for i in range(len(versionListExpected)):
                if versionListSeen[i] > versionListExpected[i]:
                    newer = True
                assert newer or versionListSeen[i] == versionListExpected[i], "The MCU FW version is older than expected"
        else:
            assert versionSeen == versionExpected, "The MCU FW version is not an exact match"
