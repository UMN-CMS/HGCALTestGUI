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
class AdminScanScene(ttk.Frame):
    
    #################################################

    # Runs upon creation
    def __init__(self, parent, master_frame, data_holder):
        
        self.data_holder = data_holder

        self.use_scanner = self.data_holder.get_use_scanner()

        self.is_current_scene = False
        
        self.EXIT_CODE = 0

        self.master_frame = master_frame

        self.parent = parent

        super().__init__(self.master_frame, width=1300-213, height = 800)

        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        # Runs the initilize_GUI function, which actually creates the frame
        # params are the same as defined above
        self.initialize_GUI(parent)

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

            logger.info("AdminScanScene: Beginning scan...")
            self.scanner = scan()
            self.listener = mp.Process(target=listen, args=(full_id, self.scanner))

            self.listener.start()
                
            while 1 > 0:

                try:
                    self.master_window.update()
                except:
                    pass
                if not len(full_id) == 0:
                    board = parse_xml(full_id[0])

                    self.listener.terminate()
                    self.scanner.terminate()
                
                    self.ent_full.delete(0,END)
                    self.ent_full.insert(0, str(board))
                    self.ent_full.config(state = 'disabled')
                    self.show_rescan_button()
                    break

                elif self.EXIT_CODE:
                    logger.info("AdminScanScene: Exit code received. Terminating processes.")
                    self.listener.terminate()
                    self.scanner.terminate()
                    logger.info("AdminScanScene: Processes terminated successfully.")
                    break
                else:
                    time.sleep(.01)
                
            logger.info("AdminScanScene: Scan complete.")

    # Creates the GUI itself
    def initialize_GUI(self, parent):

        logger.info("AdminScanScene: Frame has been created.")
        # Create a photoimage object of the QR Code

        QR_image = Image.open("{}/Images/QRimage.png".format(PythonFiles.__path__[0]))
        QR_PhotoImage = iTK.PhotoImage(QR_image)
        QR_label = ttk.Label(self, image=QR_PhotoImage)
        QR_label.image = QR_PhotoImage

        # the .grid() adds it to the Frame
        QR_label.grid(column=1, row = 1, sticky='new')

        Scan_Board_Prompt_Frame = ttk.Frame(self, width = 1105, height = 650)
        Scan_Board_Prompt_Frame.grid(column=0, row = 1, sticky='nsew')
        
        Button_Frame1 = ttk.Frame(self)
        Button_Frame1.grid(column=1, row=0, sticky='ew')

        Button_Frame2 = ttk.Frame(self)
        Button_Frame2.grid(column=1, row=2, sticky='ew')

        #resizing
        Scan_Board_Prompt_Frame.grid_columnconfigure(0, weight=1)
        Scan_Board_Prompt_Frame.grid_columnconfigure(1, weight=1)
        QR_label.grid_columnconfigure(0, weight=1)
        Button_Frame1.grid_columnconfigure(0, weight=1)
        Button_Frame2.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # creates a Label Variable, different customization options
        self.lbl_scan = ttk.Label(
            master= Scan_Board_Prompt_Frame,
            text = "Scan the QR Code on the Board",
            font = ('Arial', 18)
        )
        self.lbl_scan.grid(column=0, row=0, sticky='we')

        # Create a label to label the entry box
        lbl_full = ttk.Label(
            Scan_Board_Prompt_Frame,
            text = "Full ID: ",
            font = ('Arial', 16)
        )
        lbl_full.grid(column=0, row=2)

        # Entry for the full id to be displayed. Upon Scan, update and disable?
        global ent_full
        
        # Creating intial value in entry box
        self.user_text = tk.StringVar(self)
        
        # Creates an entry box
        self.ent_full = tk.Entry(
            Scan_Board_Prompt_Frame,
            font = ('Arial', 16),
            textvariable= self.user_text,
            )
        self.ent_full.grid(column=0, row=3)


        # Traces an input to show the submit button once text is inside the entry box
        self.user_text.trace(
            "w", 
            lambda name, 
            index, 
            mode, 
            sv=self.user_text: self.show_submit_button()
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
        self.btn_rescan.grid(column=0, row=5, padx=10, pady=5)

        # Submit button creation
        self.btn_submit = ttk.Button(
            Scan_Board_Prompt_Frame,
            text="Submit",
            #padx = 20,
            #pady = 10,
            #relief = tk.RAISED,
            command= lambda:  self.btn_submit_action(parent)
            )
        self.btn_submit.grid(column=0, row=6, padx=10, pady=5)

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
        btn_logout.grid(column=0, row=1, sticky='ne', padx=10, pady=10)

        # Creating the help button

        btn_help = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.grid(column=0, row=0, sticky='ne', padx=10, pady=10)


    def update_frame(self, parent, index):
        self.ent_full.delete(0,END)
        if self.data_holder.tester_type == 'Wagon':
            self.index = list(self.data_holder.wagon_tester_info)[index]
            self.lbl_scan['text'] = 'Scan the ' + self.index
        if self.data_holder.tester_type == 'Engine':
            self.index = list(self.data_holder.engine_tester_info)[index]
            self.lbl_scan['text'] = 'Scan the ' + self.index


    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    #################################################    


    # Function for the submit button
    def btn_submit_action(self, _parent):
       
        self.EXIT_CODE = 1 

        if self.data_holder.tester_type == 'Wagon':
            self.data_holder.wagon_tester_info[self.index] = self.ent_full.get()
        if self.data_holder.tester_type == 'Engine':
            self.data_holder.engine_tester_info[self.index] = self.ent_full.get()

        self.EXIT_CODE = 0

        _parent.next_frame_admin_scan()


    def get_submit_action(self):
        return self.btn_submit_action

    def get_parent(self):
        return self.parent

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
        logger.info("AdminScanScene: Terminating scanner proceses.")
        try:
            if self.use_scanner:
                self.scanner.kill()
                self.listener.terminate()
            self.EXIT_CODE = 1
        except:
            logger.info("AdminScanScene: Processes could not be terminated.")


##########################################################

class interposer_Popup():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.confirm_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder):
        self.data_holder = data_holder
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Select Interposer Type") 
        self.popup.geometry("200x100+550+350")
        self.popup.pack_propagate(1) 
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = ttk.Frame(self.popup, width=300, height=200)
        frm_popup.grid(row=0, column=0, sticky='nsew')

        # Creates label in the frame
        lbl_popup = ttk.Label(
            frm_popup, 
            text = "Select Interposer Type",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        # Creates retry and continue buttons
        btn_east = ttk.Button(
             frm_popup,
             text = "East", 
             command = lambda: self.east_function(self.parent)
             )
        btn_east.grid(column = 1, row = 1)

        btn_west = ttk.Button(
            frm_popup,
            text = "West",
            command = lambda: self.west_function(self.parent)
        )
        btn_west.grid(column = 0, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)


    #################################################
    
    def east_function(self, _parent):
        self.popup.destroy()
        self.data_holder.wagon_tester_info['interposer_type'] = 'East'
        
    #################################################

    def west_function(self, _parent):
        self.popup.destroy()
        self.data_holder.wagon_tester_info['interposer_type'] = 'West'



###############################################################


class finished_Popup():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.confirm_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder):
        self.data_holder = data_holder
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Done") 
        self.popup.geometry("300x150+550+350")
        self.popup.pack_propagate(1) 
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = ttk.Frame(self.popup, width=300, height=200)
        frm_popup.grid(row=0, column=0, sticky='nsew')

        # Creates label in the frame
        lbl_popup = ttk.Label(
            frm_popup, 
            text = "Finished Scanning Tester Info",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        # Creates retry and continue buttons
        btn_ok = ttk.Button(
             frm_popup,
             text = "OK", 
             command = lambda: self.east_function(self.parent)
             )
        btn_ok.grid(column = 1, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)


    #################################################
    
    def east_function(self, _parent):
        self.popup.destroy()
        

