import logging
import glob
import os
import hashlib
import time
import re
import pytest

LOGGER = logging.getLogger(__name__)

#@pytest.mark.ssh
#@pytest.mark.scp
#@pytest.mark.ping
@pytest.mark.slow
class Test_TUXT_62:
    """
    TUXT-62

    Test:
        Die neue FW Version kann aufgespielt werden und der Vorgang wird im Systemlog protokolliert.
    Input:
        fw_bin_source               - Ort an dem die FW-Binary abgelegt ist. Die FW-Binary muss an dem Ort in einem Unterordner liegt, der die Version als Namen trägt
        fw_bin_version              - Version der FW-Binary
        path_fw_bin_destination     - Ort an den die FW-Binary auf dem Gerät abgelegt wird
        fw_bin_rename               - Dateiname, wie die FW-Binary auf dem Gerät umbenannt werden soll
        path_update                 - Pfad zum starten des Update Prozesses
    Preconditions:
        Man ist über eine serielle Konsole oder per SSH mit dem Gerät verbunden und als Benutzer “root” eingeloggt (ggf. erst als User “ivu” einloggen und dann mit “sudo -i” root werden). 
    """
    date = ""

    def test_tuxt_62_0(self, configuration, ssh_command, scp):
        """
        Firmware-Datei nach /lib/firmware/ivu/ivumcu.bin auf das Gerät kopieren.
        Die Firmware-Datei kann unter \\\\ivu-ag.com\\storage\\FTP\\FTP_ivu.ticketbox-xl\\software_firmware_hardware\\04_MCU\\fw\\6.6.7\\file_6_6_7.bin abgerufen werden (muss in ivumcu.bin umbenannt werden)
        """
        fw_bin_file = glob.glob(f"{configuration['fw_bin_source']}/{configuration['fw_bin_version']}/*.bin")
        assert len(fw_bin_file) == 1, "FW binary file not found"
        src = os.path.realpath(fw_bin_file[0])
        dst = f"{configuration['path_fw_bin_destination']}/{configuration['fw_bin_rename']}"
        LOGGER.info(f"SCP put: {src} > {dst}")
        scp.put(src, dst)

        output, error = ssh_command(f"sha256sum {configuration['path_fw_bin_destination']}/{configuration['fw_bin_rename']}")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        assert len(output) >= 64, "The output should be at least 64 characters long"

        with open(src, "rb") as f:
            bytes = f.read()
            src_checksum = hashlib.sha256(bytes).hexdigest()

        assert len(src_checksum) == 64, "The calculated checksum has to be 64 characters long"

        assert output[0:64] == src_checksum, "It is to be assumed that the file was modified or damaged during transfer"

    def test_tuxt_62_1(self, configuration, ping, ping_until, ping_timeout, ssh_command):
        """
        Sicherstellen, dass der Akku eingesteckt und geladen ist. Dann wird der Updatevorgang initiiert
        """
        rhost_is_up = ping(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system is offline"

        try:
            output, error = ssh_command(f"cat /sys/devices/housekeeper/power_supply/bat0/present")

            if error.strip() != "":
                LOGGER.error(f"{error.strip()}")

            if output.strip() == "1":
                LOGGER.info("Battery connected")
            else:
                LOGGER.warn("Battery disconnected")
        except:
            LOGGER.warn("Battery status unknown")

        try:
            output, _ = ssh_command("date +\"%F %T\"")
            Test_TUXT_62.date = output.strip()
        except:
            LOGGER.warn("current timestamp unknown")

        try:
            output, error = ssh_command(f"echo 1 > {configuration['path_update']}", timeout=5)
        except:
            output = error = ""

        if error.strip() != "":
            assert error.strip() == "", "The update could not be started for some reason"

        if output.strip() != "":
            LOGGER.error(f"{output.strip()}")

        rhost_is_up = ping_timeout(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system restart for the update process failed or was delayed. The host is still up"

        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available again by now, but it is not. The host is still down"

    def test_tuxt_62_2(self, configuration, ping_until, ssh_command):
        """
        System-Protokoll überprüfen ob MCU Update erfolgreich war
        """
        rhost_is_up = ping_until(configuration['rhost'], configuration['ssh_port'])
        assert rhost_is_up, "The system should be available, but it is not. The host is down"

        if Test_TUXT_62.date == "":
            LOGGER.warn("Kein Datum gespeichert beim FW-Update. Überprüft werden nur die letzten 5 Minuten.")
           
            Test_TUXT_62.date = "5 minutes ago"
        output, error = ssh_command(f"journalctl -t kernel -r --since=\"{Test_TUXT_62.date}\" | grep -B 1 \"Updating MCU firmware\"")

        if error.strip() != "":
            LOGGER.error(f"{error.strip()}")

        match = re.match(r"^(.*)(\r\n|\r|\n).*(\d{2}:\d{2}:\d{2}) .* Updating MCU firmware: (.*)/(.*), size: (\d*), blocks: (\d*)", output)

        assert match, "There was no update entry in the system logs recently"

        assert match[1] == "-- Reboot --", "There was no reboot after the update was initiialized. Update not started."

        LOGGER.info(f"Update durchgeführt um {match[3]}")

        if match[5] != f"{configuration['fw_bin_rename']}":
            LOGGER.warn(f"Update log entry FW-Binary filename {match[5]} does not match {configuration['fw_bin_rename']}")
