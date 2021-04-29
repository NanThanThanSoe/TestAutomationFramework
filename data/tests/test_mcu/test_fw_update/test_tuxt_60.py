import logging

LOGGER = logging.getLogger(__name__)


class Test_TUXT_60:
    """
    TUXT-60

    Test:
        Die Schnisttelle zur MCU im SysFS ist vorhanden.
    Configuration:
        path        - Pfad zum Ordner, dessen Inhalt geprüft werden soll
        files       - Datei- und Ordnernamen, die unter dem angegeben Pfad mindestens erwartet werden
        exactMatch  - Wenn True, wird erwartet, dass nicht mehr als die in den files angegebnen Dateien in dem Ordner sind
    Preconditions:
        Man ist über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_60_0(self, configuration, ssh_command):
        """
        Überprüfen, dass die Schnittstelle im Sysfs vorhanden ist
        """

        output, error = ssh_command(f"ls {configuration['path']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        filesExpected = configuration["files"]
        filesSeen = list(filter(None, output.split('\n')))
        filesMissing = [value for value in filesExpected if value not in filesSeen]

        assert filesMissing == [], "File(s) not found"

        if configuration["exactMatch"]:
            filesUnexpected = [value for value in filesSeen if value not in filesExpected]
            assert filesUnexpected == [], "File(s) not expected"
