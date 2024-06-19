#################################################################################

# importing necessary modules
import multiprocessing as mp
import logging, time
import tkinter.ttk as ttk
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
class ScanScene(ttk.Frame):
    
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

        self.create_style(parent)
       
    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')

    # Creates a thread for the scanning of a barcode
    # Needs to be updated to run the read_barcode function in the original GUI
    # can see more scanner documentation in the Visual Inspection GUI
    def scan_QR_code(self, master_window):
        
        if self.use_scanner:

            self.ent_full.config(state = 'normal')
            self.ent_full.delete(0,END)
            self.master_window = master_window
            self.hide_rescan_button()

            sys.path.insert(1,'/home/hgcal/WagonTest/Scanner/python')

            from ..Scanner.python.get_barcodes import scan, listen, parse_xml

            manager = mp.Manager()
            full_id = manager.list()
            print(full_id)

            self.ent_full.config(state = 'normal')

            logger.info("ScanScene: Beginning scan...")
            self.scanner = scan()
            self.listener = mp.Process(target=listen, args=(full_id, self.scanner))

            self.listener.start()
                
            while 1 > 0:

                try:
                    self.master_window.update()
                except:
                    pass
                if not len(full_id) == 0:
                    self.data_holder.set_full_ID( parse_xml(full_id[0]))

                    self.listener.terminate()
                    self.scanner.terminate()
                
                    self.ent_full.delete(0,END)
                    self.ent_full.insert(0, str(self.data_holder.get_full_ID()))
                    self.ent_full.config(state = 'disabled')
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
        
        super().__init__(self.master_frame, width=1300-213, height = 700)

        logger.info("ScanScene: Frame has been created.")
        # Create a photoimage object of the QR Code
        QR_image = Image.open("{}/Images/QRimage.png".format(PythonFiles.__path__[0]))
        QR_PhotoImage = iTK.PhotoImage(QR_image)
        QR_label = ttk.Label(self, image=QR_PhotoImage)
        QR_label.image = QR_PhotoImage

        # the .grid() adds it to the Frame
        QR_label.grid(column=1, row = 0)

        Scan_Board_Prompt_Frame = ttk.Frame(self,)
        Scan_Board_Prompt_Frame.grid(column=0, row = 0)

        # creates a Label Variable, different customization options
        lbl_scan = ttk.Label(
            master= Scan_Board_Prompt_Frame,
            text = "Scan the QR Code on the Board",
            font = ('Arial', 18)
        )
        lbl_scan.pack(padx = 50, pady = 50)

        # Create a label to label the entry box
        lbl_full = ttk.Label(
            Scan_Board_Prompt_Frame,
            text = "Full ID: ",
            font = ('Arial', 16)
        )
        lbl_full.pack(padx = 20)

        # Entry for the full id to be displayed. Upon Scan, update and disable?
        global ent_full
        
        # Creating intial value in entry box
        user_text = tk.StringVar(self)
        
        # Creates an entry box
        self.ent_full = tk.Entry(
            Scan_Board_Prompt_Frame,
            font = ('Arial', 16),
            textvariable= user_text, 
            )
        self.ent_full.pack(padx = 50)

        # Traces an input to show the submit button once text is inside the entry box
        user_text.trace(
            "w", 
            lambda name, 
            index, 
            mode, 
            sv=user_text: self.show_submit_button()
            )

        # Rescan button creation
        self.btn_rescan = ttk.Button(
            Scan_Board_Prompt_Frame,
            text="Rescan",
            #padx = 20,
            #pady =10,
            #relief = tk.RAISED,
            command = lambda:  self.scan_QR_code(self.master_frame)
            )
        self.btn_rescan.pack(pady=30)

        # Submit button creation
        self.btn_submit = ttk.Button(
            Scan_Board_Prompt_Frame,
            text="Submit",
            #padx = 20,
            #pady = 10,
            #relief = tk.RAISED,
            command= lambda:  self.btn_submit_action(parent)
            )
        self.btn_submit.pack()

        #creates a frame for the label info
        label_frame = ttk.Frame(self)
        label_frame.grid(column=0, row = 1)

        self.label_major = ttk.Label(
            label_frame,
            text='',
            font = ('Arial', 16),
            )
        self.label_major.pack(padx=50, pady=10)

        self.label_sub = ttk.Label(
            label_frame,
            text='',
            font = ('Arial', 16),
            )
        self.label_sub.pack(padx=50, pady=10)

        self.label_sn = ttk.Label(
            label_frame,
            text='',
            font = ('Arial', 16),
            )
        self.label_sn.pack(padx=50, pady=10)
            

        # Creating frame for logout button
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 1, row = 1, sticky= 'se')

        # Creating the logout button
        btn_logout = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.pack(anchor = 'se', padx = 10, pady = 20)

        # Creating the help button
        btn_help = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
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

        self.data_holder.set_full_ID(self.ent_full.get())
        _parent.update_config()
        if self.data_holder.getGUIcfg().get_if_use_DB():
            self.data_holder.check_if_new_board() 

        self.data_holder.update_location(self.ent_full.get())
        _parent.create_test_frames(self.data_holder.data_dict['queue'])
        _parent.set_frame_postscan()

        self.EXIT_CODE = 0


    #################################################

    # Function for the log out button
    def btn_logout_action(self, _parent):

        self.EXIT_CODE = 1 
        
        if self.use_scanner:
            self.listener.terminate()
            self.scanner.terminate()

         # Send user back to login frame
        _parent.set_frame_login_frame() 

        self.EXIT_CODE = 0

    #################################################

    # Function to activate the submit button
    def show_submit_button(self):
        self.data_holder.decode_label(self.ent_full.get())
        self.btn_submit["state"] = "active"
        try:
            self.label_major['text'] = 'Major Type: ' + self.data_holder.label_info['Major Type']
            self.label_sub['text'] = 'Subtype: ' + self.data_holder.label_info['Subtype']
            self.label_sn['text'] = 'Serial Number: ' + self.data_holder.label_info['SN']
            self.label_major.update()
            self.label_sub.update()
            self.label_sn.update()
        except TypeError:
            self.label_major['text'] = ''
            self.label_sub['text'] = ''
            self.label_sn['text'] = ''
            self.label_major.update()
            self.label_sub.update()
            self.label_sn.update()


    #################################################

    # Function to disable to the submit button
    def hide_submit_button(self):
        self.btn_submit["state"] = "disabled"
        self.label_major['text'] = ''
        self.label_sub['text'] = ''
        self.label_sn['text'] = ''
        self.label_major.update()
        self.label_sub.update()
        self.label_sn.update()

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
