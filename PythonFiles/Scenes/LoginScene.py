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

        super().__init__(master_frame, width=870, height=650)
        self.data_holder = data_holder
        self.create_style()
        self.update_frame(parent)

    def create_style(self):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '/home/cac23662/Public/WagonTestGUI/awthemes-10.4.0')
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
            #font=('Arial', '24')
            )
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
        self.btn_submit.pack()
        self.btn_submit.config(state = 'disabled')


        # Creating the add user button
        self.btn_add_user = ttk.Button(
            self, 
            text="Add User",
            #padx = 20,
            #pady = 5, 
            #relief=tk.RAISED, 
            command= lambda:  self.btn_add_user_action(parent)
            )
        self.btn_add_user.pack(pady=40)



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
            # Sets the user_ID in the data_holder to the selected user
        self.data_holder.set_user_ID(self.user_selected.get())
        # Changes frame to scan_frame
        _parent.set_frame_scan_frame()
        logger.info("LoginScene: Submit button was selected. End of method")

        # self.data_holder.print()

    #################################################

    # To be given commands later, for now it is a dummy function
    def btn_add_user_action(self, _parent):
        _parent.set_frame_add_user_frame()
    
    #################################################

    # A function to pack the submit button
    def show_submit_button(self):
        logger.info("LoginScene: User has been selected.")
        self.btn_submit.config(state = 'active')
    
    #################################################

    
#################################################################################
