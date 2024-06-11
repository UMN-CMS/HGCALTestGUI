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
from PythonFiles import Images
import os
 

#################################################################################


logging.getLogger('PIL').setLevel(logging.WARNING)
logger = logging.getLogger('HGCAL_GUI')

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/visual_gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# creating the Photo Frame's class (called PhotoScene) to be instantiated in the GUIWindow
# instantiated as scan_frame by GUIWindow
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.
class PhotoScene(tk.Frame):
    
    #################################################

    # Runs upon creation
    def __init__(self, parent, master_frame, data_holder):


        self.master_frame = master_frame
        self.parent = parent

        self.data_holder = data_holder
        self.is_current_scene = False
        
        self.EXIT_CODE = 0
        # Runs the initilize_GUI function, which actually creates the frame
        # params are the same as defined above
        self.initialize_GUI(parent, master_frame)
        

       # Creates the GUI itself
    def initialize_GUI(self, parent, master_frame):
        
        self.master_frame = master_frame
        self.parent = parent

        super().__init__(self.master_frame, width = 1105, height = 850)

        logging.info("PhotoScene: Frame has been created.")
        # Create a photoimage object of the Engine
        self.Engine_image = Image.open("{}/Images/{}".format(PythonFiles.__path__[0], self.parent.image_name))
        self.Engine_image = self.Engine_image.resize((400, 300), Image.LANCZOS)
        self.Engine_PhotoImage = iTK.PhotoImage(self.Engine_image)
        self.Engine_label = tk.Label(self)
        self.Engine_label.configure(image=self.Engine_PhotoImage)
        self.Engine_label.image = self.Engine_PhotoImage

        # the .grid() adds it to the Frame
        self.Engine_label.grid(column=1, row = 1)

        Scan_Board_Prompt_Frame = Frame(self)
        Scan_Board_Prompt_Frame.grid(column=1, row = 0)

        Blank_Frame = Frame(self)
        Blank_Frame.grid(column = 0, row = 1, padx = 100, pady = 10)

        self.photo_title = tk.StringVar()
        self.photo_title.set("Photo Title")

        # creates a Label Variable, different customization options
        lbl_scan = tk.Label(
            master= Scan_Board_Prompt_Frame,
            textvariable = self.photo_title,
            font = ('Arial', 14)
        )
        lbl_scan.pack(padx = 50, pady = 50)

        # Create a label to label the entry box
        lbl_correct = tk.Label(
            Scan_Board_Prompt_Frame,
            text = "Does this look correct?",
            font = ('Arial', 16)
        )
        lbl_correct.pack(padx = 20)

        # Entry for the serial number to be displayed. Upon Scan, update and disable?
        global ent_correct
        
        # Creating intial value in entry box
        user_text = tk.StringVar(self)
        
        # Creates an entry box
        #self.ent_correct = tk.Entry(
        #    Scan_Board_Prompt_Frame,
        #    font = ('Arial', 16),
        #    textvariable= user_text, 
        #    )
        #self.ent_correct.pack(padx = 50)

        # Traces an input to show the submit button once text is inside the entry box
        #user_text.trace(
        #    "w", 
        #    lambda name, 
        #    index, 
        #    mode, 
        #    sv=user_text: self.show_submit_button()
        #    )

        # Try again button creation
        self.btn_rescan = tk.Button(
            Scan_Board_Prompt_Frame,
            text="Try Again",
            padx = 20,
            pady =10,
            relief = tk.RAISED,
            command = lambda:  self.try_again_button(parent)
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
        self.btn_submit.pack(padx = 8, pady = 5)

        # Creating frame for logout button
        frm_logout = tk.Frame(self)
        frm_logout.grid(column = 2, row = 1, sticky= 'se')


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

    # Function for the submit button
    def btn_submit_action(self, _parent):
        
        #TODO Do something with the dataholder here with the photo
        self.data_holder.send_image(img_idx=0)
        _parent.next_frame_camera_frame()


    #################################################

    # Function for the log out button
    def btn_logout_action(self, _parent):

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

    def help_action(self, _parent):
        _parent.help_popup(self)


    #################################################
    
    def set_text(self, index):
        self.image_index = index

        title = self.data_holder.get_photo_list()[index]["name"]
        descr = self.data_holder.get_photo_list()[index]["desc_short"]

        updated_title = title + "\n--------------------\n" + descr

        self.photo_title.set(updated_title)

        


    #################################################

    def try_again_button(self, _parent):
        _parent.return_frame_camera_frame()


    #################################################
    # Function to disable to the rescan button
    def hide_rescan_button(self):
        self.btn_rescan["state"] = "disabled"

    #################################################
        
    def remove_widgets(self, parent):
        for widget in self.winfo_children():
            widget.destroy()

    def update(self):
        self.Engine_image = Image.open("{}/Images/{}".format(PythonFiles.__path__[0], self.parent.image_name))
        

        print("\nIn PhotoScene 'update()' method\n")
        # Create a photoimage object of the Engine
        print("\n\n\nThe Image Path is: {} \n\n".format(self.parent.image_name))
        self.Engine_image = self.Engine_image.resize((712, 400), Image.LANCZOS)
        self.Engine_PhotoImage = iTK.PhotoImage(self.Engine_image)
        self.Engine_label = tk.Label(self)
        self.Engine_label.configure(image=self.Engine_PhotoImage)
        self.Engine_label.image = self.Engine_PhotoImage

        # the .grid() adds it to the Frame
        self.Engine_label.grid(column=1, row = 1)


 
    def kill_processes(self):
        return
