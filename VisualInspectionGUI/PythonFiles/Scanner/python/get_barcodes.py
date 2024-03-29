import subprocess
import time
import signal
import ctypes
import os
#import PythonFiles
libc = ctypes.CDLL("libc.so.6")

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
    proc = subprocess.Popen('./PythonFiles/Scanner/bin/runScanner', stdout=subprocess.PIPE, preexec_fn=set_pdeathsig(signal.SIGTERM))
    print("Starting scanner")
    return proc
    #for line in proc.stdout:
    #    if line is not None:
    #        conn.send(line.strip().decode('utf-8'))
    #        return

def listen(serial, proc):
    for line in proc.stdout:
        if line is not None:
            print(line.strip().decode('utf-8'))
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

    print(parse_xml(serial[0]))

if __name__=="__main__":
    run_scanner()
