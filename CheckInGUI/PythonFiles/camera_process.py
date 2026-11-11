"""Owns the camera reader (econ_reader.py) subprocess so the GUI can restart it.

When the camera's USB connection is bumped, the device vanishes and the reader exits
(or is left holding a dead device). After the cable is replugged, restart() starts a
fresh reader that opens the camera again: the same thing a GUI restart used to do.
"""
import atexit
import logging
import subprocess
import sys
import threading
from pathlib import Path

logger = logging.getLogger('HGCAL_VI.PythonFiles.camera_process')

READER_SCRIPT = Path(__file__).parent.resolve() / 'econ_reader.py'
STOP_TIMEOUT_S = 5.0   # time the reader gets to shut down cleanly before it is killed
                       # (its decode worker alone may take ~2 s)


class CameraProcess:

    def __init__(self, script=READER_SCRIPT):
        self.script = str(script)
        self.proc = None
        self._lock = threading.RLock()  # restart() may run on a background thread
        atexit.register(self.stop)   # don't leave the camera window behind when the GUI exits

    def start(self):
        with self._lock:
            self._start()

    def _start(self):
        if self.is_running():
            return
        try:
            self.proc = subprocess.Popen([sys.executable, self.script],
                                         cwd=str(Path(self.script).parent))
            logger.info(f"Camera reader started with PID {self.proc.pid}")
        except OSError as e:
            self.proc = None
            logger.error(f"Could not start camera reader {self.script}: {e}")

    def stop(self):
        with self._lock:
            self._stop()

    def _stop(self):
        proc, self.proc = self.proc, None
        if proc is None or proc.poll() is not None:
            return
        logger.info(f"Stopping camera reader (PID {proc.pid})")
        proc.terminate()   # the reader catches SIGTERM and releases the camera
        try:
            proc.wait(timeout=STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            logger.warning("Camera reader did not stop in time; killing it")
            proc.kill()
            proc.wait()

    def restart(self):
        with self._lock:
            self._stop()
            self._start()

    def is_running(self):
        proc = self.proc
        return proc is not None and proc.poll() is None
