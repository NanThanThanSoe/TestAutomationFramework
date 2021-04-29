# Ansteuerung Netzteil 1885 von PeakTech
# peb 22.03.2012 drv_peaktech1885.py
# V 0.0.1 21.06.2012 Neuerstellung
# V 0.0.2 22.06.2012 Optimierung, Bugs entfernt im Threading

"""
Diese Klasse wird mehrmals fuer jedes PeakTech 1885 aufgerufen.
Die Netzgeraete sind fix mit dem Testplatz verbunden
und somit auch der Comport. D. h., bei Start der Oberflaechen
kann diese Information an die einzelen PMainWindows uber die
ini-Datei mitgegeben werden. Das Oeffnen findet entweder in der
GUI statt oder dem darunterliegenden testmanager. Von dort wird
dann bei Bedarf das ganze in die Testklasse tm_power geimpft.

Hier sollte auch der Thread fuer PWL gestartet und gestoppt werden
koennen, da von mehreren Power-Modulen darauf zugegriffen wird.

Die Klasse zur Berechnung der PWL ebenfalls.
"""

import threading
import time
import serial
ADDR_PEAKTECH1885 = "00"

MODUL_NAME = "PEAKTECH 1885"


class Pwl_thread(threading.Thread):
    def __init__(self, device=None, pwl=None, delay=0.5):
        """Implementiert einen Thread zur Ausgabe der PWL-Spannung"""
        threading.Thread.__init__(self, name="pwl_thread")
        self.pwlrun = False
        self.device = device
        self.delay = delay  # Treiber peaktech 1885
        self.pwl = pwl   # Instanz von pwl

    def pwl_stop(self):
        """Beendet den Thread (synchron - blockiert ggf. kurz)."""
        self.pwlrun = False
        self.join(1.0 + self.delay)

    def pwl_start(self):
        self.pwlrun = True
        self.start()

    def run(self):
        #print("Start PWL-Ausgabe")
        self.pwl.runPWL()
        while self.pwl.getStop() == False and self.pwlrun:
            val = self.pwl.getNextValue()
            if self.device != None:
                txt = "U=%04.1f" % val
                self.device.iocontrol(txt)
            # print txt
            time.sleep(self.delay)
        #print("PWL-Ausgabe beendet")


class Pwl():
    def __init__(self, pwl=None):
        if pwl != None:
            self.PWL = pwl
        else:
            self.PWL = "0,24 5,10 10,10 15,24 20,24"
        self.PWL = self.PWL.split(" ")
        self.Size = len(self.PWL)
        # print self.PWL, self.Size
        self.StartTime = time.time()
        self.TimeX = 0
        self.ValueX = 0
        self.TimeY = 0
        self.ValueY = 0
        self.Index = 0
        self.Slope = 0
        if self.Size > 1:
            tpwl = self.PWL[self.Index].split(",")
            if (len(tpwl) == 2):
                self.TimeY = float(tpwl[0])
                self.ValueY = float(tpwl[1])
        self.getNextTupel()
        self.Stop = False

    def getNextTupel(self):
        self.Index += 1
        self.TimeX = self.TimeY
        self.ValueX = self.ValueY
        if self.Index < self.Size:
            tpwl = self.PWL[self.Index].split(",")
            if (len(tpwl) == 2):
                self.TimeY = float(tpwl[0])
                self.ValueY = float(tpwl[1])
        else:
            self.Stop = True
        # Kurvenparameter berechnen
        DiffTime = self.TimeY - self.TimeX
        DiffValue = self.ValueY - self.ValueX
        if DiffTime > 0:
            self.Slope = 1.0*DiffValue/DiffTime
        else:
            self.Slope = 0.0

    def getNextValue(self):
        elapsedTime = time.time() - self.StartTime
        if elapsedTime > self.TimeY:
            self.getNextTupel()
        currentTime = elapsedTime - self.TimeX
        value = currentTime * self.Slope + self.ValueX
        return value

    def getStop(self):
        return self.Stop

    def runPWL(self):
        self.StartTime = time.time()
        return self.StartTime


class Peaktech1885():
    def __init__(self, port=-1):
        self.comport = port
        self.ser = serial.Serial()
        self.baudrate = 9600
        self.timeout = 0.1
        self.name = MODUL_NAME
        self.pwl = None
        self.thread = None
        self.delay = 0.5

    def iocontrol(self, cmd=""):
        rc = 1
        iCMD = ""
        iADD = ADDR_PEAKTECH1885
        iPAR = ""
        cmdl = cmd.split("=")
        if len(cmdl) > 1:
            cmd = cmdl[0]
            if cmd == "U":
                iCMD = "VOLT"
                iPAR = "%03d" % int(float(cmdl[1])*10)
            elif cmd == "DELAY":
                self.delay = float(cmdl[1])/1000  # da in ms
            elif cmd == "pwl":
                if self.thread != None:
                    self.thread.pwl_stop()
                    time.sleep(1)
                    del self.thread
                    self.thread = None
                if self.pwl != None:
                    del self.pwl
                    self.pwl = None
                self.pwl = Pwl(pwl=cmdl[1])
                self.thread = Pwl_thread(
                    device=self, pwl=self.pwl, delay=self.delay)
                self.thread.pwl_start()
        else:
            if cmd == "Ein":
                iCMD = "SOUT"
                iPAR = "0"
            elif cmd == "Aus":
                iCMD = "SOUT"
                iPAR = "1"
            else:
                pass

        if len(iCMD) > 0:
            txd = iCMD + iADD + iPAR + "\r"
            rxd = ""
            ccc = ""
            if self.ser != None:
                self.ser.write(txd.encode())
                for i in range(10):
                    time.sleep(0.005)
                    nr = self.ser.in_waiting
                    if nr > 2:
                        rxd = self.ser.read(size=nr)
                        ccc = rxd.decode()
                        if ccc.find("OK") >= 0:
                            rc = 0
                        break
            #print(" -> 1885: %s = %s, rc = %d [%d*]" % (txd.rstrip(), ccc.rstrip(), rc, i))

        return rc

    def read(self):
        pass

    def write(self, value):
        pass

    def init(self):
        self.iocontrol(cmd="Aus")
        self.iocontrol(cmd="Aus")
        self.iocontrol(cmd="U=24")

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
