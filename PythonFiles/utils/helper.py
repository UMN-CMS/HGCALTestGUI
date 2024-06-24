# Helper functions for smooth operation

from pathlib import Path
import os

def get_install_path():

    return Path(__file__).parent.parent.parent

def get_logging_path():
    return os.getenv("HOME") + "/shared/gui.log"

