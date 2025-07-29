#!/TestingEnv/bin/python

# Including information about both Engine and Wagon GUIs


# Need to make the log file path before any imports
import os
from pathlib import Path
from PythonFiles.utils.helper import get_logging_path

guiLogPath = "{}".format(get_logging_path())
guiLogDir = "/".join(guiLogPath.split("/")[:-1])

if not os.path.exists(guiLogDir):
    os.makedirs(guiLogDir)

# Importing necessary modules
import multiprocessing as mp
import socket
# Imports the GUIWindow and Handlers
from PythonFiles.GUIWindow import GUIWindow
from PythonFiles.utils.SUBClient import SUBClient
from PythonFiles.update_config import update_config
from PythonFiles.utils.LocalHandler import LocalHandler
from PythonFiles.utils.SSHHandler import SSHHandler
import sys
import logging
import logging.handlers
from logging.handlers import QueueHandler, QueueListener
import yaml
from pathlib import Path

# create logger with 'HGCALTestGUI'
logger = logging.getLogger('HGCALTestGUI')
logger.setLevel(logging.DEBUG)

# avoid duplicate handlers  
if not logger.handlers:
    # file handler which rotates every day
    fh = logging.handlers.TimedRotatingFileHandler(guiLogPath, when="midnight", interval=1)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
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


# Creates a task of creating the GUIWindow
def task_GUI(conn, conn_trigger, queue, board_cfg, curpath):
    # creates the main_window as an instantiation of GUIWindow
    try:
        main_window = GUIWindow(conn, conn_trigger, queue, board_cfg, curpath)
    except Exception:
        logger.error("Uncaught exception in task_GUI", exc_info=True)
        raise

# Creates a task of creating the SUBClient
def task_SUBClient(conn, queue, board_cfg, sub_pipe):
    # Creates the SUBSCRIBE Socket Client
    try:
        sub_client = SUBClient(conn, queue, board_cfg, sub_pipe)
    except Exception:
        logger.error("Uncaught exception in task_SUBClient", exc_info=True)
        raise


# Function to create the handler of the type specified in the config file
def task_LocalHandler(gui_cfg, conn_trigger, local_pipe):

    try:
        LocalHandler(gui_cfg, conn_trigger, local_pipe)
    except Exception:
        logger.error("Uncaught exception in task_LocalHandler", exc_info=True)
        raise

def task_SSHHandler(gui_cfg, host_cfg, conn_trigger, queue):

    try:
        SSHHandler(gui_cfg, host_cfg, conn_trigger, queue)
    except Exception:
        logger.error("Uncaught exception in task_SSHHandler", exc_info=True)
        raise

def run(board_cfg, curpath, host_cfg):    

    # Creates a Pipe for the SUBClient to talk to the GUI Window
    conn_SUB, conn_GUI = mp.Pipe()

    # Create another pipe to trigger the tests when needed
    if host_cfg["TestHandler"]["name"] != "ZMQ":
        conn_trigger_GUI, conn_trigger_Handler = mp.Pipe()
        
    # Creates a queue to send information to the testing window
    queue = mp.Queue()

    #logging.FileHandler(guiLogPath + "gui.log", mode='a')

    # Turns creating the GUI and creating the SUBClient tasks into processes
    if host_cfg["TestHandler"]["name"] == "Local":
        # Creates a Queue to connect SUBClient and Handler
        q = mp.Queue()
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, conn_trigger_GUI, queue, board_cfg, curpath))
        process_Handler = mp.Process(target = task_LocalHandler, args=(board_cfg, conn_trigger_Handler, q))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, board_cfg, q))

    elif host_cfg["TestHandler"]["name"] == "SSH":
        q = mp.Queue()
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, conn_trigger_GUI, queue, board_cfg, curpath))
        process_Handler = mp.Process(target = task_SSHHandler, args=(board_cfg, host_cfg, conn_trigger_Handler, q))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, board_cfg, q))

    else: 
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, None, queue, board_cfg, curpath))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, host_cfg, None))

    # Starts the processes
    process_GUI.start()
    if host_cfg["TestHandler"]["name"] == "Local" or host_cfg['TestHandler']['name'] == 'SSH':
        process_Handler.start()
    process_SUBClient.start()

    # holds the code at this line until the GUI process ends
    process_GUI.join()
    
    try:
        #closes multiprocessing connections
        conn_SUB.close()
        conn_GUI.close()
        conn_trigger_GUI.close()
        conn_trigger_Handler.close()
    except:
        logger.debug("Pipe close is unnecessary.")

    try:
        # Cleans up the SUBClient process
        process_SUBClient.terminate()
        process_Handler.kill()
    except:
        logger.debug("Terminate is unnecessary.")
        pass


def import_yaml(config_path):

    return yaml.safe_load(open(config_path,"r"))

def main(args):
    pass

if __name__ == "__main__":

    logger.info("Creating new instance of HGCALTestGUI")

    try:
        if sys.argv[1] is not None:
            config_path = sys.argv[1]
    except:
        config_path = None

    try:
        if sys.argv[2] is not None:
            host_path = sys.argv[2]
    except:
        if config_path:
            host_path = sys.argv[1]
        else:
            host_path = None

    curpath = Path(__file__).parent.absolute()
    logger.info("Current path is: %s" % curpath)

    node = socket.gethostname()
    logger.info("Node is: %s" % socket.gethostname())

    ld_wagon_computers = [
        "cmsfactory4.cmsfactorynet",
        "cmsfactory5.cmsfactorynet",
    ]
    hd_wagon_computers = []
    ld_engine_computers = [
        "cmsfactory1.cmsfactorynet",
        "cmsfactory2.cmsfactorynet",
    ]
    hd_engine_computers = []

    if config_path is not None:
        board_cfg = import_yaml(config_path)
        host_cfg = import_yaml(host_path)
        logger.info("Board Config: " + config_path)
        logger.info("Host Config: " + host_path)

        run(board_cfg, curpath, host_cfg)
    elif any((node in x for x in ld_wagon_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/LD_Wagon_cfg.yaml")

        run(board_cfg, curpath, board_cfg)

    elif any((node in x for x in hd_wagon_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/HD_Wagon_cfg.yaml")

        run(board_cfg, curpath, board_cfg)

    elif any((node in x for x in ld_engine_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/LD_Engine_cfg.yaml")

        run(board_cfg, curpath, board_cfg)

    elif any((node in x for x in hd_engine_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/HD_Engine_cfg.yaml")

        run(board_cfg, curpath, board_cfg)

    else:
        board_cfg = import_yaml(Path(__file__).parent / "Configs/LD_Wagon_cfg.yaml")

        run(board_cfg, curpath, board_cfg)

