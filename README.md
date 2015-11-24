#FingerprintScannerRaspberryPi
Fingerprint Scanner using serial (UART) on Raspberry Pi
These files are tested with Raspberry Pi B+ running rasbian and python 3.
The serial port must be changed from serial console to serial control.
Pin 2 = 5VDC
Pin 6 = Ground
Pin 8 = TX from Rpi
Pin 7 = Input for exit button (Active Low)*
Pin 10 = Rx to Rpi
Pin 40 = Output to relay*

*IO pins utilize 3.3VDC
