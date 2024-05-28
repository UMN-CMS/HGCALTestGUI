#################################################################################

# importing necessary modules
import multiprocessing as mp
import logging, time
import tkinter as tk
import sys, time
from tkinter import *
from turtle import back
from PIL import ImageTk as iTK
from PIL import Image
import PythonFiles
import os
 

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ScanScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# creating the Scan Frame's class (called ScanScene) to be instantiated in the GUIWindow
# instantiated as scan_frame by GUIWindow
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.
class ScanScene(tk.Frame):
    
    #################################################

    # Runs upon creation
    def __init__(self, parent, master_frame, data_holder):
        
        self.data_holder = data_holder

        self.use_scanner = self.data_holder.get_use_scanner()

        self.is_current_scene = False
        
        self.EXIT_CODE = 0
        # Runs the initilize_GUI function, which actually creates the frame
        # params are the same as defined above
        self.initialize_GUI(parent, master_frame)
        

    # Creates a thread for the scanning of a barcode
    # Needs to be updated to run the read_barcode function in the original GUI
    # can see more scanner documentation in the Visual Inspection GUI
    def scan_QR_code(self, master_window):
        
        if self.use_scanner:

            self.ent_snum.config(state = 'normal')
            self.ent_snum.delete(0,END)
            self.master_window = master_window
            self.hide_rescan_button()

            sys.path.insert(1,'/home/hgcal/WagonTest/Scanner/python')

            from ..Scanner.python.get_barcodes import scan, listen, parse_xml

            manager = mp.Manager()
            serial = manager.list()
            print(serial)

            self.ent_snum.config(state = 'normal')

            logger.info("ScanScene: Beginning scan...")
            self.scanner = scan()
            self.listener = mp.Process(target=listen, args=(serial, self.scanner))

            self.listener.start()
                
            while 1 > 0:

                try:
                    self.master_window.update()
                except:
                    pass
                if not len(serial) == 0:
                    self.data_holder.set_serial_ID( parse_xml(serial[0]))

                    self.listener.terminate()
                    self.scanner.terminate()
                
                    self.ent_snum.delete(0,END)
                    self.ent_snum.insert(0, str(self.data_holder.get_serial_ID()))
                    self.ent_snum.config(state = 'disabled')
                    self.show_rescan_button()
                    break

                elif self.EXIT_CODE:
                    logger.info("ScanScene: Exit code received. Terminating processes.")
                    self.listener.terminate()
                    self.scanner.terminate()
                    logger.info("ScanScene: Processes terminated successfully.")
                    break
                else:
                    time.sleep(.01)
                
            logger.info("ScanScene: Scan complete.")

    # Creates the GUI itself
    def initialize_GUI(self, parent, master_frame):
        
        self.master_frame = master_frame
        
        super().__init__(self.master_frame, width=870, height = 500)

        logger.info("ScanScene: Frame has been created.")
        # Create a photoimage object of the QR Code
        QR_image = Image.open("{}/Images/QRimage.png".format(PythonFiles.__path__[0]))
        QR_PhotoImage = iTK.PhotoImage(QR_image)
        QR_label = tk.Label(self, image=QR_PhotoImage)
        QR_label.image = QR_PhotoImage

        # the .grid() adds it to the Frame
        QR_label.grid(column=1, row = 0)

        Scan_Board_Prompt_Frame = Frame(self,)
        Scan_Board_Prompt_Frame.grid(column=0, row = 0)

        # creates a Label Variable, different customization options
        lbl_scan = tk.Label(
            master= Scan_Board_Prompt_Frame,
            text = "Scan the QR Code on the Board",
            font = ('Arial', 18)
        )
        lbl_scan.pack(padx = 50, pady = 50)

        # Create a label to label the entry box
        lbl_snum = tk.Label(
            Scan_Board_Prompt_Frame,
            text = "Serial Number:",
            font = ('Arial', 16)
        )
        lbl_snum.pack(padx = 20)

        # Entry for the serial number to be displayed. Upon Scan, update and disable?
        global ent_snum
        
        # Creating intial value in entry box
        user_text = tk.StringVar(self)
        
        # Creates an entry box
        self.ent_snum = tk.Entry(
            Scan_Board_Prompt_Frame,
            font = ('Arial', 16),
            textvariable= user_text, 
            )
        self.ent_snum.pack(padx = 50)

        # Traces an input to show the submit button once text is inside the entry box
        user_text.trace(
            "w", 
            lambda name, 
            index, 
            mode, 
            sv=user_text: self.show_submit_button()
            )

        # Rescan button creation
        self.btn_rescan = tk.Button(
            Scan_Board_Prompt_Frame,
            text="Rescan",
            padx = 20,
            pady =10,
            relief = tk.RAISED,
            command = lambda:  self.scan_QR_code(self.master_frame)
            )
        self.btn_rescan.pack(pady=30)

        # Submit button creation
        self.btn_submit = tk.Button(
            Scan_Board_Prompt_Frame,
            text="Submit",
            padx = 20,
            pady = 10,
            relief = tk.RAISED,
            command= lambda:  self.btn_submit_action(parent)
            )
        self.btn_submit.pack()

        # Creating frame for logout button
        frm_logout = tk.Frame(self)
        frm_logout.grid(column = 1, row = 1, sticky= 'se')

        # Creating the logout button
        btn_logout = tk.Button(
            frm_logout,
            relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.pack(anchor = 'se', padx = 10, pady = 20)

        # Creating the help button
        btn_help = tk.Button(
            frm_logout,
            relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.pack(anchor = 's', padx = 10, pady = 20)


        


        # Locks frame size to the master_frame size
        self.grid_propagate(0)

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    #################################################    


    # Function for the submit button
    def btn_submit_action(self, _parent):
        
        self.EXIT_CODE = 1 

#        if self.use_scanner:
#            self.listener.terminate()
#            self.scanner.terminate()

        self.data_holder.set_serial_ID(self.ent_snum.get())
        if self.data_holder.getGUIcfg().get_if_use_DB():
            self.data_holder.check_if_new_board() 
        _parent.update_config()
        _parent.create_test_frames(self.data_holder.data_dict['queue'])
        _parent.set_frame_postscan()


    #################################################

    # Function for the log out button
    def btn_logout_action(self, _parent):

        self.EXIT_CODE = 1 
        
        if self.use_scanner:
            self.listener.terminate()
            self.scanner.terminate()

         # Send user back to login frame
        _parent.set_frame_login_frame() 

    #################################################

    # Function to activate the submit button
    def show_submit_button(self):
        self.btn_submit["state"] = "active"

    #################################################

    # Function to disable to the submit button
    def hide_submit_button(self):
        self.btn_submit["state"] = "disabled"

    #################################################

    # Function to activate the rescan button
    def show_rescan_button(self):
        self.btn_rescan["state"] = "active"

    #################################################

    # Function to disable to the rescan button
    def hide_rescan_button(self):
        self.btn_rescan["state"] = "disabled"

    #################################################
        
    def kill_processes(self):
        logger.info("ScanScene: Terminating scanner proceses.")
        try:
            if self.use_scanner:
                self.scanner.kill()
                self.listener.terminate()
            self.EXIT_CODE = 1
        except:
            logger.info("ScanScene: Processes could not be terminated.")
