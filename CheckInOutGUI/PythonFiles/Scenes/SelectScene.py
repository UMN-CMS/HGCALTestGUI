#################################################################################

# importing necessary modules
import tkinter as tk
import logging
import PythonFiles
import os

#################################################################################

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# Creates a class that is called by the GUIWindow. 
# GUIWindow instantiates an object called login_frame.
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.
class SelectScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):

        super().__init__(master_frame, width = 1105, height = 850)
        self.data_holder = data_holder
        self.update_frame(parent)


    def update_frame(self, parent):

        for widget in self.winfo_children():
            widget.destroy()


        logging.info("SelectScene: Frame has been created.")

        # Creating the title for the window
        lbl_title = tk.Label(
            self, 
            text="Select Check In or Check Out", 
            font=('Arial', '24')
            )
        lbl_title.pack(pady=75)

        self.btn_in = tk.Button(
                self,
                relief = tk.RAISED,
                text = 'Check In',
                height = 10,
                width = 40,
                command = lambda: self.btn_submit_action(parent, 'Check In')
        )
        self.btn_in.pack()
        self.btn_out = tk.Button(
                self,
                relief = tk.RAISED,
                text = 'Check Out',
                height = 10,
                width = 40,
                command = lambda: self.btn_submit_action(parent, 'Check Out')
        )
        self.btn_out.pack()

#        # Creating intial value in dropdown menu
#        self.check_selected = tk.StringVar(self)
#        self.check_selected.set("") # default value is empty
#
#        # Creating the dropdown menu itself
#        self.opt_check_dropdown = tk.OptionMenu(
#            self, 
#            self.check_selected, # Tells option menu to use the created initial value
#            *checklist # Tells the dropdown menu to use every index in the list
#            ) 
#        self.opt_check_dropdown.pack(pady=15)
#        self.opt_check_dropdown.config(width = 20, font = ('Arial', 13))
#        self.opt_check_dropdown['menu'].configure(font = ('Arial', 12))
#
#        # Traces when the user selects an option in the dropdown menu
#        # When an option is selected, it calls the show_submit_button function
#        self.check_selected.trace(
#            'w', 
#            lambda *args: self.show_submit_button()
#            )
#
#        # Creating the submit button
#        # It does not get enabled until the user selects an option menu option
#        self.btn_submit = tk.Button(
#            self, 
#            text="Submit",
#            padx = 50,
#            pady = 10, 
#            relief=tk.RAISED, 
#            command= lambda:  self.btn_submit_action(parent)
#            )
#        self.btn_submit.pack()
#        self.btn_submit.config(state = 'disabled')

        # Creating the help button
        self.btn_help = tk.Button(
            self,
            relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )   
        self.btn_help.pack(anchor = 's', padx = 10, pady = 20) 


        # Forces frame to stay the size of the main_window
        # rather than adjusting to the size of the widgets
        self.pack_propagate(0)

    

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    ################################################# 


    #################################################

    # Creates the function for the submit button command
    # @params "_parent" is also a parent like "parent", but it is a different "parent",
    # passes in GUIWindow
    def btn_submit_action(self, _parent, check_id):
            # Sets the check_ID in the data_holder to the selected user
        self.data_holder.set_check_ID(check_id)
        # Changes frame to scan_frame
        _parent.set_frame_scan_frame()

        self.data_holder.print()


    #################################################

    # To be given commands later, for now it is a dummy function
    def btn_add_user_action(self, _parent):
        _parent.set_frame_add_user_frame()
    
    #################################################

    # A function to pack the submit button
    def show_submit_button(self):
        logging.info("SelectScene: Check Type has been selected.")
        self.btn_submit.config(state = 'active')
    
    #################################################

    
#################################################################################
