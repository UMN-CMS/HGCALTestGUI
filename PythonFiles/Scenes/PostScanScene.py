import PythonFiles
import json, logging
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk as iTK
from PIL import Image
from matplotlib.pyplot import table
from pyparsing import col
import PythonFiles
import os
import datetime


logging.getLogger("PIL").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

class PostScanScene(tk.Frame):


    def __init__(self, parent, master_frame, data_holder):

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        self.data_holder = data_holder

        self.master_frame = master_frame

        super().__init__(self.master_frame)

        logger.info("PostScanScene: Frame has been created.")

        self.parent = parent
        # Setting weights of columns so the column 4 is half the size of columns 0-3
        # for i in range(self.data_holder.getNumTest()):
        #    self.columnconfigure(i, weight = 2)
        # self.columnconfigure(self.data_holder.getNumTest(), weight = 1)
        # Instantiates an updated table with the current data
        # self.create_updated_table(parent)
        green_check = Image.open(
            "{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0])
        )
        green_check = green_check.resize((75, 75), Image.LANCZOS)
        self.green_check = iTK.PhotoImage(green_check)

        redx = Image.open("{}//Images/RedX.png".format(PythonFiles.__path__[0]))
        redx = redx.resize((75, 75), Image.LANCZOS)
        self.redx = iTK.PhotoImage(redx)

        self.create_frame(parent)

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)


    def create_frame(self, parent):
        logger.debug("PostScanScene: Destroying old widgets on the SummaryScene.")
        print("PostScanScene: Destroying old widgets on the SummaryScene.")

        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logger.warning(
                "PostScanScene:Widgets could not be found and/or destroyed (making room for new widgets."
            )
        else:
            logger.info(
                "PostScanScene: Widgets destroyed successfully (making room for new widgets)."
            )

        self.canvas = tk.Canvas(self)
        self.frame = tk.Frame(self.canvas)
        self.scroller = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scroller.set)
        self.canvas.grid(row=0, column=0)
        self.scroller.grid(row=0, column=1, sticky="NSEW")
        self.window = self.canvas.create_window(
            (4, 4), window=self.frame, anchor="n", tags="self.frame"
        )

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.frame.bind("<Enter>", self.onEnter)
        self.frame.bind("<Leave>", self.onLeave)

        self.onFrameConfigure(None)

        # Adds the title to the Summary Frame
        self.title = tk.Label(
            self.frame, fg="#0d0d0d", text="Board Scanned!", font=("Arial", 18, "bold")
        )
        self.title.grid(row=0, column=1, pady=20)

        # Adds Board Serial Number to the SummaryFrame
        self.id = tk.Label(
            self.frame,
            fg="#0d0d0d",
            text=f"Serial Number: {self.data_holder.getActiveSerial()}",
            font=("Arial", 14, "bold"),
        )
        self.id.grid(row=1, column=1, pady=20)

        try:
            tests = self.data_holder.getTests()
            for test in tests:
                self.lbl_res = tk.Label(
                    self.frame, text=str(el) + ": ", font=("Arial", 14)
                )
                self.lbl_res.grid(row=idx + 2, column=1)
                if test["passed"]:
                    self.lbl_img = tk.Label(
                        self.frame,
                        image=self.green_check,
                        width=75,
                        height=75,
                        font=("Arial", 14),
                    )
                    self.lbl_img.image = green_check
                    self.lbl_img.grid(row=idx + 2, column=2)
                else:
                    self.lbl_img = tk.Label(
                        self.frame,
                        image=self.redx,
                        width=75,
                        height=75,
                        font=("Arial", 14),
                    )
                    self.lbl_img.image = redx
                    self.lbl_img.grid(row=idx + 2, column=2)
            if not tests:
                self.lbl_res = tk.Label(
                    self.frame,
                    text="prev results",
                    font=("Arial", 14),
                )
                self.lbl_res.grid(row=2, column=1)

        except Exception as e:
            print(e)
            self.lbl_snum = tk.Label(self, text="Error, No Results", font=("Arial", 14))
            self.lbl_snum.grid(row=2, column=1, pady=10)

        # Creates the "table" as a frame object
        self.frm_table = tk.Frame(self)
        self.frm_table.grid(row=4, column=1)

        # Where to start putting the JSON information
        starting_row = 4
        proceed_button = tk.Button(
            self.frame,
            relief=tk.RAISED,
            text="Proceed",
            command=lambda: self.btn_proceed_action(parent),
        )
        proceed_button.grid(row=1, column=3, padx=10, pady=10)

        # creating the next board buttom
        next_board_button = tk.Button(
            self.frame,
            relief=tk.RAISED,
            text="Back to Scan",
            command=lambda: self.btn_NextBoard_action(parent),
        )
        next_board_button.grid(row=2, column=3, padx=10, pady=10)

        # Creating the logout button
        btn_logout = tk.Button(
            self.frame,
            relief=tk.RAISED,
            text="Logout",
            command=lambda: self.btn_logout_action(parent),
        )
        btn_logout.grid(row=3, column=3, padx=10, pady=20)

    def btn_proceed_action(self, _parent):
        _parent.gotoGroup("tests")

    def btn_NextBoard_action(self, parent):
        parent.gotoScene("scan")

    def btn_logout_action(self, parent):
        parent.gotoScene("login")

    def update_frame(self):
        self.create_frame(self.parent)


    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onMouseWheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def onEnter(self, event):
        self.canvas.bind_all("<Button-4>", self.onMouseWheel)
        self.canvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")


