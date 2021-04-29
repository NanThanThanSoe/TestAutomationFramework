import logging
import pytest
import re

LOGGER = logging.getLogger(__name__)


@pytest.mark.usefixtures("scp_put_tmp")
class Test_TUXT_92:
    """
    TUXT-92

    Test:
        Grobe Zusammenfassung: Nachricht schicken, Nachricht empfangen, Nachricht auf Integrität prüfen.
            Die Schnittstelle kann gemäß der Spezifikation erreicht werden und ist via ioctl und termios konfigurierbar.
            Eine definierte Standardnachricht kann gesendet werden und wird auf der Empfängerseite erfolgreich auf Integrität geprüft.
            Eine definierte Standardnachricht wird von der Gegenseite gesendet, kann empfangen werden und und wird erfolgreich auf Integrität geprüft.
            Die RTS-Leitung kann auf der Schnittstelle gesetzt werden. Auf der Gegenseite führt das zum Setzen der CTS-Leitung.
            Die CTS-Leitung kann auf der Schnittstelle ausgelesen werden. Sie wird gesetzt wenn wenn die Gegenseite ihre RTS-Leitung setzt.
        Die Tests sind automatisiert und werden für alle in der RS232-Spezifikation aufgelisteten Porteinstellungen gemacht:
            9600 Baud, 8 Datenbits, 1 Stop-Bit, keine Parität
            38400 Baud, 8 Datenbits, 1 Stop-Bit, keine Parität
            57600 Baud, 8 Datenbits, 1 Stop-Bit, keine Parität
            115200 Baud, 8 Datenbits, 1 Stop-Bit, keine Parität
        Nach den CTS/RTS-Tests werden die Sende- und Empfangstests mit Nachrichten der folgenden Längen ausgeführt: 1, 4, 6, 64, 256, 1024 und 4096 Bytes.
    Configuration:
        path_src          - Pfad zum Ort an dem die Seriellen Tests verfügbar sind
        path_dst          - Pfad unter dem die Seriellen Tests auf dem Gerät abgelegt werden
        test_file_or_dir  - Test Datei die von pytest auf dem Gerät ausgeführt wird
        files             - Dateien, die im Ordner der Seriellen Tests verfügbar sein müssen
        exactMatch        - Wenn True, wird erwartet, dass nicht mehr als die in den files angegebnen Dateien in dem Ordner sind
        profile           - Profil mit dem die Tests ausgeführt werden
    Preconditions:
        Das eingesetzte Linux-Image enthält python3, pytest und pyserial.
        Die automatisierte seriellen Tests aus http://git.ivu-ag.com/projects/IVUBOXOS/repos/autotests/browse/serial sind auf dem Gerät installiert, z.B. unter /harddisk/tests.
        Beide RS232-Ports sind mit einem Null-Modem (= gekreuzten) Kabel miteinander verbunden.
        Beide RS232-Stecker am Kabel sind festgeschraubt.
    """

    def test_tuxt_92_0(self, configuration, ssh_command):
        """
        Eine Shell auf dem Gerät öffnen.
        In das Installationsverzeichnis der automatisierten seriellen Tests wechseln.
        Ein Aufruf von "ls" zeigt mindestens die Datei "test_rs232.py" an.
        """

        output, error = ssh_command(f"ls {configuration['path_dst']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        filesExpected = configuration["files"]
        filesSeen = list(filter(None, output.split('\n')))
        filesMissing = [value for value in filesExpected if value not in filesSeen]

        assert filesMissing == [], "File(s) not found"

        if configuration["exactMatch"]:
            filesUnexpected = [value for value in filesSeen if value not in filesExpected]
            assert filesUnexpected == [], "File(s) not expected"


    def test_tuxt_92_1(self, configuration, ssh_command, th085):
        """
        Die Sendetests starten.
        Alle Tests sind erfolgreich und zeigen PASSED an.
        """

        LOGGER.info(f"Enable TH085 Loopback UAR1")
        th0850_status = th085.write(port=4, pin=3, state=1)
        assert th0850_status == 0, "Failed to enable serial loopback on UAR1"

        output, error = ssh_command(f"cd {configuration['path_dst']};pytest {configuration['test_file_or_dir']} -P {configuration['profile']} -v")
        
        LOGGER.info(f"Disable TH085 Loopback UAR1")
        th0850_status = th085.write(port=4, pin=3, state=0)
        if th0850_status != 0:
            LOGGER.critical("Failed to disable serial loopback on UAR1")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        matches = re.finditer(r"^(.*) FAILED\s*\[\s*(\d+)\%\]$", output, re.MULTILINE)

        failed = 0
        for match in matches:
            failed += 1
            LOGGER.error(f"Test failed: {match[1]}")
        
        if failed > 0:
            pytest.fail("At least one serial test has failed", False)
