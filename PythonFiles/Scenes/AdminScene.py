
#################################################################################

# importing necessary modules
import tkinter as tk
import tkinter.ttk as ttk
import logging
import PythonFiles
import os

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.AdminScene')


# Creates a class that is called by the GUIWindow. 
# GUIWindow instantiates an object called add_user_scene.
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.

class AdminScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
        super().__init__(master_frame, width=1300-213, height=800)
        self.data_holder = data_holder
        self.create_style(parent)
        self.update_frame(parent)

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')
 

    def update_frame(self, parent):
        
        for widget in self.winfo_children():
            widget.destroy()
        
        # Creating the title for the window
        lbl_title = ttk.Label(
            self, 
            text="Admin Tools", 
            font=('Arial', '24')
            )
        lbl_title.pack(pady=(50,0))

        # Creating the submit button
        self.btn_submit = ttk.Button(
            self, 
            text="Add User",
            command= lambda:  self.btn_add_user_action(parent)
            )
        self.btn_submit.pack()
        
        # Creating the cancel button
        self.btn_submit = ttk.Button(
            self, 
            text="Specify Test Stand Info",
            command= lambda:  self.btn_teststand_action(parent)
            )
        self.btn_submit.pack()

        self.btn_submit = ttk.Button(
            self, 
            text="Add Tester Component Info",
            command= lambda:  self.btn_component_action(parent)
            )
        self.btn_submit.pack()

        # Forces frame to stay the size of the main_window
        # rather than adjusting to the size of the widgets
        self.pack_propagate(0)

    #################################################

    # Creates the function for the submit button command
    # @params "_parent" is also a parent like "parent", but it is a different "parent",
    # passes in GUIWindow
    def btn_add_user_action(self, _parent):  
        _parent.set_frame_add_user_frame()

    #################################################
    
    def btn_teststand_action(self, _parent): 
        popup1 = Popup1(_parent, self.data_holder)

    #################################################
    
    def btn_component_action(self, _parent): 
        popup3 = Popup3(_parent, self.data_holder)

    #################################################

#################################################################################


class Popup1():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.confirm_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("Teststand info is being specified.")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Select Test Stand Type") 
        self.popup.geometry("300x200+500+300")
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
            text = "Select Test Stand Type",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        # Creates retry and continue buttons
        btn_wagon = ttk.Button(
             frm_popup,
             text = "Wagon Tester", 
             command = lambda: self.wagon_function(self.parent)
             )
        btn_wagon.grid(column = 1, row = 1)

        btn_continue = ttk.Button(
            frm_popup,
            text = "Engine Tester",
            command = lambda: self.engine_function(self.parent)
        )
        btn_continue.grid(column = 0, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)


    #################################################
    
    def wagon_function(self, _parent):
        self.popup.destroy()
        self.data_holder.tester_type = 'Wagon'
        popup2 = Popup2(_parent, self.data_holder)
        
    #################################################

    def engine_function(self, _parent):
        self.popup.destroy()
        self.data_holder.tester_type = 'Engine'

        _parent.set_frame_admin_scan()


#################################################################################

class Popup2():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.confirm_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("Number of Wagon Wheels is being Specified.")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Select Test Stand Type") 
        self.popup.geometry("300x200+500+300")
        self.popup.pack_propagate(1) 
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = ttk.Frame(self.popup, width=300, height=200)
        frm_popup.grid(row=0, column=0, sticky='nsew')

        bind_func = self.continue_function
        frm_popup.bind_all("<Return>", lambda event: bind_func(self.parent))

        # Creates label in the frame
        lbl_popup = ttk.Label(
            frm_popup, 
            text = "Enter Number of Wagon Wheels",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        self.text = ""
        self.wagon_wheels = tk.Entry(
            frm_popup,
            textvariable= self.text,
            font=('Arial', '15'),
            )
        self.wagon_wheels.grid(column = 0, row = 1, columnspan = 2)

        # Creates retry and continue buttons
        btn_retry = ttk.Button(
             frm_popup,
             text = "Cancel", 
             command = lambda: self.cancel_function()
             )
        btn_retry.grid(column = 1, row = 2)

        btn_continue = ttk.Button(
            frm_popup,
            text = "Confirm",
            command = lambda: self.continue_function(self.parent)
        )
        btn_continue.grid(column = 0, row = 2)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(2, weight=1)


    #################################################
    
    # Called when the "cancel" button is selected
    def cancel_function(self):
        self.popup.destroy()
        
    #################################################

    # Called to continue on in the testing procedure
    def continue_function(self, _parent):  
        self.data_holder.wagon_tester_info['num_wagon_wheels'] = self.wagon_wheels.get()

        self.popup.destroy()
        _parent.set_frame_admin_scan()



#################################################################################


class Popup3():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.confirm_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("Tester component info is being updated.")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Select Test Stand Type") 
        self.popup.geometry("300x200+500+300")
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
            text = "Select Test Stand Type",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        # Creates retry and continue buttons
        btn_wagon = ttk.Button(
             frm_popup,
             text = "Wagon Tester", 
             command = lambda: self.wagon_function(self.parent)
             )
        btn_wagon.grid(column = 1, row = 1)

        btn_continue = ttk.Button(
            frm_popup,
            text = "Engine Tester",
            command = lambda: self.engine_function(self.parent)
        )
        btn_continue.grid(column = 0, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)


    #################################################
    
    def wagon_function(self, _parent):
        self.popup.destroy()
        self.data_holder.tester_type = 'Wagon'
        _parent.set_frame_tester_component_frame()
        
    #################################################

    def engine_function(self, _parent):
        self.popup.destroy()
        self.data_holder.tester_type = 'Engine'
        _parent.set_frame_tester_component_frame()


#################################################################################
