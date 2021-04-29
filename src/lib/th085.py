# -*- coding: iso-8859-1 -*-

"""
# th085.py
# 2013-01-09 ivu-ag peb 
# Treiber seriell zur Ansteuerung des Supportmoduls TH-085 von PHYTEC
# Aktuell wird nur das Setzen von Ausgaengen unterstuetzt.
# Der serielle Com-Port wird mittels der TH085DLL.dll automatisch ermittelt.
# Muss also im gleichen Verzeichnis liegen.
# V1.0 Neuerstellung
"""

# Modulimport
import serial

__version__ = 1.0
__date__ = "2014-01-09"
__author__ = "peb ivu-ag/aachen"


class TH085:
    def __init__(self, port=-1):
        self.comport = port
        self.ser = serial.Serial()
        self.baudrate = 57600
        self.timeout = 0.1
        # ansteuerung des moduls erfolgt in dem mode debug_mode_off
        self.debug_mode_off = 0  # debug_mode_on = 0, debug_mode_off = 1

    def openCom(self):
        if self.comport != -1:
            self.ser.port = self.comport
            self.ser.baudrate = self.baudrate
            self.ser.timeout = self.timeout
            try:
                self.ser.open()
            except:
                self.comport = -1
        return self.comport

    def closeCom(self):
        if self.comport != -1:
            try:
                self.ser.close()
                self.comport = -1
            except:
                pass
        return self.comport

    def io(self, cmd="", size=1):
        res = ""
        val = -10  # vorbesetzung, wird durch
        if self.comport != -1:
            self.ser.reset_input_buffer()
            cmd += "\r"
            self.ser.write(cmd.encode())
            rc = self.ser.read(size=size)
            val = self.check(rc.decode(), size)
        return val

    def check(self, rc, size):
        val = -15  # gibt es laut PHYTEC nicht
        if len(rc) == size:
            val = -12
            pos = rc.find("th-")
            diff = pos - (size-7)  # ab hier liegt der string
            # anzahl diff zeichen versuchen zu lesen
            if diff > 0:  # es muessen noch zeichen geholt werden
                val = -13
                rdiff = self.ser.read(size=diff)
                if len(rdiff) == diff:
                    rc += rdiff.decode()
            try:
                val = int(rc[(size-10-diff):(size-9+diff)])
            except:
                val = -14
        return val

    def initModul(self):
        # Firmware abfragen im Debug-Mode
        # Debug Mode abschalten
        val = self.io(cmd="debug_mode_off", size=36)
        if val == 0:
            self.debug_mode_off = 1
        else:  # zuruecksetzen und erneut versuchen
            self.io(cmd="17", size=200)
            val = self.io(cmd="debug_mode_off", size=36)
            if val == 0:
                self.debug_mode_off = 1
        return val

    def write(self, port=0, pin=0, state=0):  # brauchen wir mehr?
        val = -10  # gibt es laut PHYTEC nicht
        cmd = "1,%d,%d,%d" % (port, pin, state)
        val = self.io(cmd=cmd, size=20)
        return val

    def udpwrite(self, cmd="", size=20):
        val = -16
        if len(cmd) > 0:
            val = self.io(cmd=cmd, size=size)
        return val
