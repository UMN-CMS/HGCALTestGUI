#################################################################################

# importing necessary modules
import multiprocessing as mp
import logging, time
import tkinter as tk
import tkinter.ttk as ttk
import sys, time
from tkinter import *
from turtle import back
from PIL import ImageTk as iTK
from PIL import Image
import PythonFiles
import os


#################################################################################

logger = logging.getLogger('HGCAL_GUI')
FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


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
        self.is_current_scene = False
        self.EXIT_CODE = 0
        # Runs the initilize_GUI function, which actually creates the frame
        # params are the same as defined above
        self.initialize_GUI(parent, master_frame)
    
    def create_style(self, _parent):
        self.s = ttk.Style()
 
        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
 
        self.s.theme_use('awdark')


    # Creates a thread for the scanning of a barcode
    # Needs to be updated to run the read_barcode function in the original GUI
    def scan_QR_code(self, master_window):

        self.ent_full.config(state = 'normal')
        self.ent_full.delete(0,END)
        self.master_window = master_window
        self.hide_rescan_button()

        #sys.path.insert(1,'/home/hgcal/WagonTest/Scanner/python')

        from ..Scanner.python.get_barcodes import scan, listen, parse_xml

        manager = mp.Manager()
        full_id = manager.list()

        self.ent_full.config(state = 'normal')

        print("\nScanScene: Beginning scan...\n")
        logging.info("ScanScene: Beginning scan...")
        self.scanner = scan(self.parent.main_path)
        self.listener = mp.Process(target=listen, args=(full_id, self.scanner))

        self.listener.start()

        while 1 > 0:

            try:
                self.master_window.update()
            except:
                pass
            if not len(full_id) == 0:
                # takes in the full id scanned, parses the hexadecimal in ASCII
                # and sends it to the data holder
                self.data_holder.set_full_ID( parse_xml(full_id[0]))

                self.listener.terminate()
                self.scanner.terminate()

                self.ent_full.delete(0,END)
                self.ent_full.insert(0, str(self.data_holder.get_full_ID()))
                self.ent_full.config(state = 'disabled')
                self.show_rescan_button()
                break

            elif self.EXIT_CODE:
                logging.info("ScanScene: Exit code received. Terminating processes.")
                self.listener.terminate()
                self.scanner.terminate()
                logging.info("ScanScene: Processes terminated successfully.")
                break
            else:
                time.sleep(.01)

        logging.info("ScanScene: Scan complete.")

    # Creates the GUI itself
    def initialize_GUI(self, parent, master_frame):

        self.master_frame = master_frame
        self.parent = parent

        super().__init__(self.master_frame,style = 'ScanScene.TFrame', width = 1350, height = 850)

        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        self.create_style(parent)

        lbl_frm = ttk.Frame(self)
        lbl_frm.grid(column=1, row = 0 )


        logging.info("ScanScene: Frame has been created.")
        # Create a photoimage object of the QR Code
        QR_image = Image.open("{}/Images/WagonExample.png".format(PythonFiles.__path__[0]))
        QR_PhotoImage = iTK.PhotoImage(QR_image)
        QR_label = ttk.Label(lbl_frm, image=QR_PhotoImage)
        QR_label.image = QR_PhotoImage

        # the .grid() adds it to the Frame
        QR_label.grid(column=0, row = 0, sticky='new', pady = (0, 45))

        # Create a photoimage object of the QR Code
        QR_image2 = Image.open("{}/Images/EngineExample.png".format(PythonFiles.__path__[0]))
        QR_PhotoImage = iTK.PhotoImage(QR_image2)
        QR_label2 = ttk.Label(lbl_frm, image=QR_PhotoImage)
        QR_label2.image = QR_PhotoImage

        # the .grid() adds it to the Frame
        QR_label2.grid(column=0, row = 1, sticky='new')

        Scan_Board_Prompt_Frame = ttk.Frame(self)
        Scan_Board_Prompt_Frame.grid(column=0, row = 0, sticky='nsew')

        Scan_Board_Prompt_Frame.grid_columnconfigure(0, weight=1)
        Scan_Board_Prompt_Frame.grid_columnconfigure(1, weight=1)
        QR_label.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # creates a Label Variable, different customization options
        lbl_scan = ttk.Label(
            master= Scan_Board_Prompt_Frame,
            text = "Scan the QR Code on the Board",
            font = ('Arial',36)
        )
        lbl_scan.pack(padx = 50, pady = (85, 100))

        # Create a label to label the entry box
        lbl_full = ttk.Label(
            Scan_Board_Prompt_Frame,
            text = "Full ID:",
            font = ('Arial', 18)
        )
        lbl_full.pack(padx = 20, pady = 15)

        # Creating intial value in entry box
        user_text = tk.StringVar(self)

        # Creates an entry box
        self.ent_full = ttk.Entry(
            Scan_Board_Prompt_Frame,
            font = ('Arial', 16),
            textvariable= user_text,
            width = 50
            )
        self.ent_full.pack(padx = (75, 50))

        #self.ent_snum.mark_set("insert", "%d.%d" % (1, 1))

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
            command = lambda:  self.scan_QR_code(self.master_window)
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
        btn_logout.pack(anchor = 'se', padx = 10, pady = 10)

        # Creating the help button
        btn_help = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.pack(anchor = 's', padx = 10)




        # Locks frame size to the master_frame size
        self.grid_propagate(0)



    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    def get_submit_action(self):
        return self.btn_submit_action

    def get_parent(self):
        return self.parent
    #################################################


    #################################################

    # Function for the submit button
    def btn_submit_action(self, _parent):

        self.EXIT_CODE = 0

        self.data_holder.set_full_ID(self.ent_full.get())
        self.data_holder.check_if_new_board()
        self.data_holder.update_location(self.ent_full.get())
        _parent.update_config()
        _parent.set_frame_postscan()

    #################################################

    # Function for the log out button
    def btn_logout_action(self, _parent):

        logging.debug("ScanScene: Closing the scanner from the logout button action.")
        self.EXIT_CODE = 1
        self.listener.terminate()
        self.scanner.terminate()


         # Send user back to login frame
        _parent.set_frame_login_frame()
        master_frame.after(500, self.set_frame_login_frame)

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
        logging.info("ScanScene: Terminating scanner proceses.")
        try:
            self.scanner.kill()
            self.listener.terminate()
            self.EXIT_CODE = 1
        except:
            logging.info("ScanScene: Processes could not be terminated.")
