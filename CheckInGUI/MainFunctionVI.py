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
import yaml
from pathlib import Path


# Creates a main function to initialize the GUI
def main():
    
    logging.FileHandler(guiLogPath + "visual_gui.log", mode='a')
    
    filepath = os.path.dirname(os.path.abspath(__file__))
    print( "Current path is: %s" % (filepath))

    node = socket.gethostname()
    print(socket.gethostname())
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

    masterCfg = import_yaml("{}/Configs/Wagon_cfg.yaml".format(filepath))

    board_cfg = masterCfg


    main_window = GUIWindow(board_cfg)
    

def import_yaml(config_path):

    return yaml.safe_load(open(config_path,"r"))





if __name__ == "__main__":
    main()
