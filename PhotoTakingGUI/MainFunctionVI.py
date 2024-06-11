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


# Creates a main function to initialize the GUI
def main():
    
    logging.FileHandler(guiLogPath + "visual_gui.log", mode='a')
    
    curpath = os.path.abspath(os.curdir)
    print( "Current path is: %s" % (curpath))

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
   
    board_cfg = None

    from TestConfigs.Engine_cfg import masterCfg

    print("Hostname setup for wagon testing. Initializing Wagon Test GUI...")

    board_cfg = masterCfg


    main_window = GUIWindow(board_cfg)
    






if __name__ == "__main__":
    main()
