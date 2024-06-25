import subprocess
import time
import signal
import ctypes
import os
#import PythonFiles
libc = ctypes.CDLL("libc.so.6")

from multiprocessing import Process, Manager, Pipe

# these functions are run individually in ScanScene

# decodes hexadecimal into the serial number
def decode(hex_str):
    serial = ""
    for h in hex_str.split(" "):
        serial += bytes.fromhex(h).decode("ASCII")

    return serial

# parses the hexadecimal value grabbed
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

def scan(path):
    proc = subprocess.Popen('{}/PythonFiles/Scanner/bin/runScanner'.format(path), stdout=subprocess.PIPE, preexec_fn=set_pdeathsig(signal.SIGTERM))
    print("Starting scanner")
    return proc

def listen(serial, proc):
    for line in proc.stdout:
        if line is not None:
            print(line.strip().decode('utf-8'))
            serial.append(line.strip().decode('utf-8'))
            return


def run_scanner():
    manager = Manager()
    serial = manager.list()

    proc = scan()
    listener = Process(target=listen, args=(serial, proc))

    listener.start()

    # holds until something is scanned
    listener.join()

    print(parse_xml(serial[0]))

if __name__=="__main__":
    run_scanner()
