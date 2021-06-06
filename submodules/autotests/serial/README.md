# Automatisierte RS-232 und IBIS Loopback-Tests

## Einleitung

Dieses Verzeichnis enthält Tests für den RS-232-Port und den IBIS-Port vom Cortex-Chip der Ticket.Box. Sie haben die folgenden Voraussetzungen:

- Python 3 und [pytest](https://docs.pytest.org/en/latest/) im Image
- Für RS232-Tests: i.MX6- und Cortex-RS-232-Ports mit einem [Nullmodem-Kabel](https://de.wikipedia.org/wiki/Nullmodem-Kabel) zusammen verbunden
- Für IBIS-Tests: die Fähigkeit, einen Kurzschluss auf den Sendebus zu erzeugen (z.B. durch Überbrücken mit einer Büroklammer)

## RS-232-Tests

### Starten
Die Tests sind als pytest-Module geschrieben, bestehend aus zwei separaten Skripten: `test_rs232.py` und `test_rs232_dauertest.py`. Das Erste erledigt vergleichsweise schnelle Sende- und Empfangstests, das Zweite macht Dauertests. Dank ihr Dateinamen werden sie von pytest automatisch entdeckt und ausgeführt, wenn man das `pytest`-Kommando ohne Argumente aufruft.

Die Skripte können je nach Bedarf auch an pytest übergeben worden oder sogar direkt in der Shell gestartet werden:

```
$ pytest test_rs232.py
```
```
$ ./test_rs232.py
```

Standardmäßig druckt pytest sehr wenig Information über ausgeführte Tests aus:

```
root@phycard-imx6-ivu-ticketbox:/harddisk/tests# ./test_rs232.py                               
===================================== test session starts =====================================
platform linux -- Python 3.7.8, pytest-5.1.3, py-1.8.0, pluggy-0.13.0
rootdir: /harddisk/tests
collected 768 items

test_rs232.py ......................................................................... [  9%]
```

Um mehr Details zu bekommen gibt es den Parameter `-v`:

```
root@phycard-imx6-ivu-ticketbox:/harddisk/tests# ./test_rs232.py -v
===================================== test session starts =====================================
platform linux -- Python 3.7.8, pytest-5.1.3, py-1.8.0, pluggy-0.13.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /harddisk/tests
collected 768 items

test_rs232.py::Test_RS232::test_RTS[19200,8,N,1] PASSED                                 [  0%]
test_rs232.py::Test_RS232::test_CTS[19200,8,N,1] PASSED                                 [  0%]
test_rs232.py::Test_RS232::test_send[19200,8,N,1-1] PASSED                              [  0%]
test_rs232.py::Test_RS232::test_receive[19200,8,N,1-1] PASSED                           [  0%]
test_rs232.py::Test_RS232::test_send[19200,8,N,1-4] PASSED                              [  0%]
test_rs232.py::Test_RS232::test_receive[19200,8,N,1-4] PASSED                           [  0%]
```

### Testkonfigurationen mit Profilen auswählen

Das Testmodul führt seine Tests auf **Profile** aus. Profile sind eine Menge an Parameterwerten für die Port-Konfiguration. Die Tests werden auf alle möglichen Kombinationen davon ausgeführt.

Es gibt unterschiedliche Profile. Wir haben pytest erweitert, damit man sie mit dem Parameter `-P` auf der Kommandozeile angeben kann:

```
$ ./test_rs232.py -P common
```

Ohne Angabe vom Profil mit dem Parameter nutzen die Tests das common-Profil.

#### Das common-Profil

"common" enthält die gängigste Parameterkonfigurationen, bzw. diejenige davon die relativ schnell zu testen sind. `test_rs232.py` braucht damit ca. 60 Sekunden.

- Baudraten: 19200, 57600, 115200, 230400.
- Datenbits: 8, 7.
- Paritäten: keine (N), gerade (E), ungerade (O).
- Stop-Bits: 1, 2.

#### Das quick-Profil

"quick" wird vorwiegend als Smoketest für die serielle Leitung oder die Tests selbst benutzt.

`test_rs232.py` läuft damit in ca. 3 Sekunden.

- Baudraten: 115200.
- Datenbits: 8.
- Paritäten: keine (N).
- Stop-Bits: 1.

#### Das spec-Profil

"spec" nutzt die in unserer Spezifikation 'UART2 - RS232 Architektur IVU.box' aufgelistete Werte und gilt somit als minimaler Abnahmetest.

`test_rs232.py` läuft damit in ca. 25 Sekunden.

- Baudraten: 9600, 38400, 57600, 115200, 230400.
- Datenbits: 8.
- Paritäten: keine (N).
- Stop-Bits: 1.

#### Das abnahme-Profil

"abnahme" nutzt die Kombinationen wie sie in dem Abnahmedokument der Ticket-Box für CE6 und CE7 stehen.

`test_rs232.py` läuft damit in ca. 120 Sekunden.

- Baudraten: 1200, 9600, 19200, 57600.
- Datenbits: 8.
- Paritâten: keine (N).
- Stop-Bits: 1.

#### Das full-Profil

"full" testet alle unterstützte Kombinationen ausführlich.

`test_rs232.py` läuft damit weit über 20 Minuten.

- Baudraten: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400.
- Datenbits: 8, 7. Die API unterstützt auch 6 und 5, aber sie funktionieren scheinbar nicht.
- Paritäten: alle, nämlich keine (N), gerade (E), ungerade (O), Space (S), Mark (M).
- Stop-Bits: 1, 1,5, 2.

## IBIS-Tests

Da das Mainboard A über einen IBIS-Slave-Port verfügt, der geräteintern mit dem IBIS-Master-Port gekreuzt zusammenverkabelt ist, hat unsere Ticket.Box ein eingebautes IBIS-Loopback das wir für die Tests nutzen.

### Verfügbare Tests
Die Tests sind als pytest-Module geschrieben, bestehend aus diesen Skripten:

1. `test_ibis.py` &ndash; Sende- und Empfangstests für Datenlängen zwischen 1 und 300 Bytes
2. `test_ibis_dauertest.py` &ndash; Dauertests über 100 Zyklen
3. `test_ibis_kurzschluss.py` &ndash; Kurzschlusstests auf Sende- und Antwortbus

Sie sind ähnlich wie die im Abschnitt "Start" der RS-232-Tests oben aufgeführten Skripte, werden ähnlich gestartet, und akzeptieren dieselben Parameter soweit sie nicht RS-232-Spezifisch sind. IBIS hat hingegen keine Testprofile.

### Sende- und Empfangstests

`test_ibis.py` sendet Daten hin und her zwischen dem Master- und Slave-Port mit unterschiedlichen Datengrößen, standardmäßig alle Größen zwischen 1 und 300 Bytes. Die Endgröße kann bei Bedarf mit dem Parameter `-S` oder `--ibis-max-data-size` adjustiert werden. Das folgende Kommando testet also alle Größen zwischen 1 und 20 Bytes statt 300:

```
$ ./test_ibis.py -S 20
```

### Dauertests

`test_ibis_dauertest.py` sendet eine kleine Datenmenge hin und her zwischen Master und Slave, standardmäßig 100 mal. Diese Anzahl kann bei Bedarf mit dem Parameter `-C` oder `--ibis-endurance-cycles` adjustiert werden. Das folgende Kommando testet also über 20 Zyklen statt 100:

```
$ ./test_ibis_dauertest.py -C 20
```

### Kurzschlusstests

`test_ibis_kurzschluss.py` testet die Kurschlussdetektierung auf dem Master-Port, beide auf dem Sendebus und auf dem Antwortbus.

Der Antwortbus kann aus dem Slave-Port kurzgeschlossen werden und es ist also möglich es mit den Bordmitteln im Gerät zu testen. 

Bei dem Sendebus ist dies hingegen nicht möglich und der Kurzschluss muss von Außen durch ein Zusammenschalten der Sender-Datenleitung (WBSD) mit der Sendermasse (WBSM) verursacht werden. Verfügt der Testplatz über eine IBIS-Sub-D9-Buchse, sind dafür die Pins 1 und 6 z.B. mit einer Büroklammer zu überbrücken:

```
      6   7   8   9
    _________________
╔══╱═>O   O   O   O  ╲
╚═╱>O   O   O   O   O ╲
  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    1   2   3   4   5
```

Ohne Automatisierungsmöglichkeit sind die Tests auf die ausführende Tester:innen für die manuelle Überbrückung angewiesen. `test_ibis_kurzschluss.py` muss deswegen im Verbose-Modus gestartet werden:
```
$ ./test_ibis_kurzschluss.py -v
=========================================================================================== test session starts ===========================================================================================
platform linux -- Python 3.7.8, pytest-5.1.3, py-1.8.0, pluggy-0.13.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /harddisk/tests
collected 6 items

test_ibis_kurzschluss.py::Test_IBIS_Short_Circuits::test_default_cts_dsr_values PASSED
test_ibis_kurzschluss.py::Test_IBIS_Short_Circuits::test_please_short_the_sender_bus_within_the_next_20_seconds
```

Im Testfall `test_please_short_the_sender_bus_within_the_next_20_seconds` wartet das Skript 20 Sekunden, dass Tester:innen den Sendebus manuell kurzschliessen. Dann erfolgt der eigentliche Test, und danach bittet das Skript mit `test_please_unshort_the_sender_bus_within_the_next_20_seconds` darum die Überbrückung wegzumachen damit den Rest der Tests erledigt werden kann.

```
test_ibis_kurzschluss.py::Test_IBIS_Short_Circuits::test_please_short_the_sender_bus_within_the_next_20_seconds PASSED
test_ibis_kurzschluss.py::Test_IBIS_Short_Circuits::test_sender_bus_short_circuit PASSED
test_ibis_kurzschluss.py::Test_IBIS_Short_Circuits::test_please_unshort_the_sender_bus_within_the_next_20_seconds PASSED
```

## Bemerkungen

Da pytest verwendet wird bringt er sehr viele Funktionalität "out of the box" mit, besonders im Bereich Logging und Reporting. Ein JUnit-Bericht über die Testausführung lässt sich z.B. mit dem richtigen Parameter direkt schreiben: 

```
$ ./test_rs232.py --junit-xml=rs232-report.xml
```