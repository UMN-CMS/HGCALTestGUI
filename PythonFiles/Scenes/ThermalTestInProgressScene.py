#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import tkinter.font as font
import logging
from PythonFiles.utils.ConsoleRedirector import ConsoleRedirector
logging.getLogger('PIL').setLevel(logging.WARNING)
# import PythonFiles
import os
import sys

# Importing Necessary Files
# from PythonFiles.utils.REQClient import REQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestInProgressScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# Creating class for the window
class ThermalTestInProgressScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        
        self.console_text = None
        self.original_stdout = sys.stdout  # Store the default stdout
        
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent
        
        self.update_frame(parent)

        # Restore to default (in constructor)
        # sys.stdout = self.original_stdout

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A ThermalTestInProgressScene frame has been updated.")
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
            text = "Thermal Test in Progress", 
            font = ('Arial', '28')
            )
        lbl_title.pack(side = 'top', pady = 10)
        

        # # Create the rectangle canvas
        # canvas = tk.Canvas(frm_window, width=700, height=200)
        # canvas.pack()
        # canvas.create_rectangle(0, 0, 700, 200, fill="lightgray", outline="black")

        # Create console display inside the window
        self.create_console_window(frm_window)
        print("ThermalTestInProgressScene: Console created.")
        logger.info("ThermalTestInProgressScene: Successfully created console for output on GUI.")
        

        # Example print statements (These will appear in the Tkinter window)
        print("Initializing system...")
        print("Loading data...")
        print("Process completed successfully!")


        # Create a label for bottom text
        lbl_wait_text = ttk.Label(
            frm_window, 
            text = "Please wait, tests in progress...", 
            font = ('Arial', '14')
            )
        lbl_wait_text.pack(side = 'top', pady = 15)


        #------------------------------

        # Create the countdown timer frame
        self.frm_timer = ttk.Frame(frm_window, padding=10)
        self.frm_timer.pack(side='top', pady=20)

        # Create the label for approximate time remaining
        lbl_approx_time = ttk.Label(self.frm_timer, text="Approximate time remaining:", font=("Arial", 15))
        lbl_approx_time.grid(row=0, column=0, padx=5, pady=5, sticky="w")


        # Create a label to display the countdown timer
        self.timer_label = ttk.Label(self.frm_timer, text="02:00:00", font=("Arial", 24), foreground="red")
        self.timer_label.grid(row=1, column=0, columnspan=3, pady=10)

        # Clear and start the countdown from 2 hours (7200 seconds)
        self.cancel_timer()
        self.remaining_time = 7200
        self.update_timer()






        # Create a logout button
        btn_stop_early = ttk.Button(
            frm_window, 
            text = "Stop Test Early", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_stop_early_action(parent))
        btn_stop_early.pack(anchor = 'center', pady = 5)


        # Create a button to go to test results
        self.btn_next = ttk.Button(
            frm_window, 
            text = "Thermal Test Results", 
            state="disabled",
            #relief = tk.RAISED, 
            command = lambda: self.btn_next_action(parent))
        self.btn_next.pack(anchor = 'center', pady = 5)


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
    def create_console_window(self, frm_window):
        # Create a frame to hold the console output and scrollbar
        console_frame = tk.Frame(frm_window)
        
        # Create a Text widget for displaying console output
        self.console_text = tk.Text(console_frame, width=85, height=30, wrap="word", state="disabled", bg="black", fg="white")
        self.console_text.pack(side="left", fill="both", expand=True)

        # Create a Scrollbar and attach it to the Text widget
        scrollbar = tk.Scrollbar(console_frame, command=self.console_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.console_text.config(yscrollcommand=scrollbar.set)

        console_frame.pack()


        # Redirect sys.stdout to the Text widget
        print("ThermalTestInProgressScene: Sending console text to ThermalTestInProgressScene")
        # sys.stdout = ConsoleRedirector(self.console_text)
        print("ThermalTestInProgressScene: Sent console text to ThermalTestInProgressScene")
        
            



    # Timer functionality
    def update_timer(self):
        # Updates the countdown timer every second.
        if self.remaining_time > 0:
            self.remaining_time -= 1
            hours, remainder = divmod(self.remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            if (seconds % 30 == 0):
                print("Time:", hours, ":", minutes, ":", seconds)
            self.timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

            # Schedule the next update
            self._timer_id = self.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="00:00:00", foreground="red")
            self.btn_next.config(state="normal") #Results Button can only be pressed when timer is done

    def set_timer(self, hours, minutes):
        # Manually sets the countdown timer based on function parameters.
        # Convert input to total seconds
        self.remaining_time = (hours * 3600) + (minutes * 60)

        # Update timer display immediately
        self.update_timer()


    def cancel_timer(self):
        # Cancel any scheduled timer updates
        if hasattr(self, "_timer_id"):
            self.after_cancel(self._timer_id)
        
        # Reset the remaining time
        self.remaining_time = 0

        # Update the timer display immediately
        self.timer_label.config(text="00:00:00", foreground="red")

    
    
    def help_action(self, _parent):
        _parent.help_popup(self)
 

    def btn_stop_early_action(self, _parent):
        confirm = messagebox.askyesno(
                title="Confirm Early Stop",
                message="Are you sure you want to stop the test now?\nThermal testing is still in progress!"
            )
        if confirm:
            logger.info("User stopped thermal testing early!")
            self.cancel_timer()
            logger.info("TestScene: Succesfully logged out from the ThermalTestScene")
            _parent.set_frame_thermal_final_results()

        # TODO Complete
        # _parent.btn_stop_early_action(self)
        pass 


    # Send to the next scene (thermal_final_results)
    def btn_next_action(self, _parent):
        response = messagebox.askokcancel(
                title="Confirm Test Finish",
                message="Make sure the green light on top of the Cycler is on before proceeding to results."
            )
        if response:
            self.cancel_timer()
            logger.info("TestScene: Succesfully logged out from the ThermalTestScene")
            # sys.stdout = self.original_stdout
            _parent.set_frame_thermal_final_results()



    def run_all_action(self, _parent):
       
        _parent.run_all_tests() 
        

    #################################################      
        
    def get_submit_action(self):
        return self.btn_confirm_action

    def get_parent(self):
        return self.parent
    
    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        logger.info("TestScene: Successfully logged out from the ThermalTestScene.")
        _parent.set_frame_login_frame()

    #################################################




