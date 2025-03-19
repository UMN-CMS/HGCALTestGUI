#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import tkinter.font as font
import logging
logging.getLogger('PIL').setLevel(logging.WARNING)
# import PythonFiles
import os

# Importing Necessary Server Files
from PythonFiles.utils.ThermalREQClient import ThermalREQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestConfigScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Creating class for the window
class ThermalTestConfigScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent

        # Create a list of boolean values for the checkboxes
        # TODO Verify this is correctly set up
        self.checkbox_values = [
                                False, False, False, False, False, 
                                False, False, False, False, False, 
                                False, False, False, False, False,
                                False, False, False, False, False
                                ]
        self.bool_checkbox_values = [
                                False, False, False, False, False, 
                                False, False, False, False, False, 
                                False, False, False, False, False,
                                False, False, False, False, False
                                ]
        
        self.current_engine_selection = None
        
        self.update_frame(parent)

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A ThermalTestConfigScene frame has been updated.")
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
        


        # Create a frame to contain the label, dropdown, and confirm button in a single row
        frm_engine_selection = ttk.Frame(frm_window)
        frm_engine_selection.pack(anchor='center', pady=10)

        # Create a label for the engine type
        lbl_full = ttk.Label(
            frm_engine_selection, 
            text="Engine Type: ", 
            font=('Arial', '20')
        )
        lbl_full.pack(side='left', padx=5)

        # Dynamically update dropdown menu
        engine_types = ["LD_Engines", "HD_Half_Engines", "HD_Full_Engines"]
        self.engine_type_selected = tk.StringVar(self)
        self.engine_type_selected.set("")

        # Creating the dropdown menu itself
        self.engine_dropdown = tk.OptionMenu(
            frm_engine_selection, 
            self.engine_type_selected,  
            *engine_types  
        ) 
        self.engine_dropdown.pack(side='left', padx=5)
        self.engine_dropdown.config(width=20)

        # Traces when the user selects an option in the dropdown menu
        self.engine_type_selected.trace_add(
            'write', 
            lambda *args: self.dropdown_engine_selected()
            )



        # Create a label for confirming test
        lbl_active = ttk.Label(
            frm_window, 
            text = "Select active sites:", 
            font = ('Arial', '24')
            )
        lbl_active.pack(side = 'top', pady = 15)




        # Create a frame to hold the checkboxes
        checkbox_frame = ttk.Frame(frm_window)
        checkbox_frame.pack(pady=10)

        # Loop to create 20 checkboxes (2 columns and 10 rows)
        for i in range(20):
            col = i // 10  # Determine which column (0 or 1)
            row = i % 10   # Determine the row (0-9)

            # Create the checkbox and label for each
            chk_var = tk.BooleanVar()
            chk_var.set(self.checkbox_values[i])

            checkbox = ttk.Checkbutton(
                checkbox_frame,
                text=f"{i + 1}",  # Display the number next to the checkbox (1-indexed)
                variable=chk_var,
                command=lambda idx=i: self.checkbox_selected(idx)  # Pass index to function
            )
            checkbox.grid(row=row, column=col, padx=10, pady=5, sticky="w")

            # Store the checkbox variable if you need to access the values later
            self.checkbox_values[i] = chk_var


        # Create a frame for the select/deselect buttons
        frm_select = ttk.Frame(frm_window)
        # Create "Select All" button
        btn_select_all = ttk.Button(
            frm_select,
            text="Select All",
            command=lambda: self.btn_select_all_action(parent)
        )
        btn_select_all.pack(side='left', padx=10)

        # Create "Deselect All" button
        btn_deselect_all = ttk.Button(
            frm_select,
            text="Deselect All",
            command=lambda: self.btn_deselect_all_action(parent)
        )
        btn_deselect_all.pack(side='left', padx=5)

        frm_select.pack(anchor='center', pady=10)



        # Create a label for bottom text
        lbl_begin_text = ttk.Label(
            frm_window, 
            text = "Once all engines are properly connected, click the button below to begin the setup check:", 
            font = ('Arial', '20')
            )
        lbl_begin_text.pack(side = 'top', pady = 25)


        # Create a logout button
        btn_setup_check = ttk.Button(
            frm_window, 
            text = "Run Setup Check", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_setup_check_action(parent))
        btn_setup_check.pack(anchor = 'center', pady = 5)






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

        # # Create a button for confirming test
        # run_all_btn = ttk.Button(
        #     frm_logout, 
        #     text = "Run All Tests",
        #     command = lambda:self.run_all_action(parent),
        #     )
        # run_all_btn.pack(anchor = 'center', pady = 5)


        # # Create a rescan button
        # btn_rescan = ttk.Button(
        #     frm_logout, 
        #     text = "Change Boards", 
        #     #relief = tk.RAISED, 
        #     command = lambda: self.btn_rescan_action(parent))
        # btn_rescan.pack(anchor = 'center', pady = 5)

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
 
    def checkbox_selected(self, idx):
        self.gui_cfg = self.data_holder.getGUIcfg()
        
        self.bool_checkbox_values = []

        for chk_var in self.checkbox_values:
            value = chk_var.get() 
            # print(f"Value: {value} (Type: {type(value)})")  # Debugging output
            self.bool_checkbox_values.append(value)  # Ensure proper boolean conversion

        # print("simple_checkbox_values:", simple_checkbox_values)





    def btn_setup_check_action(self, _parent):
        
        print("Sending REQ to ThermalREQClient...")
        
        sending_REQ = ThermalREQClient(
            self.gui_cfg, 
            'submit_slots', 
            self.bool_checkbox_values, 
            self.data_holder.data_dict['current_full_ID'], 
            self.data_holder.data_dict['user_ID'], 
            self.conn_trigger
            )
        
        _parent.set_frame_thermal_setup_results()
        # TODO Complete data logging from current scene

        pass

    def dropdown_engine_selected(self):
        self.current_engine_selection = self.engine_type_selected.get()
        print("ThermalTestConfigScene: engine_selected =", self.current_engine_selection)
        logger.info("ThermalTestConfigScene: selected the {} engine from the dropdown".format(self.current_engine_selection))

    def btn_select_all_action(self, _parent):
        
        self.select_all_checkbox()
        self.checkbox_selected(0)

        pass

    def btn_deselect_all_action(self, _parent):

        self.deselect_all_checkbox()
        self.checkbox_selected(0)       
        
        pass

    # def btn_confirm_engine_action(self, _parent):
        
    #     print()

    #     pass


    def run_all_action(self, _parent):
       
        _parent.run_all_tests() 
        
    # Since BooleanVar is linked to the checkboxes, updating it will instantly reflect on the GUI.
    def select_all_checkbox(self):
        # Set all checkbox values to True
        for i in range(len(self.checkbox_values)):
            self.checkbox_values[i].set(True)  # Update BooleanVar

    # Since BooleanVar is linked to the checkboxes, updating it will instantly reflect on the GUI.
    def deselect_all_checkbox(self):
        for i in range(len(self.checkbox_values)):
            self.checkbox_values[i].set(False)  # Update BooleanVar



    #################################################

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.reset_board()
    
    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        self.gui_cfg = self.data_holder.getGUIcfg()
      
        sending_REQ = ThermalREQClient(
            self.gui_cfg, 
            'submit_slots', 
            self.bool_checkbox_values, 
            self.data_holder.data_dict['current_full_ID'], 
            self.data_holder.data_dict['user_ID'], 
            self.conn_trigger
            )

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




