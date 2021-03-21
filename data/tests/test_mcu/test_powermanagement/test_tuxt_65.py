import logging
import pytest

LOGGER = logging.getLogger(__name__)

#@pytest.mark.ssh
@pytest.mark.slow
class Test_TUXT_65:

    def test_tuxt_65_0(self, configuration, ssh_command):

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
