#################################################################################

import tkinter as tk
import logging
import PythonFiles
import os
    
#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.TestFailedPopup')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'w', format=FORMAT, level=logging.DEBUG)


class TestFailedPopup():
    
    #################################################

    def __init__(self, parent, previous_frame, data_holder):
        self.test_failed_popup(parent, previous_frame, data_holder)
    
    #################################################

    # Function to make retry or continue window if the test fails
    def test_failed_popup(self, parent, previous_frame, data_holder):
        self.data_holder = data_holder
        logger.info("TestFailedPopup: A test has been failed. Prompting user for 'retry' or 'continue'.")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Test Failed") 
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup, 
            text = " The board failed the test. \n Would you like to retry? ",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2, pady = 25)

        # Creates retry and continue buttons
        btn_retry = tk.Button(
             frm_popup,
             width = 8,
             height = 2,
             text = "Retry", 
             relief = tk.RAISED,
             font = ('Arial', 12),
             command = lambda: self.retry_function(parent, previous_frame)
             )
        btn_retry.grid(column = 0, row = 1)

        btn_continue = tk.Button(
            frm_popup,
            width = 8,
            height = 2,
            text = "Continue",
            relief = tk.RAISED,
            font = ('Arial', 12),
            command = lambda: self.continue_function()
        )
        btn_continue.grid(column = 1, row = 1)

    #################################################
    
    # Called when the no button is pressed to destroy popup and return you to the main window
    def retry_function(self, parent, previous_frame):
        self.popup.destroy()
        parent.set_frame(previous_frame)
        
    #################################################

    # Called to continue on in the testing procedure
    def continue_function(self):
        self.popup.destroy()

    #################################################


#################################################################################
