#!/TestingEnv/bin/python

# Including information about both Engine and Wagon GUIs


# Need to make the log file path before any imports
import os
from pathlib import Path
from PythonFiles.utils.helper import get_logging_path

guiLogPath = "{}".format(get_logging_path())
guiLogDir = "/".join(guiLogPath.split("/")[:-1])
print("Writing log file to {}".format(guiLogPath))

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
import yaml
from pathlib import Path

# create logger with 'HGCALTestGUI'
logger = logging.getLogger('HGCALTestGUI')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(guiLogPath)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info("Creating new instance of HGCALTestGUI")

# Creates a task of creating the GUIWindow
def task_GUI(conn, conn_trigger, queue, board_cfg):
    # creates the main_window as an instantiation of GUIWindow
    main_window = GUIWindow(conn, conn_trigger, queue, board_cfg)

# Creates a task of creating the SUBClient
def task_SUBClient(conn, queue, board_cfg, sub_pipe):
    # Creates the SUBSCRIBE Socket Client
    sub_client = SUBClient(conn, queue, board_cfg, sub_pipe)

# Function to create the handler of the type specified in the config file
def task_LocalHandler(gui_cfg, conn_trigger, local_pipe):

    LocalHandler(gui_cfg, conn_trigger, local_pipe)

def task_SSHHandler(gui_cfg, conn_trigger, queue):

    SSHHandler(gui_cfg, conn_trigger, queue)

def run(board_cfg):    
    # Creates a Pipe for the SUBClient to talk to the GUI Window
    conn_SUB, conn_GUI = mp.Pipe()

    # Create another pipe to trigger the tests when needed
    if board_cfg["TestHandler"]["name"] != "ZMQ":
        conn_trigger_GUI, conn_trigger_Handler = mp.Pipe()
        
    # Creates a queue to send information to the testing window
    queue = mp.Queue()

    #logging.FileHandler(guiLogPath + "gui.log", mode='a')

    # Turns creating the GUI and creating the SUBClient tasks into processes
    if board_cfg["TestHandler"]["name"] == "Local":
        # Creates a Queue to connect SUBClient and Handler
        q = mp.Queue()
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, conn_trigger_GUI, queue, board_cfg))
        process_Handler = mp.Process(target = task_LocalHandler, args=(board_cfg, conn_trigger_Handler, q))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, board_cfg, q))

    elif board_cfg["TestHandler"]["name"] == "SSH":
        q = mp.Queue()
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, conn_trigger_GUI, queue, board_cfg))
        process_Handler = mp.Process(target = task_SSHHandler, args=(board_cfg, conn_trigger_Handler, q))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, board_cfg, q))

    else: 
        process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, None, queue, board_cfg))
        process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue, board_cfg, None))

    # Starts the processes
    process_GUI.start()
    if board_cfg["TestHandler"]["name"] == "Local" or board_cfg['TestHandler']['name'] == 'SSH':
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
        print("Pipe close is unnecessary.")

    try:
        # Cleans up the SUBClient process
        process_SUBClient.terminate()
        process_Handler.kill()
    except:
        print("Terminate is unnecessary.")
        pass


def board_config(sn):

    board_cfg = None
    
    if sn == None:
        if any(node in y for y in  wagon_GUI_computers):
            from TestConfigs.Wagon_cfg import masterCfg

            print("Hostname setup for wagon testing. Initializing Wagon Test GUI...")

            board_cfg = masterCfg
        
        if any(node in y for y in engine_GUI_computers):
            from TestConfigs.Engine_cfg import masterCfg

            print("Hostname setup for engine testing. Initializing Engine Test GUI...")

            board_cfg = masterCfg


        run(board_cfg)

    else:
        update_config(sn)

def import_yaml(config_path):

    return yaml.safe_load(open(config_path,"r"))

def main(args):
    pass

if __name__ == "__main__":

    try:
        if sys.argv[1] is not None:
            config_path = sys.argv[1]
            print(config_path)
    except:
        print("Opting for custom configuration setup called below")
        config_path = None

    curpath = os.path.abspath(os.curdir)
    print( "Current path is: %s" % (curpath))

    node = socket.gethostname()
    print(socket.gethostname())
    wagon_GUI_computers = [
        "cmsfactory1.cmsfactorynet",
        "cmsfactory5.cmsfactorynet",
        "cmslab4.umncmslab",
        "cmsfactory2.cmsfactorynet",
    ]
    engine_GUI_computers = [
        "cmsfactory4.cmsfactorynet",
    ]

    if config_path is not None:
        board_cfg = import_yaml(config_path)

        run(board_cfg)
    elif any((node in x for x in wagon_GUI_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/Wagon_cfg.yaml")

        run(board_cfg)

    elif any((node in x for x in wagon_GUI_computers)):
        board_cfg = import_yaml(Path(__file__).parent / "Configs/Engine_cfg.yaml")

        run(board_cfg)

    else:
        board_config(None)
   
