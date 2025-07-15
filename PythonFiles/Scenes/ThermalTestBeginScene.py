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
# Importing Necessary Files
from PythonFiles.utils.ThermalREQClient import ThermalREQClient

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.ThermalTestBeginScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Creating class for the window
class ThermalTestBeginScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, queue, conn_trigger):
        super().__init__(master_frame, width=1300-213, height = 800)
        self.queue = queue
        self.conn_trigger = conn_trigger
        self.data_holder = data_holder
        self.parent = parent
        
        self.update_frame(parent)
        self.naming_scheme = [
                        "SFP0", "SFP1", "SFP2", "SFP3",
                        "A1", "A2", "A3", "A4",
                        "B1", "B2", "B3", "B4",
                        "C1", "C2", "C3", "C4",
                        "D1", "D2", "D3", "D4"
                    ]

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A ThermalTestBeginScene frame has been updated.")
        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 15)
        print(list(self.data_holder.data_dict.keys())) 
        print("\n"*5)
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
            text = "Begin Thermal Test", 
            font = ('Arial', '28')
            )
        lbl_title.pack(side = 'top', pady = (10, 50))
       
      
        lbl_section1 = ttk.Label(
            frm_window, 
            text = f"1. Seal the chamber door \n 2. Start the ENGIN CYCL profile on the thermal cycler", 
            font = ('Arial', '24'),
            anchor="w",
            justify="left"
            )
        lbl_section1.pack(side = 'top', pady = (15, 175))
        
        lbl_section2_title = ttk.Label(
            frm_window, 
            text = "Then, verify the following:", 
            font = ('Arial', '24'),
            anchor="w",
            justify="center"
            )
        lbl_section2_title.pack(side = 'top', pady = (15, 10))
        
        lbl_section2 = ttk.Label(
            frm_window, 
            text = '1."ENGIN CYCL Running" is displayed on the thermal chamber screen \n 2. The rotameter indicator is at the top of the gauge',font = ('Arial', '24'),
            anchor="w",
            justify="left"
            )
        lbl_section2.pack(side = 'top', pady = (15, 200))

       
        lbl_section3 = ttk.Label(
            frm_window, 
            text = "If everything is ready, click below to start the full test", 
            font = ('Arial', '24')
            )
        lbl_section3.pack(side = 'top', pady = 15)




        

        

        # Create a logout button
        btn_start_all = ttk.Button(
            frm_window, 
            text = "Start Full Test", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_start_full_test_action(parent))
        btn_start_all.pack(anchor = 'center', pady = 5)






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

    def help_action(self, _parent):
        _parent.help_popup(self)
        

    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_start_full_test_action(self, _parent):
        self.gui_cfg = self.data_holder.getGUIcfg()
        checkbox_states = self.data_holder.data_dict.get("checkbox_states",[])
        ready_channels = []
        print('\n')
        print("Channel States", checkbox_states)
        for i in range(len(checkbox_states)):
            if checkbox_states[i] != 'excluded':
                ready_channels.append(True)
            else:
                ready_channels.append(False)

        print('\n')
        print("Ready Channels", ready_channels)
        print('\n')
        #try:
        print("ThermalTestBeginScene: Sending REQ to ThermalREQClient...")
        sending_REQ = ThermalREQClient(
            self.gui_cfg,
            'startCycle',
            ready_channels,
            self.data_holder.data_dict['current_full_ID'],
            self.data_holder.data_dict['user_ID'],
            self.conn_trigger
            )
        print("ThermalTestBeginScene: Completed REQ to ThermalREQClient...")
        #except Exception as e:
        #    messagebox.showerror('Exception', e)
        self.begin_update(self.parent.master_window, self.parent.queue, self.parent)

        _parent.set_frame_thermal_test_in_progress()
         
    def get_parent(self):
        return self.parent
    
    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        logger.info("TestScene: Successfully logged out from the TestScene.")
        result = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if result:
            _parent.set_frame_login_frame()


    #################################################

    def begin_update(self, master_window, queue, parent):
        print("\nBeginning to update... Looking for new information...\n")

        received_data = False
        json_received = None
        while not received_data:
            if not queue.empty():
                print("ThermalTestInProgressScene: Queue is not empty...")
                signal=queue.get()
                print(f"ThermalTestInProgressScene: signal = {signal}")

                if "Results received successfully." in signal:
                    # self.data_holder.update_from_json_string(message) 
                    message='FOO'
                    message=self.conn_trigger.recv()
                    print("message from conn_trigger:", message)
                    logger.info("ThermalTestInProgressScene: JSON Received.")
                    logger.info(message)
                    json_received=message
                    received_data = True
                # else:
                #     topic, message = signal.split(" ; ")
                #     print("signal:", signal, "\ntopic:", topic, "message", message)
                #     if (topic == "print"):
                #         print(message) 
                #     if (topic == "Done."):
                #         received_data = True

            time.sleep(0.01)

        if json_received:
            print("startCycle has started")
        else:
            print("ThermalTestInProgressScene: No json received after allotted time.")
    





