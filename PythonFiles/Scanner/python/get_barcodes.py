import subprocess
import time
import signal
import ctypes
from pathlib import Path
#import PythonFiles
import logging
import serial
from serial.tools import list_ports
import time

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scanner.python.get_barcodes')

from multiprocessing import Process, Manager, Pipe

def decode(hex_str):
    serial = ""
    for h in hex_str.split(" "):
        serial += bytes.fromhex(h).decode("ASCII")

    return serial

def parse_xml(inXML):
    if "<" not in inXML:
        return
    else:
        splitting = inXML.split("datalabel")
        return decode(splitting[1][1:-2])

def set_pdeathsig(sig = signal.SIGTERM):
    def callable():
        return libc.prctl(1, sig)
    return callable

def scan():
    proc = subprocess.Popen(Path(__file__).parent.parent / 'bin/runScanner', stdout=subprocess.PIPE, preexec_fn=set_pdeathsig(signal.SIGTERM))
    logger.info('Starting scanner')
    return proc
    #for line in proc.stdout:
    #    if line is not None:
    #        conn.send(line.strip().decode('utf-8'))
    #        return

def get_serial_port():
    ports = list_ports.comports()
    for p in ports:
        if any(keyword in p.description for keyword in ["Prolific", "FTDI", "USB-to-Serial", "CP210x", "Abstract"]):
            return p.device

    logger.error("No scanner port found")
    return None

def scan_from_serial(serial_list, stop_flag):
    port = get_serial_port()
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:

            while not stop_flag.is_set():
                line = ser.readline().decode('utf-8').strip()
                if line:
                    serial_list.append(line)
                    break
    except serial.SerialException as e:
        logger.exception(f"Serial Error: {e}")


def listen(serial, proc):
    for line in proc.stdout:
        if line is not None:
            serial.append(line.strip().decode('utf-8'))
            return

    #while not output_found:
    #    output = conn.recv()
    #    if output is not None:
    #        serial.append(output)
    #        output_found = True
    #    else:
    #        print('Still waiting')

def run_scanner():
    manager = Manager()
    serial = manager.list()

    proc = scan()
    listener = Process(target=listen, args=(serial, proc))

    listener.start()

    listener.join()

    logger.info('Scanner: %s' % parse_xml(serial[0]))

if __name__=="__main__":
    run_scanner()
