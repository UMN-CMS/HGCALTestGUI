#################################################################################

# importing necessary modules
import tkinter as tk
import tkinter.ttk as ttk
import logging
import PythonFiles
import os

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.LoginScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# Creates a class that is called by the GUIWindow. 
# GUIWindow instantiates an object called login_frame.
# @param parent -> passes in GUIWindow as the parent.
# @param master_frame -> passes master_frame as the container for everything in the class.
# @param data_holder -> passes data_holder into the class so the data_holder functions can
#       be accessed within the class.
class LoginScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):

        super().__init__(master_frame, width=1300-225, height=800)
        self.data_holder = data_holder
        self.create_style(parent)
        self.update_frame(parent)
   
        self.parent = parent


    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')


    def update_frame(self, parent):

        for widget in self.winfo_children():
            widget.destroy()


        logger.info("LoginScene: Frame has been created.")


        # Creating a list of users for dropdown menu
        # Eventually need to add a way for a database to have control over this list
        User_List = self.data_holder.get_all_users()

        # Creating the title for the window
        lbl_title = ttk.Label(
            self, 
            text="Please Select Your Name", 
            )
        lbl_title.config(font = ('Arial', 52))
        lbl_title.pack(pady=75)

        # Creating intial value in dropdown menu
        self.user_selected = tk.StringVar(self)
        self.user_selected.set("") # default value is empty

        # Creating the dropdown menu itself
        self.opt_user_dropdown = tk.OptionMenu(
            self, 
            self.user_selected, # Tells option menu to use the created initial value
            *User_List # Tells the dropdown menu to use every index in the User_List list
            ) 
        self.opt_user_dropdown.pack(pady=15)
        self.opt_user_dropdown.config(width = 20)
        #self.opt_user_dropdown['menu'].configure(font = ('Arial', 12))

        # Traces when the user selects an option in the dropdown menu
        # When an option is selected, it calls the show_submit_button function
        self.user_selected.trace(
            'w', 
            lambda *args: self.show_submit_button()
            )

        # Creating the submit button
        # It does not get enabled until the user selects an option menu option
        self.btn_submit = ttk.Button(
            self, 
            text="Submit",
            #padx = 50,
            #pady = 10, 
            #relief=tk.RAISED, 
            command= lambda:  self.btn_submit_action(parent)
            )
        self.btn_submit.pack(pady = (25,0))
        self.btn_submit.config( state = 'disabled')

        # Creating the add user button
        self.btn_admin = ttk.Button(
            self, 
            text="Admin Tools",
            #padx = 20,
            #pady = 5, 
            #relief=tk.RAISED, 
            command= lambda:  self.btn_admin_action(parent)
            )
        self.btn_admin.pack(pady=40)



        # Creating the help button
        self.btn_help = ttk.Button(
            self,
            #relief = tk.RAISED,
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

    # Creates the function for the submit button command
    # @params "_parent" is also a parent like "parent", but it is a different "parent",
    # passes in GUIWindow
    def btn_submit_action(self, _parent):
        if (self.user_selected.get() != ""):
            # Sets the user_ID in the data_holder to the selected user
            self.data_holder.set_user_ID(self.user_selected.get())
            # Changes frame to scan_frame
            _parent.set_frame_scan_frame()
        else:
            pass
    
    def get_submit_action(self):
        return self.btn_submit_action

    def get_parent(self):
        return self.parent

    #################################################

    def btn_admin_action(self, _parent):
        pass_pop = PasswordPopup(_parent, self.data_holder)
    
    #################################################

    # A function to pack the submit button
    def show_submit_button(self):
        self.btn_submit.config(state = 'active')
    
    #################################################

class PasswordPopup():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.create_style(parent)
        self.password_popup(data_holder)
        self.parent = parent    

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')

    #################################################

    # Function to enter password for admin access
    def password_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("PasswordPopup: Prompting the user for the admin password")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Admin Access") 
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
            text = "Enter Admin Password",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2)

        self.password = ""
        self.user_password = tk.Entry(
            frm_popup,
            textvariable= self.password,
            font=('Arial', '15'),
            show = "*"
            )
        self.user_password.grid(column = 0, row = 1, columnspan = 2)

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
        self.data_holder.attempt_admin_access(self.user_password.get())
        print(self.data_holder.admin)
        if self.data_holder.admin == True:
            _parent.set_frame_admin_frame()
        else:
            fail_pop = FailedPopup(_parent, self.data_holder)

        self.popup.destroy()




#################################################################################

class FailedPopup():
    
    #################################################

    def __init__(self, parent, data_holder):
        self.password_popup(data_holder)
        self.parent = parent    

    #################################################

    # Function to enter password for admin access
    def password_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("PasswordPopup: Admin Access was denied.")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Admin Connection Failed") 
        self.popup.geometry("300x200+500+300")
        self.popup.pack_propagate(1) 
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = ttk.Frame(self.popup, width=300, height=200)
        frm_popup.grid(row=0, column=0, sticky='nsew')

        bind_func = self.cancel_function
        frm_popup.bind_all("<Return>", lambda event: bind_func())

        # Creates label in the frame
        lbl_popup = ttk.Label(
            frm_popup, 
            text = "Incorrect Password!",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2, pady = 25)

        # Creates retry and continue buttons
        btn_retry = ttk.Button(
             frm_popup,
             text = "Retry", 
             command = lambda: self.retry_function(self.parent)
             )
        btn_retry.grid(column = 0, row = 1)

        btn_ok = ttk.Button(
            frm_popup,
            text = "Cancel",
            command = lambda: self.cancel_function()
        )
        btn_ok.grid(column = 1, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)


    #################################################
    
    # Called when the "cancel" button is selected
    def cancel_function(self):
        self.popup.destroy()

    def retry_function(self, _parent):
        self.popup.destroy()
        pass_pop = PasswordPopup(_parent, self.data_holder)
        


#################################################################################
