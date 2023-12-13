import tkinter as tk
from tkinter import messagebox
import tkinter.font as font
import logging

logging.getLogger("PIL").setLevel(logging.WARNING)
import PythonFiles
import os

from PythonFiles.utils.REQClient import REQClient


logger = logging.getLogger(__name__)


class TestScene(tk.Frame):
    def __init__(
        self,
        parent,
        master_frame,
        data_holder,
        test_id,
        test_config,
        queue,
        conn_trigger,
    ):
        super().__init__(master_frame, width=870, height=500, padx=5, pady=5)
        self.data_holder = data_holder
        self.queue = queue
        self.conn_trigger = conn_trigger

        self.test_config = test_config
        self.test_id = test_id
        self.test_name = self.test_config["name"]
        self.test_description_short = self.test_config["desc_short"]
        self.test_description_long = self.test_config["desc_long"]

        #self.update_frame(parent)

    def update_frame(self, parent):
        logger.debug("ParentTestClass: A test frame has been updated.")
        # Creates a font to be more easily referenced later in the code
        font_scene = ("Arial", 15)

        # Create a centralized window for information
        frm_window = tk.Frame(self, width=870, height=480)
        frm_window.grid(column=1, row=0, padx=223, pady=100)

        # Create a label for the tester's name
        lbl_tester = tk.Label(frm_window, text="Tester: ", font=font_scene)
        lbl_tester.pack(side="top")

        # Create an entry for the tester's name
        ent_tester = tk.Entry(frm_window, font=font_scene)
        ent_tester.insert(0, self.data_holder.getActiveUser())
        ent_tester.pack(side="top")
        ent_tester.config(state="disabled")

        # Create a label for the serial number box
        lbl_snum = tk.Label(frm_window, text="Serial Number: ", font=font_scene)
        lbl_snum.pack(side="top")

        # Create a entry for the serial number box
        ent_snum = tk.Entry(frm_window, font=font_scene)
        ent_snum.insert(0, self.data_holder.getActiveSerial())
        ent_snum.pack(side="top")
        ent_snum.config(state="disabled")

        # Create a label for the test about to be run
        lbl_test = tk.Label(frm_window, text="Current Test: ", font=font_scene)
        lbl_test.pack(side="top")

        # Create a entry for the test type
        self.ent_test = tk.Entry(frm_window, font=font_scene)
        self.ent_test.pack(side="top")
        self.ent_test.insert(0, self.test_name)
        self.ent_test.config(state="disabled")

        # Create a label for confirming test
        lbl_confirm = tk.Label(
            frm_window, text="Are you ready to begin the test?", font=font_scene
        )
        lbl_confirm.pack(side="top")

        self.lbl_desc_short = tk.Label(
            frm_window,
            text=self.test_description_short,
            wraplength=500,
            justify="left",
            font=font_scene,
        )

        self.lbl_desc_short.pack(side="top")

        self.lbl_desc = tk.Label(
            frm_window,
            text=self.test_description_long,
            wraplength=500,
            justify="left",
            font=font_scene,
        )

        self.lbl_desc.pack(side="top")

        # Create a button for confirming test
        btn_confirm = tk.Button(
            frm_window,
            text="Confirm",
            relief=tk.RAISED,
            command=lambda: self.btn_confirm_action(parent),
        )
        btn_confirm.pack(side="top")
        btn_confirm["font"] = font.Font(family="Arial", size=13)

        # if self.test_idx == 0:

        #    # Create a button for confirming test
        #    run_all_btn = tk.Button(
        #        frm_window,
        #        text="Run All Tests",
        #        relief=tk.RAISED,
        #        command=lambda: self.run_all_action(parent),
        #    )
        #    run_all_btn.pack(pady=20)
        #    run_all_btn["font"] = font.Font(family="Arial", size=13)

        # Create frame for logout button
        frm_logout = tk.Frame(self)
        frm_logout.grid(column=2, row=1, padx=5, sticky="e")

        # Create a logout button
        btn_logout = tk.Button(
            frm_logout,
            text="Logout",
            relief=tk.RAISED,
            command=lambda: self.btn_logout_action(parent),
        )
        btn_logout.pack(anchor="center")

        # Create a frame for the back button
        frm_back = tk.Frame(self)
        frm_back.grid(column=2, row=0, sticky="n", padx=5)

        # Create a rescan button
        btn_rescan = tk.Button(
            frm_back,
            text="Change Boards",
            relief=tk.RAISED,
            command=lambda: self.btn_rescan_action(parent),
        )
        btn_rescan.pack(anchor="n")

        # Creating the help button
        btn_help = tk.Button(
            frm_back,
            relief=tk.RAISED,
            text="Help",
            command=lambda: self.help_action(parent),
        )
        btn_help.pack(anchor="s", padx=10, pady=10)

        self.grid_propagate(0)

    def help_action(self, _parent):
        _parent.help_popup(self)

    def run_all_action(self, _parent):
        _parent.run_all_tests(self.test_id)

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.reset_board()

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        self.gui_cfg = self.data_holder.getGUIcfg()

        # try:
        test_client = REQClient(
            self.gui_cfg,
            "test{}".format(self.test_id),
            self.data_holder.getActiveSerial(),
            self.data_holder.getActiveUser(),
            self.conn_trigger,
        )
        # except Exception as e:
        #    messagebox.showerror('Exception', e)

        _parent.set_frame_test_in_progress(self.queue)

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        logger.info("TestScene: Successfully logged out from the TestScene.")
        _parent.set_frame_login_frame()
