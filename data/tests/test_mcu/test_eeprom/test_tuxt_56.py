import logging
import pytest
import re

LOGGER = logging.getLogger(__name__)


@pytest.mark.incomplete
class Test_TUXT_56:
    """
    TUXT-56

    Test:
        Überprüfen ob das EEPROM, wenn angeschlossen an der korrekten Stelle im sysfs eingehängt ist
    Configuration:
        path        - Pfad unter dem EEPROM eingehängt wird
        files       - Datei- und Ordnernamen, die unter dem angegeben Pfad mindestens erwartet werden
        exactMatch  - Wenn True, wird erwartet, dass nicht mehr als die in den files angegebnen Dateien in dem Ordner sind
    Preconditions:
        Lauffähige IVU.ticket.box G3R mit angeschlossenem 1Wire - Eeprom sowie Anbindung zu einer SSH - Shell.
    """

    def test_tuxt_56_0(self, configuration, ssh_command):
        """
        Gerät starten und warten, bis es hochgefahren ist und man sich per SSH - Shell mit dem Gerät verbinden kann.
        """

        # ToDo: Warten bis Gerät gestartet ist. Eventuell Start initialisieren mit externem Modul / Plugin?

        output, error = ssh_command("echo 1")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")
        assert output.strip() == "1"


    def test_tuxt_56_1(self, configuration, ssh_command):
        """
        In das car-eeprom Verzeichnis wechseln
        """

        output, error = ssh_command(f"cd {configuration['path']}")

        assert error.strip() == ""
        assert output.strip() == ""


    def test_tuxt_56_2(self, configuration, ssh_command):
        """
        Die Dateien auflisten in dem Verzeichnis
        """

        output, error = ssh_command(f"cd {configuration['path']};ls *")

        assert error.strip() == ""

        checkFilesExist(output, configuration["files"], configuration["exactMatch"])

def checkFilesExist(output, files, exactMatch):
    subdirectories = re.findall(r"^(.*):$", output, flags=re.MULTILINE)
    output_list = re.split(r"^(.*):$", output, flags=re.MULTILINE)
    if len(output_list) == len(subdirectories) * 2:
        output_list.insert(0, "")
    output_list.insert(0, ".")

    output_structured = {}

    for i in range(int(len(output_list) / 2)):
        output_structured[output_list[i * 2]] = re.split(r"\s+", output_list[1 + i * 2].strip(), flags=re.MULTILINE)

    compareDirectoryContent(files, output_structured, exactMatch)

def compareDirectoryContent(filesExpected, filesSeen, exactMatch):
    filesMissing = [value for value in filesExpected if value not in filesSeen]
    
    assert filesMissing == [], "File(s) or Subdirectory(s) not found"

    if exactMatch:
        filesUnexpected = [value for value in filesSeen if value not in filesExpected]
        assert filesUnexpected == [], "File(s) or Subdirectory(s) not expected"

    if type(filesSeen) is type({}):
        for subdirectory in filesExpected:
            compareDirectoryContent(filesExpected[subdirectory], filesSeen[subdirectory], exactMatch)
