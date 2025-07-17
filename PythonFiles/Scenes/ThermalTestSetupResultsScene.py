#################################################################################

# Importing Necessary Modules
import tkinter as tk
import time
import tkinter.ttk as ttk
from tkinter import messagebox
import tkinter.font as font
import logging
logging.getLogger('PIL').setLevel(logging.WARNING)
# import PythonFiles
import os
import sys
import json
from PythonFiles.utils.ConsoleRedirector import ConsoleRedirector

import requests

# Importing Necessary Server Files
from PythonFiles.utils.ThermalREQClient import ThermalREQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestSetupResultsScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Define state options
STATES = {
    "ready": ("✔", "green"),
    "failure": ("✖", "red"),
    "warning": ("⚠", "orange"),
    "excluded": ("__", "black"),
    "waiting": ("...", "lightgray"),
    "failed3": ("✖⚠", "maroon"),
    "passed": ("✔⚠", "steelblue")
}

# Creating class for the window
class ThermalTestSetupResultsScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        
        self.naming_scheme = [
                        "SFP0", "SFP1", "SFP2", "SFP3",
                        "A1", "A2", "A3", "A4",
                        "B1", "B2", "B3", "B4",
                        "C1", "C2", "C3", "C4",
                        "D1", "D2", "D3", "D4"
                    ]
        
        # Initialize the states
        self.checkbox_states = ["waiting"]*20

        self.console_text = None
        self.original_stdout = sys.stdout  # Store the default stdout
        
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent
        self.is_initial_check = True
        self.update_frame(parent)
        # sys.stdout = self.original_stdout
        
        

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    
    def update_frame(self, parent):
        logger.debug("ParentTestClass: A ThermalTestSetupResultsScene frame has been updated.")
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



        # # Create a canvas for the rectangle
        # canvas = tk.Canvas(frm_window, width=700, height=200)
        # canvas.pack()

        # # Draw the rectangle
        # canvas.create_rectangle(0, 0, 700, 200, fill="lightgray", outline="black")


        # Create a frame to hold the checkboxes
        checkbox_frame = ttk.Frame(frm_window)
        checkbox_frame.pack(pady=10)
        

        self.adjustment_var = [
            False, False, False, False, False, 
            False, False, False, False, False, 
            False, False, False, False, False, 
            False, False, False, False, False
        ]

        # Key descriptions
        key_descriptions = {
            "ready": "Ready",
            "failure": "Connection Failure",
            "warning": "Not Ready for Thermal Testing",
            "excluded": "Excluded from Test",
            "waiting": "Waiting",
            "failed3": "Failed Thermal Testing 3 Times",
            "passed": "Already Passed Thermal Testing"
        }


        key_frame = ttk.Frame(checkbox_frame, padding=10)
        key_frame.grid(row=0, column=4, rowspan=10, padx=(100, 20), sticky="nw")

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

            # If statement is necessary for formatting
            # (note the pady)
            if (col == 1):
                # Create a text label next to the state label (Item 1, Item 2, etc.)
                text_label = ttk.Label(
                    checkbox_frame,
                    text=f"{self.naming_scheme[i]}",
                    font=("Arial", 14)
                )
                text_label.grid(row=row, column=col * 2 + 1, padx=(2, 0), pady=2, sticky="w")
            else:
                # Create a text label next to the state label (Item 1, Item 2, etc.)
                text_label = ttk.Label(
                    checkbox_frame,
                    text=f"{self.naming_scheme[i]}",
                    font=("Arial", 14)
                )
                text_label.grid(row=row, column=col * 2 + 1, padx=(2, 205), pady=2, sticky="w")

            # Bind click event to toggle state
            state_label.bind("<Button-1>", lambda e, lbl=state_label, idx=i: self.toggle_state(lbl, idx))

            # Store label reference
            self.checkbox_labels.append(state_label)

        # Add labels to the key
    

        for i, (state, description) in enumerate(key_descriptions.items()):
            ttk.Label(
                 key_frame,
                 text=f"{STATES[state][0]} {description}",
                 foreground=STATES[state][1],
                 font=("Arial", 14)
             ).grid(row=i, column=0, padx=5, pady=3, sticky="w")



        # Create a label for bottom text
        lbl_begin_text = ttk.Label(
            frm_window, 
            text = "Make any adjustments using the channel selectors below. You may: Add new boards, or replace/remove/recheck existing boards", 
            font = ('Arial', '14')
            )
        lbl_begin_text.pack(side = 'top', pady = (15,5))



        # Create 20 checkboxes in a single row
        adjustment_row_frame = ttk.Frame(frm_window)
        
        for i in range(20):
            adj_var = tk.BooleanVar()
            adj_var.set(self.adjustment_var[i])
            self.adjustment_var[i] = adj_var

            adj_checkbox = ttk.Checkbutton(
                adjustment_row_frame,
                text=f"{self.naming_scheme[i]}",
                variable=adj_var,
                command= lambda idx=i: self.adj_checkbox_action(idx)
            )
            adj_checkbox.grid(row=0, column=i, padx=5, pady=5, sticky="w")  # Single row layout
        adjustment_row_frame.pack(pady=10)



        # Create a logout button
        btn_recheck = ttk.Button(
            frm_window, 
            text = "Recheck Selected Sites", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_recheck_selected_action(parent))
        btn_recheck.pack(anchor = 'center', pady = 5)
        
        btn_remove = ttk.Button(
                frm_window,
                text="Remove Selected Sites",
                command = lambda: self.btn_remove_selected_action(parent))
        btn_remove.pack(anchor = 'center', pady = 5)

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
        frm_logout.grid(column = 2, row = 2, padx = 10, pady=10, sticky = 'se')
        frm_logout.columnconfigure(0, weight=1)

        # Create a logout button
        btn_logout = ttk.Button(
            frm_logout, 
            text = "Logout", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'center', pady = 5)

    

        #if (self.test_idx == 0):


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

        self.get_setup_check_results()

    # For completely resetting the checkbox states from a list 
    def set_checkbox_states(self, checkbox_list):
        for index, state in checkbox_list:
            self.checkbox_states[index] = "{}".format(state)
            
            # Formatting the frontend label
            label = self.checkbox_labels[index]
            label.config(text=STATES[state][0], foreground=STATES[state][1])

        print("ThermalTestSetupResultsScene: completed set_checkbox_states:", self.checkbox_states)


    def get_setup_check_results(self):
        # print("checkbox_states", self.checkbox_states)    #for debugging
        # TODO return to the dataholder for storage
        return self.checkbox_states    
    
    def adj_checkbox_action(self, idx):
        self.get_adj_checkbox_action(idx)

    def get_adj_checkbox_action(self, idx):
        # print("adj_:", self.adjustment_var)
        simple_adj = []

        for adj_val in self.adjustment_var:
            val = adj_val.get()
            simple_adj.append(val)

        # print("simple_adj:", simple_adj)

        # TODO Return to the dataholder
        return simple_adj
 
    
    
    def help_action(self, _parent):
        _parent.help_popup(self)
 

    def btn_proceed_action(self, _parent):
        # sys.stdout = self.original_stdout
        self.is_initial_check = True
        self.checkbox_states = ['waiting']*20

        _parent.set_frame_thermal_begin()
        pass 


    def btn_recheck_selected_action(self, _parent):
        
        self.is_initial_check = False
        gui_cfg = self.data_holder.getGUIcfg()
    
        bool_checkbox_values = []
        for chk_var in self.adjustment_var:
            value = chk_var.get() 
            # print(f"Value: {value} (Type: {type(value)})")  # Debugging output
            bool_checkbox_values.append(value)  # Ensure proper boolean conversion
        
        sending_REQ = ThermalREQClient(
            gui_cfg, 
            'fullIDs', 
            bool_checkbox_values, 
            self.data_holder.data_dict['current_full_ID'], 
            self.data_holder.data_dict['user_ID'], 
            self.conn_trigger
            )

        self.begin_update(self.parent.master_window, self.parent.queue, self.parent)
        # TODO Complete
        # _parent.btn_recheck_selected_action(self)
        pass
        
    def btn_remove_selected_action(self, _parent):
        

        for i in range(20):
            if self.adjustment_var[i].get():
                state = 'excluded'
                print(f"Updating {self.naming_scheme[i]} to state '{state}'")

                self.checkbox_states[i] = state
                self.checkbox_labels[i].config(
                        text=STATES[state][0],
                        foreground=STATES[state][1]
                        )
        #This data_dict will be called in the next scene to tell the server which channels to thermal test        
        self.data_holder.data_dict["checkbox_states"] = self.checkbox_states

        self.update_frame(self.parent)
                



    def btn_setup_check_action(self, _parent):
        
        # TODO Complete
        # _parent.thermal_setup_check(self)
        pass


    def btn_confirm_engine_action(self, _parent):
        
        # TODO Complete
        # _parent.confirm_engine_type(self)
        pass

    
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
            self.is_initial_check = True
            self.checkbox_states = ['waiting']*20
            _parent.set_frame_login_frame()

    #################################################

    #This is the initial result display update being fed from the ThermalConfig scene
    def apply_initial_check_results(self, state_list):
           
        for i in range(min(len(state_list), len(self.checkbox_states))):
            if state_list[i][1] > 2:
                state = 'failed3'
            else:
                state = state_list[i][0]

            self.checkbox_states[i] = state    
            self.checkbox_labels[i].config(
                        text=STATES[state][0],
                        foreground=STATES[state][1]
                        )


        #This data_dict will be called in the next scene to tell the server which channels to thermal test
        self.data_holder.data_dict["checkbox_states"] = self.checkbox_states

    

    #This will be called for each recheck in the ThermalSetupResults scene. It only updates the channels selected for rechecking
    def apply_recheck_results(self, state_list):
        selected_indices = [i for i, var in enumerate(self.adjustment_var) if var.get()]

        for i in range(min(len(state_list), len(self.checkbox_states))):
            if self.adjustment_var[i].get():
                if state_list[i][1] > 2:
                    state = 'failed3'
                else:    
                    state = state_list[i][0]
                print(f'Updating channel {self.naming_scheme[i]} to state: {state}')
                self.checkbox_states[i] = state
                self.checkbox_labels[i].config(
                        text=STATES[state][0],
                        foreground=STATES[state][1]
                        )
        #This data_dict will be called in the next scene to tell the server which channels to thermal test        
        self.data_holder.data_dict["checkbox_states"] = self.checkbox_states

    
    def begin_update(self, master_window, queue, parent):
        print("\nThermalTestSetupResultsScene: Beginning to update...looking for new information...\n")

        #Create loading popup
        self.loading_popup = tk.Toplevel(self)
        self.loading_popup.title("Loading...")
        self.loading_popup.geometry("500x300")
        self.loading_popup.transient(self)
        self.loading_popup.grab_set()
        self.loading_popup.configure(bg='#2e2e2e')

        label = ttk.Label(self.loading_popup, text="Checking\nselected\nchannels...", font=('Arial', 40),foreground='white',background='#2e2e2e')
        label.pack(pady=30)

        self.after(100, lambda: self.wait_for_server_response(master_window, queue, parent))


    def wait_for_server_response(self, master_window, queue, parent):

        received_data = False
        json_received = None
        while not received_data:
            if not queue.empty():
                print("ThermalTestSetupResultsScene: Queue is not empty...")
                signal=queue.get()
                print(f"ThermalTestSetupResultsScene: signal = {signal}")
                
                if "Results received successfully." in signal:
                    message = "FOO"
                    message =  self.conn_trigger.recv()
                    print("\nMessage from conn_trigger:", message)
                    # self.data_holder.update_from_json_string(message) 
                    
                    logger.info("ThermalTestSetupResultsScene: JSON Received.")
                    logger.info(message)
                    json_received = message
                    received_data = True
                # else:
                #     topic, message = signal.split(" ; ")
                #     print("signal:", signal, "\ntopic:", topic, "message", message)
                #     if (topic == "print"):
                #         print(message) 
                #     if (topic == "Done."):
                #         received_data = True

                else:
                    self.after(50, lambda: self.wait_for_server_response(master_window, queue, parent))
                    return

        if hasattr(self, 'loading_popup') and self.loading_popup.winfo_exists():
            self.loading_popup.destroy()

    
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

        if self.is_initial_check == True:
            self.apply_initial_check_results(json_dict)
        else:
            self.apply_recheck_results(json_dict)

        self.update_frame(self.parent)        



        # logger.info("ThermalTestSetupResultsScene: Started console update loop.")
        
        # # How long before the queue is being checked (if empty)
        # # units of seconds
        # refresh_break = 0.01

        # # Time spent in the waiting phase; in units of refresh_break
        # # Time waiting (sec) = counter * refresh_break
        # counter = 0

        # self.window_closed = False

        # # Maximum timeout in seconds
        # Timeout_after = 10
        # MAX_TIMEOUT = Timeout_after / 2.5
        # # try:
        # print("\n\nThermalTestSetupResultsScene: Beginning the while loop\n\n") 
        # logger.info("ThermalTestSetupResultsScene: While-loop - Beginning try catch for receiving data through the pipeline.")
        
        # information_received = False
        # json_received = False

        # try:
        #     while not json_received:
        #         message = queue.get_nowait()
        #         if (counter == 1000 or len(message) > 1):
        #             print("Looping....")
        #             print("Message:", message)
        #             counter = 0
        #         else:
        #             counter = counter + 1
        # except queue.Empty:
        #     pass  # No new messages
                
