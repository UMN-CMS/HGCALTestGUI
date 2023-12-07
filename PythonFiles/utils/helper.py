# Helper functions for smooth operation

from pathlib import Path

def get_install_path():

    return Path(__file__).parent.parent.parent

def get_logging_path():

    return get_install_path() / "logs/HGCALTestGUI.log"

