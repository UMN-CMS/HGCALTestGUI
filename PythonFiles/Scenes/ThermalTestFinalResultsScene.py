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
import time
import json
from PythonFiles.utils.ConsoleRedirector import ConsoleRedirector
import sys
import requests

from PythonFiles.utils.ThermalREQClient import ThermalREQClient
# Importing Necessary Files
# from PythonFiles.utils.REQClient import REQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestFinalResultsScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Define state options
STATES = {
    "pass": ("✔", "green"),
    "fail": ("✖", "red"),
    "retest": ("⚠", "orange"),
    "excluded": ("__", "black"),
    "waiting": ("...", "lightgray")
}

# Creating class for the window
class ThermalTestFinalResultsScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent

        self.naming_scheme = [
                                "SFP0", "SFP1", "SFP2", "SFP3",
                                "A1", "A2", "A3", "A4",
                                "B1", "B2", "B3", "B4",
                                "C1", "C2", "C3", "C4",
                                "D1", "D2", "D3", "D4"
                            ]
        self.checkbox_states = ['waiting']*20

        self.update_frame(parent)
    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A ThermalTestFinalResultsScene frame has been updated.")
        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 15)
        
        self.create_style(parent)
        # Create a centralized window for information
        frm_window = ttk.Frame(self, width=1000, height = 480)
        frm_window.grid(column=0, row=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        frm_window.columnconfigure(0, weight=1)
        frm_window.rowconfigure(0, weight=1)

        # Create a label for the tester's name
        lbl_title = ttk.Label(
            frm_window, 
            text = "Thermal Test Results", 
            font = ('Arial', '28')
            )
        lbl_title.pack(side = 'top', pady = 10)
        
        container_frame = ttk.Frame(frm_window)
        container_frame.pack(pady=10, padx=450, fill='x')


        # Create a frame to hold the checkboxes
        checkbox_frame = ttk.Frame(container_frame)
        checkbox_frame.pack(side='left', padx=(0, 50))

        # Initialize states
        # TODO Update these to fill dynamically

        # TODO Find where to pull this information from
        self.checkbox_labels = []
        self.checkbox_vars = []

        key_frame = ttk.Frame(container_frame, padding=10, width=400)
        key_frame.pack(side='left', fill='y')
        key_frame.pack_propagate(False)

        # Key descriptions
        key_descriptions = {
            "pass": "Pass",
            "fail": "Fail",
            "retest": "Needs Retesting",
            "excluded": "Excluded from Test",
            "waiting": "Waiting"
        }

        self.naming_scheme = [
                                "SFP0", "SFP1", "SFP2", "SFP3",
                                "A1", "A2", "A3", "A4",
                                "B1", "B2", "B3", "B4",
                                "C1", "C2", "C3", "C4",
                                "D1", "D2", "D3", "D4"
                            ]

        # Loop to create 20 visual checkboxes 
        for i in range(20):
            col = i // 4 
            row = i % 4

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

            text_label = ttk.Label(
                    checkbox_frame,
                    text=f"{self.naming_scheme[i]}",
                    font=("Arial", 14)
                )
            text_label.grid(row=row, column=col * 2 + 1, padx=10, pady=6, sticky="w")


            # TODO Remove/update board status button binds on Final Results Scene
            # Bind click event to toggle state
            # state_label.bind("<Button-1>", lambda e, lbl=state_label, idx=i: self.toggle_state(lbl, idx))

            # Store label reference
            self.checkbox_labels.append(state_label)

        # Add labels to the key
        for i, (state, description) in enumerate(key_descriptions.items()):
            ttk.Label(
                key_frame, 
                text=f"{STATES[state][0]}  {description}",
                foreground=STATES[state][1], 
                font=("Arial", 14),
                wraplength=400
            ).grid(row=i, column=0, padx=5, pady=3, sticky="w")



        # # Create a label for bottom text
        # lbl_begin_text = ttk.Label(
        #     frm_window, 
        #     text = "Place passed engines in blue bin\nFailed engines in red bin\nEngines needing retests in gray bin", 
        #     font = ('Arial', '14')
        #     )
        # lbl_begin_text.pack(side = 'top', pady = (75, 15))

        

        # Create a frame to hold the bottom text labels
        lbl_frame = ttk.Frame(frm_window)
        lbl_frame.pack(side="top", pady=(75, 15))

        # Create labels for each line with colored symbols
        lbl_pass = ttk.Label(
            lbl_frame,
            text=f"{STATES['pass'][0]} ",
            font=("Arial", 14),
            foreground=STATES["pass"][1]
        )
        lbl_pass.pack(side="top", anchor="w", padx=5)

        lbl_pass_text = ttk.Label(
            lbl_frame,
            text="Place passed engines in blue bin",
            font=("Arial", 14),
            foreground="white"
        )
        lbl_pass_text.pack(side="top", anchor="w", padx=25)

        lbl_fail = ttk.Label(
            lbl_frame,
            text=f"{STATES['fail'][0]} ",
            font=("Arial", 14),
            foreground=STATES["fail"][1]
        )
        lbl_fail.pack(side="top", anchor="w", padx=5)

        lbl_fail_text = ttk.Label(
            lbl_frame,
            text="Failed engines in red bin",
            font=("Arial", 14),
            foreground="white"
        )
        lbl_fail_text.pack(side="top", anchor="w", padx=25)

        lbl_retest = ttk.Label(
            lbl_frame,
            text=f"{STATES['retest'][0]} ",
            font=("Arial", 14),
            foreground=STATES["retest"][1]
        )
        lbl_retest.pack(side="top", anchor="w", padx=5)

        lbl_retest_text = ttk.Label(
            lbl_frame,
            text="Engines needing retests in gray bin",
            font=("Arial", 14),
            foreground="white"
        )
        lbl_retest_text.pack(side="top", anchor="w", padx=25)



        # Create a logout button
        btn_finish = ttk.Button(
            frm_window, 
            text = "Finish", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_finish_action(parent))
        btn_finish.pack(anchor = 'center', pady = (25, 10))

        





        # Create frame for logout button
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 2, row = 2, padx = 10, pady = 10, sticky = 'se')
        frm_logout.columnconfigure(0, weight=1)

        # Create a logout button
        btn_logout = ttk.Button(
            frm_logout, 
            text = "Logout", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'center', pady = 5)

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
 

    def btn_finish_action(self, _parent):

        self.gui_cfg = self.data_holder.getGUIcfg()
        confirm = messagebox.askyesno(
                title="Confirm Finish",
                message="Make sure you have analyzed all results, this will kill any active tests!"
            )

        checkbox_states = self.data_holder.data_dict.get("checkbox_states",[])
        ready_channels = []
        for i in range(len(checkbox_states)):
            if checkbox_states[i] != 'excluded':
                ready_channels.append(True)
            else:
                ready_channels.append(False)

        if confirm:

            print("ThermalTestInProgressScene: Sending REQ to ThermalREQClient...")
            sending_REQ = ThermalREQClient(
                self.gui_cfg,
                'killCycle',
                ready_channels,
                self.data_holder.data_dict['current_full_ID'],
                self.data_holder.data_dict['user_ID'],
                self.conn_trigger
                )
            print("ThermalTestinProgressScene: Completed REQ to ThermalREQClient...")
        


        logger.info("TestScene: Successfully Finished Thermal Testing.")
        _parent.set_frame_login_frame()

   
    #################################################

        
    def get_submit_action(self):
        return self.btn_confirm_action

    def get_parent(self):
        return self.parent
    
    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        logger.info("TestScene: Successfully logged out from the TestScene.")
        result = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if result:
            _parent.set_frame_login_frame()

    def btn_stop_early_action(self, _parent):
        self.gui_cfg = self.data_holder.getGUIcfg()
        confirm = messagebox.askyesno(
                title="Confirm Stop",
                message="Make sure a thermal test is actually running!"
            )

        checkbox_states = self.data_holder.data_dict.get("checkbox_states",[])
        ready_channels = []
        for i in range(len(checkbox_states)):
            if checkbox_states[i] != 'excluded':
                ready_channels.append(True)
            else:
                ready_channels.append(False)

        if confirm:
            logger.info("User stopped thermal testing early!")
            self.cancel_timer()

            print("ThermalTestInProgressScene: Sending REQ to ThermalREQClient...")
            sending_REQ = ThermalREQClient(
                self.gui_cfg,
                'killCycle',
                ready_channels,
                self.data_holder.data_dict['current_full_ID'],
                self.data_holder.data_dict['user_ID'],
                self.conn_trigger
                )
            print("ThermalTestinProgressScene: Completed REQ to ThermalREQClient...")





    #################################################


    def send_REQ(self, _parent):
    
        checkbox_states = self.data_holder.data_dict.get("checkbox_states",[])
        ready_channels = []
        for i in range(len(checkbox_states)):
            if checkbox_states[i] != 'excluded':
                ready_channels.append(True)
            else:
                ready_channels.append(False)
        
        print("ThermalTestFinalResultsScene: Sending REQ to ThermalREQClient...")
        sending_REQ = ThermalREQClient(
                self.data_holder.getGUIcfg(),
                'analyzeCycle',
                ready_channels,
                self.data_holder.data_dict['current_full_ID'],
                self.data_holder.data_dict['user_ID'],
                self.conn_trigger
                )
        print("ThermalTestFinalResultsScene: Completed REQ to ThermalREQClient...")
        
        self.begin_update(self.parent.master_window, self.parent.queue, self.parent)

    def begin_update(self, master_window, queue, parent):
        print("\nThermalTestSetupResultsScene: Beginning to update...looking for new information...\n")
         
        received_data = False
        json_received = None
        while not received_data:
            if not queue.empty():
                print("ThermalTestSetupResultsScene: Queue is not empty...")
                signal=queue.get()
                print(f"ThermalTestSetupResultsScene: signal = {signal}")

                if "Results received successfully." in signal:
                    message = "FOO"
                    message = self.conn_trigger.recv()
                    print('\nMessage from conn_trigger: ', message)
                    logger.info("ThermalTestFinalResultsScene: JSON Received.")
                    logger.info(message)
                    
                    if 'completed' not in message:
                        received_data = True
                        json_received = message

            time.sleep(0.01)

        if json_received:
            self.format_json_received_to_json(json_received)
        else:
            print("ThermalTestSetupResultsScene: No json received after allotted time.")
        return False
                                                                                              

    def format_json_received_to_json(self, imported_json_string):
        json_string = imported_json_string.replace("'", '"')
        json_string = json_string.replace('True', 'true')
        json_string = json_string.replace('False', 'false')
        json_dict = json.loads(json_string)


        print(f"\n\njson_dict: {json_dict}\n\n\n")

        self.apply_results(json_dict)

        self.update_frame(self.parent)  

    def apply_results(self, json_dict):
        for i, name in enumerate(self.naming_scheme):
            if name in json_dict:
                state = json_dict[name].get('passing_state')
                self.checkbox_states[i] = state
            else:
                self.checkbox_states[i] = 'excluded'
            
