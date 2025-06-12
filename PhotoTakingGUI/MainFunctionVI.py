# Need to make the log file path before any imports
import os
guiLogPath = "/home/{}/GUILogs/".format(os.getlogin())

if not os.path.exists(guiLogPath):
    os.makedirs(guiLogPath)

import sys
sys.path.append("..")

# Imports the GUIWindow
from PythonFiles.GUIWindow import GUIWindow
import socket
import logging
import logging.handlers
import yaml

logger = logging.getLogger('HGCAL_Photo')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    fh = logging.handlers.TimedRotatingFileHandler(guiLogPath + "photo_gui.log", when="midnight", interval=1)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

class StreamToLogger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ''

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logger, logging.DEBUG)
#sys.stderr = StreamToLogger(logger, logging.ERROR)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


# Creates a main function to initialize the GUI
def main():
    logger.info("Creating new instance of HGCAL_Photo")
       
    filepath = os.path.dirname(os.path.abspath(__file__))
    logger.info("Current path is: %s" % (filepath))

    node = socket.gethostname()
    logger.info("Node is: %s" % node)

    try:
        config_path = sys.argv[1]
    except:
        config_path = "{}/Configs/Wagon_cfg.yaml".format(filepath)

    logger.info('Board Config: %s' % config_path)
    masterCfg = import_yaml(config_path)

    main_window = GUIWindow(masterCfg, filepath)
    

def import_yaml(config_path):

    return yaml.safe_load(open(config_path,"r"))
    



if __name__ == "__main__":
    main()
