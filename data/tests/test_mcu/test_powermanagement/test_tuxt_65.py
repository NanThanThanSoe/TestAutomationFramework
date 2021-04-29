import logging

LOGGER = logging.getLogger(__name__)


class Test_TUXT_65:
    """
    TUXT-65

    Test:
        Die Schnittstellen sind im sysfs abgebildet
    Configuration:
        path        - Pfad zum Ordner, dessen Inhalt geprüft werden soll
        files       - Datei- und Ordnernamen, die unter dem angegeben Pfad mindestens erwartet werden
        exactMatch  - Wenn True, wird erwartet, dass nicht mehr als die in den files angegebnen Dateien in dem Ordner sind
    Preconditions:
        Über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “ivu” eingeloggt.
    """

    def test_tuxt_65_0(self, configuration, ssh_command):
        """
        Überprüfen, dass die Schnittstelle im Sysfs vorhanden ist.
        Schnittstellen für Batteriespannung sind vorhanden
        """

        output, error = ssh_command(f"ls {configuration['path1']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        filesExpected = configuration["files1"]
        filesSeen = list(filter(None, output.split('\n')))
        filesMissing = [value for value in filesExpected if value not in filesSeen]

        assert filesMissing == [], "File(s) not found"

        if configuration["exactMatch"]:
            filesUnexpected = [value for value in filesSeen if value not in filesExpected]
            assert filesUnexpected == [], "File(s) not expected"

    def test_tuxt_65_1(self, configuration, ssh_command):
        """
        Überprüfen, dass die Schnittstelle im Sysfs vorhanden ist.
        Schnittstellen für Bordnetzspannung sind vorhanden
        """

        output, error = ssh_command(f"ls {configuration['path2']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        filesExpected = configuration["files2"]
        filesSeen = list(filter(None, output.split('\n')))
        filesMissing = [value for value in filesExpected if value not in filesSeen]

        assert filesMissing == [], "File(s) not found"

        if configuration["exactMatch"]:
            filesUnexpected = [value for value in filesSeen if value not in filesExpected]
            assert filesUnexpected == [], "File(s) not expected"
