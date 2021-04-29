# Ansteuerung USB OPTO-4 OUT mini der Fa. Kolter
# peb 22.03.2012 drv_usbopto4out.py
# V 1.0 22.03.2012 Neuerstellung
# V 1.1 23.03.2012 Ruecklesen der Ausgaenge auf der Hardware
# V 1.2 30.03.2012 Wert clrOut3 von 9 auf 11

# Ansteuerung ueber DTR, TXD und RTS
# Data   => DTR
# Clock  => TXD
# Strobe => RTS

# Vor Test mit diesem Modul in der Systemsteuerung den ComPort ausfindig machen
# Unter Win7 gehen auch ComPorts > 10 mit Angabe der Nummer
# Fuer Python muss man den ComPort aus der Systemsteuerung um 1 weniger angeben

import time
import serial
MODUL_NAME = "USB OPTO-4 OUT"


class Usbopto4out():
    def __init__(self, port=-1, output=0):
        self.comport = port
        self.baudrate = 9600
        self.timeout = 0.1
        self.output = output
        self.ser = serial.Serial()
        # if self.comport >= 0:
        #    self.open()
        #    # self.write(self.output)
        self.name = MODUL_NAME

    def iocontrol(self, cmd="clrAll"):
        """manage and control output ports

        Args:
            cmd (str, optional): supported commands: setOut1, setOut2, setOut3, setOut4, clrOut1, clrOut2, clrOut3, clrOut4, setAll, clrAll. Defaults to "clrAll".

        Raises:
            Exception: command unknown
        """
        if cmd == "setOut1":
            self.write(self.output | 1)
        elif cmd == "setOut2":
            self.write(self.output | 2)
        elif cmd == "setOut3":
            self.write(self.output | 4)
        elif cmd == "setOut4":
            self.write(self.output | 8)
        elif cmd == "clrOut1":
            self.write(self.output & 14)  # = 15 - 1
        elif cmd == "clrOut2":
            self.write(self.output & 13)  # = 15 - 2
        elif cmd == "clrOut3":
            self.write(self.output & 11)  # = 15 - 4
        elif cmd == "clrOut4":
            self.write(self.output & 7)  # = 15 - 8
        elif cmd == "setAll":
            self.write(15)
        elif cmd == "clrAll":
            self.write(0)
        else:
            raise Exception("Invalid command")

    def read(self):
        """get the current output port state

        Returns:
            int: binary number representing the output 1=on 0=off
        """
        if self.ser.is_open:
            # Eingaenge zwischenspeichern
            self.ser.rts = False
            self.ser.dtr = True
            self.ser.dtr = False
            # Register auslesen
            self.ser.rts = False
            v = 0
            for i in range(4):
                # 1 mal takten
                self.ser.break_condition = False
                self.ser.break_condition = True
                if self.ser.cts:
                    v = v | ( 1 << i )
            self.output = v
        return self.output

    def write(self, value):
        """set output
        O1 first bit
        O2 second bit
        O3 third bit
        O4 fourth bit

        Args:
            value (int): binary number representing the output 1=on 0=off
        """
        if self.ser.is_open:
            self.output = value
            self.ser.rts = True            # Daten senden
            self.ser.dtr = value & 1
            self.ser.break_condition = False
            self.ser.break_condition = True
            self.ser.dtr = value & 2
            self.ser.break_condition = False
            self.ser.break_condition = True
            self.ser.dtr = value & 4
            self.ser.break_condition = False
            self.ser.break_condition = True
            self.ser.dtr = value & 8
            self.ser.break_condition = False
            self.ser.break_condition = True
            self.ser.rts = False            # Datenuebernahme

    def init(self):  # Beispielkode siehe unit1.pas, Funktion allerdings unklar
        self.ser.break_condition = False
        self.ser.dtr = False
        self.ser.rts = False
        for i in range(8):
            self.ser.dtr = False
            self.ser.rts = True
            self.ser.dtr = False
            self.ser.rts = False

    def open(self):
        try:
            self.ser.port = self.comport
            self.ser.baudrate = self.baudrate
            self.ser.timeout = self.timeout
            self.ser.open()
            self.init()
        except:
            pass

    def close(self):
        self.ser.close()
