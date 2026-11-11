"""Tiny localhost link from the camera reader (econ_reader.py) to the GUI (EconScanScene).

The reader runs as its own process, so a decoded ID is sent as one UDP datagram to
127.0.0.1. UDP keeps the reader from ever blocking or crashing when the GUI isn't
listening; the datagram is simply dropped.

Kept dependency-free so both sides can import it (econ_reader.py imports it as a
sibling module, the GUI as PythonFiles.econ_link).
"""
import socket

HOST = '127.0.0.1'
PORT = 50555
PREFIX = b'ECON:'   # ignore stray datagrams that aren't ours


def send_code(text):
    """Send one decoded ID to the GUI. Returns True if the datagram went out."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(PREFIX + text.encode('utf-8'), (HOST, PORT))
        return True
    except OSError:
        return False


class Receiver:
    """Non-blocking receiver for the GUI side; call poll() from a Tk after() loop."""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, PORT))   # raises OSError if another GUI holds the port
        self.sock.setblocking(False)

    def poll(self):
        """Return the newest code waiting (older queued ones are dropped), or None."""
        latest = None
        while True:
            try:
                data, _ = self.sock.recvfrom(4096)
            except (BlockingIOError, InterruptedError):
                return latest
            except OSError:
                return latest
            if data.startswith(PREFIX):
                text = data[len(PREFIX):].decode('utf-8', 'replace').strip()
                if text:
                    latest = text

    def close(self):
        self.sock.close()
