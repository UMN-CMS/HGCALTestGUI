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
from pathlib import Path


# Creates a main function to initialize the GUI
def main():
    
    logging.handlers.TimedRotatingFileHandler(guiLogPath + "visual_gui.log", when="midnight", interval=1)
    
    filepath = os.path.dirname(os.path.abspath(__file__))
    print("Current path is: %s" % filepath)
    logging.debug("Current path is: %s" % filepath)

    node = socket.gethostname()
    print(socket.gethostname())
    logging.debug(socket.gethostname())

    wagon_GUI_computers = [ 
        "cmsfactory1.cmsfactorynet",
        "cmsfactory2.cmsfactorynet",
        "cmsfactory4.cmsfactorynet",
        "cmsfactory5.cmsfactorynet",
        "cmslab4.umncmslab",
        "127.0.1.1",
    ]   
    engine_GUI_computers = [ 

    ]   
    
    try:
        if sys.argv[1] is not None:
            config_path = sys.argv[1]
            print(config_path)
    except:
        print("Opting for custom configuration setup called below")
        config_path = "{}/Configs/Wagon_cfg.yaml".format(filepath)

    masterCfg = import_yaml(config_path)

    board_cfg = masterCfg


    main_window = GUIWindow(board_cfg, filepath)
    

def import_yaml(config_path):

    return yaml.safe_load(open(config_path,"r"))





if __name__ == "__main__":
    main()
