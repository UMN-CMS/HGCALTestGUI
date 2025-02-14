#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import tkinter.font as font
import logging
logging.getLogger('PIL').setLevel(logging.WARNING)
import PythonFiles
import os

# Importing Necessary Files
from PythonFiles.utils.REQClient import REQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestConfigScence')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Creating class for the window
class ThermalTestConfigScence(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, test_name, test_description_short, test_description_long, queue, conn_trigger, test_idx):
        super().__init__(master_frame, width=1300-213, height = 800)
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.test_name = test_name
        self.test_description_short = test_description_short
        self.test_description_long = test_description_long
        self.data_holder = data_holder
        self.test_idx = test_idx
        self.parent = parent
        
        self.update_frame(parent)

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A test frame has been updated.")
        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 15)
        
        self.create_style(parent)
        # Create a centralized window for information
        frm_window = ttk.Frame(self, width=870, height = 480)
        frm_window.grid(column=0, row=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        frm_window.columnconfigure(0, weight=1)
        frm_window.rowconfigure(0, weight=1)

        # Create a label for the tester's name
        lbl_title = ttk.Label(
            frm_window, 
            text = "Test Configuration", 
            font = ('Arial', '28')
            )
        lbl_title.pack(side = 'top', pady = 10)
        
        # # Create an entry for the tester's name
        # ent_tester = tk.Entry(
        #     frm_window, 
        #     )
        # ent_tester.insert(0, self.data_holder.data_dict['user_ID'])
        # ent_tester.pack(side = 'top', pady = 10)
        # ent_tester.config(state = "disabled")

        # Create a label for the full id box
        lbl_full = ttk.Label(
            frm_window, 
            text = "Engine Type: ", 
            font = ('Arial', '20')
            )
        lbl_full.pack(side = 'top', pady = 10)

        engine_types = ["LD_Engines", "HD_Half_Engines", "HD_Full_Engines"]
        self.engine_type_selected = tk.StringVar(self)
        self.engine_type_selected.set("")

        # Creating the dropdown menu itself
        self.engine_dropdown = tk.OptionMenu(
            self, 
            self.user_selected, # Tells option menu to use the created initial value
            *engine_types # Tells the dropdown menu to use every index in the User_List list
            ) 
        self.opt_user_dropdown.pack(pady=15)
        self.opt_user_dropdown.config(width = 20)


        # Create a entry for the full id box
        ent_full = tk.Entry(
            frm_window, 
            #font = font_scene
            )
        ent_full.insert(0, self.data_holder.data_dict['current_full_ID'])
        ent_full.pack(side = 'top', pady = 10)
        ent_full.config(state = "disabled")

        # Create a label for the test about to be run
        lbl_test = ttk.Label(
            frm_window, 
            text = "Current Test: ", 
            font = ('Arial', '24')
            )
        lbl_test.pack(side = 'top', pady = 10)

        # Create a entry for the test type
        self.ent_test = tk.Entry(
            frm_window, 
            )
        self.ent_test.pack(side = 'top', pady = 10)
        self.ent_test.insert(0, self.test_name)
        self.ent_test.config(state = "disabled")

        # Create a label for confirming test
        lbl_confirm = ttk.Label(
            frm_window, 
            text = "Are you ready to begin the test?", 
            font = ('Arial', '24')
            )
        lbl_confirm.pack(side = 'top', pady = 15)

        self.lbl_desc_short = ttk.Label(
            frm_window,
            text = self.test_description_short,
            wraplength = 500,
            justify="center",
            font = ('Arial', '24')
            )

        self.lbl_desc_short.pack(side = 'top', pady = 15)

        self.lbl_desc = ttk.Label(
            frm_window,
            text = self.test_description_long,
            wraplength = 800,
            justify="center",
            font = ('Arial', '24')
            )
        self.lbl_desc.pack(side = 'top', pady = 15)

        # Create frame for logout button
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 2, row = 1, padx = 5, sticky = 'ew')
        frm_logout.columnconfigure(0, weight=1)

        # Create a logout button
        btn_logout = ttk.Button(
            frm_logout, 
            text = "Logout", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'center', pady = 5)

        # Create a button for confirming test
        btn_confirm = ttk.Button(
            frm_logout,
            text = "Confirm",
            #relief = tk.RAISED, 
            command = lambda:self.btn_confirm_action(parent)
            )
        btn_confirm.pack(anchor = 'center', pady = 5)

        #if (self.test_idx == 0):

        # Create a button for confirming test
        run_all_btn = ttk.Button(
            frm_logout, 
            text = "Run All Tests",
            command = lambda:self.run_all_action(parent),
            )
        run_all_btn.pack(anchor = 'center', pady = 5)


        # Create a rescan button
        btn_rescan = ttk.Button(
            frm_logout, 
            text = "Change Boards", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_rescan_action(parent))
        btn_rescan.pack(anchor = 'center', pady = 5)

        # Creating the help button
        btn_help = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.pack(anchor = 'center', pady = 5)
        

        self.grid_propagate(0)


    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)
 

    def run_all_action(self, _parent):
       
        _parent.run_all_tests() 
        

    #################################################

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.reset_board()
    
    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        self.gui_cfg = self.data_holder.getGUIcfg()
      
        #try:
        test_client = REQClient(self.gui_cfg, 'test{}'.format(self.test_idx), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'], self.conn_trigger)
        #except Exception as e:
        #    messagebox.showerror('Exception', e)

        _parent.set_frame_test_in_progress(self.queue)
        
    def get_submit_action(self):
        return self.btn_confirm_action

    def get_parent(self):
        return self.parent
    
    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        logger.info("TestScene: Successfully logged out from the TestScene.")
        _parent.set_frame_login_frame()

    #################################################




