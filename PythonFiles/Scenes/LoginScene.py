import tkinter as tk
import logging
import PythonFiles
import os

logger = logging.getLogger(__name__)


class LoginScene(tk.Frame):
    def __init__(self, parent, master_frame, data_holder):
        super().__init__(master_frame, width=870, height=500)
        self.data_holder = data_holder
        self.update_frame(parent)

    def update_frame(self, parent):
        for widget in self.winfo_children():
            widget.destroy()

        logger.info("Frame has been created.")

        # Creating a list of users for dropdown menu
        # Eventually need to add a way for a database to have control over this list
        User_List = self.data_holder.get_all_users()

        # Creating the title for the window
        lbl_title = tk.Label(self, text="Please Select Your Name", font=("Arial", "24"))
        lbl_title.pack(pady=75)

        # Creating intial value in dropdown menu
        self.user_selected = tk.StringVar(self)
        self.user_selected.set("")  # default value is empty

        # Creating the dropdown menu itself
        self.opt_user_dropdown = tk.OptionMenu(
            self,
            self.user_selected,  # Tells option menu to use the created initial value
            *User_List  # Tells the dropdown menu to use every index in the User_List list
        )
        self.opt_user_dropdown.pack(pady=15)
        self.opt_user_dropdown.config(width=20, font=("Arial", 13))
        self.opt_user_dropdown["menu"].configure(font=("Arial", 12))

        # Traces when the user selects an option in the dropdown menu
        # When an option is selected, it calls the show_submit_button function
        self.user_selected.trace("w", lambda *args: self.show_submit_button())

        # Creating the submit button
        # It does not get enabled until the user selects an option menu option
        self.btn_submit = tk.Button(
            self,
            text="Submit",
            padx=50,
            pady=10,
            relief=tk.RAISED,
            command=lambda: self.btn_submit_action(parent),
        )
        self.btn_submit.pack()
        self.btn_submit.config(state="disabled")

        # Creating the add user button
        self.btn_add_user = tk.Button(
            self,
            text="Add User",
            padx=20,
            pady=5,
            relief=tk.RAISED,
            command=lambda: self.btn_add_user_action(parent),
        )
        self.btn_add_user.pack(pady=40)

        # Creating the help button
        self.btn_help = tk.Button(
            self,
            relief=tk.RAISED,
            text="Help",
            command=lambda: self.help_action(parent),
        )
        self.btn_help.pack(anchor="s", padx=10, pady=20)

        # Forces frame to stay the size of the main_window
        # rather than adjusting to the size of the widgets
        self.pack_propagate(0)

    def help_action(self, _parent):
        _parent.help_popup(self)

    # Creates the function for the submit button command  passes in GUIWindow
    def btn_submit_action(self, _parent):
        user = self.user_selected.get()
        logger.info(f"Setting user to {user}")
        # Sets the user_ID in the data_holder to the selected user
        self.data_holder.set_user_ID(user)
        _parent.gotoScene("scan")
        logger.info("Submit button was selected. End of method")

    # To be given commands later, for now it is a dummy function
    def btn_add_user_action(self, _parent):
        _parent.set_frame_add_user_frame()

    # A function to pack the submit button
    def show_submit_button(self):
        logger.info("LoginScene: User has been selected.")
        self.btn_submit.config(state="active")
