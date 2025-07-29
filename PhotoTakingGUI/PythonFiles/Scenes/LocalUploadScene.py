
#################################################################################

# importing necessary modules
import multiprocessing as mp
import logging, time
import tkinter.ttk as ttk
import tkinter as tk
import sys, time
from tkinter import *
from tkinter import messagebox as mb
from turtle import back
from PIL import ImageTk as iTK
from PIL import Image
import PythonFiles
import os
 

#################################################################################

logger = logging.getLogger('HGCAL_Photo.PythonFiles.Scenes.LocalUploadScene')


# creating the Scan Frame's class (called ScanScene) to be instantiated in the GUIWindow
# instantiated as scan_frame by GUIWindow
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.
class LocalUploadScene(ttk.Frame):
    
    #################################################

    # Runs upon creation
    def __init__(self, parent, master_frame, data_holder):
        
        self.data_holder = data_holder
        
        self.EXIT_CODE = 0

        self.master_frame = master_frame

        super().__init__(self.master_frame, width=1300-213, height = 700)

        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        self.create_style(parent)

        # Runs the initilize_GUI function, which actually creates the frame
        # params are the same as defined above
        self.initialize_GUI(parent, master_frame)

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')


    def get_local_boards(self, parent):

        self.local_boards_list = []

        for self.dirpath, dirnames, filenames in os.walk("{}/PythonFiles/Images".format(parent.main_path)):
            for f in filenames:
                fp = os.path.join(self.dirpath, f)
                name = fp[59:]
                if "320" in name:
                    sn, view = name.split('_')
                    self.local_boards_list.append([fp, sn, os.path.splitext(view)[0]])

        self.update_board_tree()

    # Creates the GUI itself
    def initialize_GUI(self, parent, master_frame):
        
        # reskinned frame from the shipping GUI
        Scan_Board_Prompt_Frame = ttk.Frame(self, width = 1105, height = 650)
        Scan_Board_Prompt_Frame.grid(column=0, row = 0, sticky='nsew')

        #resizing
        Scan_Board_Prompt_Frame.grid_columnconfigure(0, weight=1)
        Scan_Board_Prompt_Frame.grid_columnconfigure(1, weight=1)
        Scan_Board_Prompt_Frame.grid_rowconfigure(1, weight=2)
        #Scan_Board_Prompt_Frame.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # creates a Frame for the Treeview
        self.boards_scanned_frame = ttk.Frame(Scan_Board_Prompt_Frame, borderwidth=2, relief="sunken")
        self.boards_scanned_frame.grid(column=0, row=1, rowspan = 10, sticky='nsew', padx = 20, pady = 20)

        #creating treeview for boards scanned
        self.board_tree = ttk.Treeview(
            self.boards_scanned_frame,
            selectmode = 'browse',
            )
        self.board_tree["columns"] = ("id", "board_barcode", "board_view")
        self.board_tree.column('#0', width = 0, stretch = 'no')
        self.board_tree.column("id", anchor = 'center', width=50, stretch='no')
        self.board_tree.column("board_barcode", anchor = 'center', width=300, stretch='yes')
        self.board_tree.column("board_view", anchor = 'center', width=200, stretch='yes')

        self.board_tree.heading('id', text = "#", anchor = 'center')
        self.board_tree.heading('board_barcode', text = "Board Barcode", anchor = 'center')
        self.board_tree.heading('board_view', text = "View", anchor = 'center')

        self.board_tree.grid(column = 0, row = 0, sticky='nsew')
        
        # creates a Label Variable, different customization options
        self.lbl_scan = ttk.Label(
            master= Scan_Board_Prompt_Frame,
            text = "List of all locally saved boards",
            font = ('Arial', 20)
        )
        self.lbl_scan.grid(column=0, columnspan = 2, row=0, sticky='we', padx=10, pady=5)

        # Entry for the full id to be displayed. Upon Scan, update and disable?
        #global ent_full
        
        # Creating intial value in entry box
        self.user_text = tk.StringVar(self)

        # Remove button creation
        self.btn_rm = ttk.Button(
            Scan_Board_Prompt_Frame,
            text = "Remove Board",
            command = lambda:  self.btn_rm_action(parent)
            )
        self.btn_rm.grid(column=1, row=1, padx = 10, pady = 5)

        # save to db button creation
        self.btn_save_to_db = ttk.Button(
            Scan_Board_Prompt_Frame,
            text = "Upload Boards",
            command = lambda: self.btn_save_to_db_action(parent)
            )
        self.btn_save_to_db.grid(column = 1, row = 3, padx = 10, pady = 50)
        
        # Creating frame for logout button (DEV)
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 0, row = 5, columnspan=2, sticky= 'nsew')

        # Creating the finish scanning button
        btn_cancel = ttk.Button(
            frm_logout,
            text = "Cancel",
            command = lambda: self.btn_fin_scan_action(parent)
        )
        btn_cancel.grid(column=0, columnspan = 2, row=4, padx=10, pady=50)

        # Creating the help button
        btn_help = ttk.Button(
            Scan_Board_Prompt_Frame,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.grid(column=1, row=2, padx=10, pady=10)

    #################################################

    def update_board_tree(self):
        for item in self.board_tree.get_children():
            self.board_tree.delete(item)
        i = 0
        for board in self.local_boards_list:
            i = i + 1
            self.board_tree.insert("", "end", values = (i, board[1], board[2])) 

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    #################################################

    def btn_save_to_db_action(self, _parent):
        self.data_holder.add_local_boards_to_db(self.local_boards.list)
        logger.info("Adding locally saved images uploaded to database.")

    #################################################

    # Function for the remove button
    def btn_rm_action(self, _parent):
        selection = self.board_tree.selection()
        select = self.board_tree.item(selection, "values")

        rm_action = mb.askyesno(
	    message=(f'Are you sure you want to remove {select}?'),
	    icon='warning',
            title='Remove'
            )
        if rm_action == True:
            self.local_boards_list.remove([self.dirpath + "/" + select[1] + "_" + select[2] + ".png", select[1], select[2]])
            self.update_board_tree()
            os.remove(self.dirpath + "/" + select[1] + "_" + select[2] + ".png")
            logger.info("LocalUploadScene: %s_%s.png deleted." % (select[1], select[2]))

    #################################################
    
    # finish scanning action
    def btn_fin_scan_action(self, _parent):
        self.EXIT_CODE = 1 
        
        if self.use_scanner:
            self.listener.terminate()
            self.scanner.terminate()

        self.data_holder.clear_add_boards_to_db_list()

         # Send user back to login frame
        _parent.set_frame_login_frame() 

        self.EXIT_CODE = 0

    #################################################
