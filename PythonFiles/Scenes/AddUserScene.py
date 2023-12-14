import tkinter as tk
import logging
import PythonFiles
import os

logger = logging.getLogger(__name__)


class AddUserScene(tk.Frame):
    def __init__(self, parent, master_frame, data_holder):
        super().__init__(master_frame)
        logger.info("Frame has been created.")
        self.data_holder = data_holder
        self.update_frame(parent)

    def update_frame(self, parent):
        for widget in self.winfo_children():
            widget.destroy()

        # Creating the title for the window
        lbl_title = tk.Label(self, text="Add User", font=("Arial", "24"))
        lbl_title.pack(pady=(50, 0))

        # Creating entry box for new user's name
        self.new_user_name = ""
        self.user_entry = tk.Entry(
            self, textvariable=self.new_user_name, font=("Arial", "15")
        )
        self.user_entry.pack(pady=30)

        # Creating the title for the window
        password_label = tk.Label(
            self, text="Enter Admin Password", font=("Arial", "20")
        )
        password_label.pack(pady=(10, 0))

        # Creating entry box for new user's name
        self.password = ""
        self.user_password = tk.Entry(
            self, textvariable=self.password, font=("Arial", "15"), show="*"
        )
        self.user_password.pack(pady=30)

        # Creating the submit button
        self.btn_submit = tk.Button(
            self,
            text="Submit",
            padx=50,
            pady=10,
            relief=tk.RAISED,
            command=lambda: self.btn_submit_action(parent),
        )
        self.btn_submit.pack()

        # Creating the cancel button
        self.btn_submit = tk.Button(
            self,
            text="Cancel",
            padx=50,
            pady=10,
            relief=tk.RAISED,
            command=lambda: self.btn_cancel_action(parent),
        )
        self.btn_submit.pack()

        # Forces frame to stay the size of the main_window
        # rather than adjusting to the size of the widgets
        self.pack_propagate(0)

    #################################################

    # Creates the function for the submit button command
    # @params "_parent" is also a parent like "parent", but it is a different "parent",
    # passes in GUIWindow
    def btn_submit_action(self, _parent):
        self.new_user_name = self.user_entry.get()
        self.password = self.user_password.get()

        # Popup to confirm that a new user is added into the DB
        cnfm_pop = ConfirmPopup(
            _parent, self.data_holder, self.new_user_name, self.password
        )

    #################################################

    def btn_cancel_action(self, _parent):
        _parent.set_frame_login_frame()

    #################################################


#################################################################################


class ConfirmPopup:
    #################################################

    def __init__(self, parent, data_holder, new_user_name, password):
        print("\n\n\n\n\n{}\n\n\n\n".format(parent))
        self.confirm_popup(data_holder, new_user_name, password)
        self.parent = parent

    #################################################

    # Function to make retry or continue window if the test fails
    def confirm_popup(self, data_holder, new_user_name, password):
        self.data_holder = data_holder
        self.new_user_name = new_user_name
        self.password = password
        logger.info(
            "Confirming that the user wants to add {}".format(self.new_user_name)
        )
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("New User Name")
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup,
            text=" You are about to add {} as a user \n Are you sure? ".format(
                self.new_user_name
            ),
            font=("Arial", 13),
        )
        lbl_popup.grid(column=0, row=0, columnspan=2, pady=25)

        # Creates retry and continue buttons
        btn_retry = tk.Button(
            frm_popup,
            width=8,
            height=2,
            text="Cancel",
            relief=tk.RAISED,
            font=("Arial", 12),
            command=lambda: self.cancel_function(),
        )
        btn_retry.grid(column=0, row=1)

        btn_continue = tk.Button(
            frm_popup,
            width=8,
            height=2,
            text="Confirm",
            relief=tk.RAISED,
            font=("Arial", 12),
            command=lambda: self.continue_function(self.parent),
        )
        btn_continue.grid(column=1, row=1)

    # Called when the "cancel" button is selected
    def cancel_function(self):
        self.popup.destroy()

    # Called to continue on in the testing procedure
    def continue_function(self, _parent):
        self.popup.destroy()

        # Adding a new user name to data_holder/DB
        logger.info(
            "Going to DataHolder to try to add {} as a username".format(
                self.new_user_name
            )
        )
        self.data_holder.add_new_user_name(self.new_user_name, self.password)
        # Changes frame to scan_frame
        _parent.set_frame_login_frame()
