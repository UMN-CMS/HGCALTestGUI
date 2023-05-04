#!/TestingEnv/bin/python

# Importing necessary modules
import multiprocessing as mp
import socket
# Imports the GUIWindow
from PythonFiles.GUIWindow import GUIWindow
from PythonFiles.utils.SUBClient import SUBClient
import os
import sys

# Creates a task of creating the GUIWindow
def task_GUI(conn, queue, board_cfg):
    # creates the main_window as an instantiation of GUIWindow
    main_window = GUIWindow(conn, queue, board_cfg)

# Creates a task of creating the SUBClient
def task_SUBClient(conn, queue):
    # Creates the SUBSCRIBE Socket Client
    sub_client = SUBClient(conn, queue)

def run(board_cfg):    
    # Creates a Pipe for the SUBClient to talk to the GUI Window
    conn_SUB, conn_GUI = mp.Pipe()

    queue = mp.Queue()

    guiLogPath = "/shared/{}/GUILogs/".format(os.getlogin())

    if os.path.exists(guiLogPath):
        os.makedirs(guiLogPath)

    # Turns creating the GUI and creating the SUBClient tasks into processes
    process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, queue, board_cfg))
    process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue,))
    

    # Starts the processes
    process_GUI.start()
    process_SUBClient.start()

    # Should hold the code at this line until the GUI process ends
    process_GUI.join()

    try:
        conn_SUB.close()
        conn_GUI.close()
    except:
        print("Pipe close is unnecessary.")

    try:
        # Cleans up the SUBClient process
        process_SUBClient.terminate()
    except:
        print("Terminate is unnecessary.")
        pass

def main(args):
    pass

if __name__ == "__main__":

    curpath = os.path.abspath(os.curdir)
    print( "Current path is: %s" % (curpath))

    node = socket.gethostname()
    print(socket.gethostname())
    wagon_GUI_computers = [
        "cmsfactory1.cmsfactorynet.umn.edu",
        "cmslab4.umncmslab",
    ]
    engine_GUI_computers = [

    ]
   
    board_cfg = None

    if node in wagon_GUI_computers:
        from TestConfigs.Wagon_cfg import masterCfg

        print("Hostname setup for wagon testing. Initializing Wagon Test GUI...")

        board_cfg = masterCfg

    run(board_cfg)