#                 master_window.update()
#                 if not queue.empty():    
#                     information_received = True
#                     text = queue.get()
#                     print(text)
#                     logger.info(text)
                    

#                     if "Done." in text:
#                         print("\nTest is complete; received 'Done.'\n")
#                         logger.info("ThermalTestSetupResultsScene: Stopping Progress Bar.")

#                     if "Exit." in text:
#                         time.sleep(1)
#                         parent.test_error_popup("Unable to run test")
#                         logger.info("ThermalTestSetupResultsScene: Unable to run test.")
#                         break

#                     if "Results received successfully." in text:
                    
#                         # message =  self.conn.recv()
#                         message = "FOO"
#                         self.data_holder.update_from_json_string(message) 
                        
#                         logger.info("ThermalTestSetupResultsScene: JSON Received.")
#                         logger.info(message)
#                         json_received = True
# #                        FinishedTestPopup(parent, self.data_holder, queue)
# #
# #                    if "Closing Test Window." in text:
#                         logger.info("ThermalTestSetupResultsScene: ending loop")
#                         try:
#                             master_window.update()
#                         except Exception as e:
#                             print("\ThermalTestSetupResultsScene: Unable to update master_window\n")
#                             print("Exception: ", e)
#                             logger.info(e)

#                         time.sleep(0.02)
#                         break
                    

        # except ValueError as e:
            
        #     print("\n\nException:  ", e)

        #     # Throw a message box that shows the error message
        #     # Logs the message
        #     time_sec = counter*refresh_break
        #     logger.info('ThermalTestSetupResultsScene: Timeout Error', "Exception received -> Process timed out after 10 seconds")

        #     messagebox.showwarning('Timeout Error', "ThermalTestSetupResultsScene: Process timed out after 10 seconds")
        #     logger.info("ThermalTestSetupResultsScene: Trying to go back to the login frame.")
        #     # parent.set_frame_login_frame()
        #     return False
        
        # #except Exception as e:
            
        # #    print("\n\nException:  ", e, "\n\n")

        # return True    

#########################################################


