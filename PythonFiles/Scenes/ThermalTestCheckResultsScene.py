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

# Importing Necessary Files
# from PythonFiles.utils.REQClient import REQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestCheckResultsScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Define state options
STATES = {
    "ready": ("✔", "green"),
    "failure": ("✖", "red"),
    "warning": ("⚠", "orange"),
    "excluded": ("__", "black"),
    "waiting": ("...", "lightgray")
}

# Creating class for the window
class ThermalTestCheckResultsScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent
        
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
            text = "Setup Check Results", 
            font = ('Arial', '28')
            )
        lbl_title.pack(side = 'top', pady = 10)
        

        # Create a canvas for the rectangle
        canvas = tk.Canvas(frm_window, width=700, height=200)
        canvas.pack()

        # Draw the rectangle
        canvas.create_rectangle(0, 0, 700, 200, fill="lightgray", outline="black")


        # Create a frame to hold the checkboxes
        checkbox_frame = ttk.Frame(frm_window)
        checkbox_frame.pack(pady=10)

        # Initialize states
        # TODO Update these to fill dynamically
        self.checkbox_states = [
            "ready", "failure", "warning", "excluded", "waiting",
            "failure", "ready", "waiting", "excluded", "warning",
            "waiting", "ready", "excluded", "failure", "warning",
            "ready", "waiting", "failure", "excluded", "warning"
        ]

        # TODO Find where to pull this information from
        self.checkbox_labels = []
        self.checkbox_vars = []


        # Loop to create 20 visual checkboxes (2 columns, 10 rows)
        for i in range(20):
            col = i // 10  # Determine column (0 or 1)
            row = i % 10   # Determine row (0-9)

            # Get the initial state from checkbox_states
            initial_state = self.checkbox_states[i]
            initial_text = STATES[initial_state][0]
            initial_color = STATES[initial_state][1]

            # Create a label as a clickable checkbox (icon)
            state_label = ttk.Label(
                checkbox_frame, 
                text=initial_text, 
                foreground=initial_color, 
                font=("Arial", 18),
                padding=2
            )
            state_label.grid(row=row, column=col * 2, padx=5, pady=2, sticky="w")

            # Create a text label next to the state label (Item 1, Item 2, etc.)
            text_label = ttk.Label(
                checkbox_frame,
                text=f"Item {i + 1}",
                font=("Arial", 14)
            )
            text_label.grid(row=row, column=col * 2 + 1, padx=(2, 205), pady=2, sticky="w")

            # Bind click event to toggle state
            state_label.bind("<Button-1>", lambda e, lbl=state_label, idx=i: self.toggle_state(lbl, idx))

            # Store label reference
            self.checkbox_labels.append(state_label)


        # Create a label for bottom text
        lbl_begin_text = ttk.Label(
            frm_window, 
            text = "Make any adjustments and rerun check on selected sites:", 
            font = ('Arial', '14')
            )
        lbl_begin_text.pack(side = 'top', pady = 15)

        # Create 20 checkboxes in a single row
        checkbox_row_frame = ttk.Frame(frm_window)
        
        for i in range(20):
            var = tk.BooleanVar()
            self.checkbox_vars.append(var)

            checkbox = ttk.Checkbutton(
                checkbox_row_frame,
                text=f"{i + 1}",
                variable=var
            )
            checkbox.grid(row=0, column=i, padx=5, pady=5, sticky="w")  # Single row layout
        checkbox_row_frame.pack(pady=10)



        # Create a logout button
        btn_recheck = ttk.Button(
            frm_window, 
            text = "Recheck Selected Sites", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_recheck_selected_action(parent))
        btn_recheck.pack(anchor = 'center', pady = 5)


        # Create a label for bottom text
        lbl_proceed_text = ttk.Label(
            frm_window, 
            text = "If everything is ready, proceed to the full test", 
            font = ('Arial', '14')
            )
        lbl_proceed_text.pack(side = 'top', pady = 15)


        # Create a logout button
        btn_proceed = ttk.Button(
            frm_window, 
            text = "Proceed", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_proceed_action(parent))
        btn_proceed.pack(anchor = 'center', pady = 5)






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

    # Function to toggle states on click
    def toggle_state(self, label, index):
        current_state = self.checkbox_states[index]
        state_keys = list(STATES.keys())
        new_state = state_keys[(state_keys.index(current_state) + 1) % len(STATES)]
        
        # Update state and label
        self.checkbox_states[index] = new_state
        label.config(text=STATES[new_state][0], foreground=STATES[new_state][1])

    
    
    def help_action(self, _parent):
        _parent.help_popup(self)
 

    def btn_proceed_action(self, _parent):
        
        #TODO Complete
        # _parent.btn_proceed_action(self)
        pass 


    def btn_recheck_selected_action(self, _parent):
        
        #TODO Complete
        # _parent.btn_recheck_selected_action(self)
        pass
        
    
    def btn_setup_check_action(self, _parent):
        
        #TODO Complete
        # _parent.thermal_setup_check(self)
        pass

    def btn_select_all_action(self, _parent):
        
        #TODO Complete
        # _parent.select_all_bays(self)
        pass

    def btn_deselect_all_action(self, _parent):
        
        #TODO Complete
        # _parent.deselect_all_bays(self)
        pass

    def btn_confirm_engine_action(self, _parent):
        
        #TODO Complete
        # _parent.confirm_engine_type(self)
        pass


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




