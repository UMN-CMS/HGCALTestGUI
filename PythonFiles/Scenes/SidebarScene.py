#################################################################################

import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from tkinter import Scrollbar
from PIL import ImageTk as iTK
from PIL import Image
import logging
import PythonFiles
import os
import platform


#################################################################################

logger = logging.getLogger("HGCALTestGUI.PythonFiles.Scenes.SidebarScene")


class SidebarScene(tk.Frame):
    def __init__(self, parent, sidebar_frame, data_holder):
        super().__init__(
            sidebar_frame, width=213, height=650, bg="#808080", padx=10, pady=10
        )

        self.Green_Check_Image = Image.open(
            "{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0])
        )
        self.Green_Check_Image = self.Green_Check_Image.resize((50, 50), Image.LANCZOS)
        self.Green_Check_PhotoImage = iTK.PhotoImage(self.Green_Check_Image)
        self.Red_X_Image = Image.open(
            "{}/Images/RedX.png".format(PythonFiles.__path__[0])
        )
        self.Red_X_Image = self.Red_X_Image.resize((50, 50), Image.LANCZOS)
        self.Red_X_PhotoImage = iTK.PhotoImage(self.Red_X_Image)

        ############

        self.mycanvas = tk.Canvas(self, background="#808080", width=213, height=650)
        self.viewingFrame = tk.Frame(
            self.mycanvas, background="#808080", width=213, height=650
        )
        self.scroller = ttk.Scrollbar(
            self, orient="vertical", command=self.mycanvas.yview
        )
        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        self.mycanvas.pack(side="right")
        self.scroller.pack(side="left", fill="both", expand=True)

        self.canvas_window = self.mycanvas.create_window(
            (4, 4), window=self.viewingFrame, anchor="nw", tags="self.viewingFrame"
        )

        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind("<Enter>", self.onEnter)
        self.viewingFrame.bind("<Leave>", self.onLeave)

        self.onFrameConfigure(None)

        self.data_holder = data_holder

        self.update_sidebar(parent)

    #################################################

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.mycanvas.configure(
            scrollregion=self.mycanvas.bbox("all")
        )  # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        """Reset the canvas window to encompass inner frame when required"""
        pass
        # canvas_width = event.width
        # self.mycanvas.itemconfig(self, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    #################################################
    def update_sidebar(self, _parent):
        logger.info("SidebarScene: The sidebar has been updated.")

        # Variables for easy button editing
        btn_height = 3
        btn_width = 18
        btn_font = ("Arial", 10)
        btn_pady = 5

        self.btn_login = tk.Button(
            self.viewingFrame,
            pady=btn_pady,
            text="LOGIN PAGE",
            height=btn_height,
            width=btn_width,
            font=btn_font,
        )
        self.btn_login.grid(column=0, row=0)

        self.btn_scan = tk.Button(
            self.viewingFrame,
            pady=btn_pady,
            text="SCAN PAGE",
            height=btn_height,
            width=btn_width,
            font=btn_font,
        )
        self.btn_scan.grid(column=0, row=1)

        tests = self.data_holder.getTests()
        self.test_btns = {}
        original_offset = 2

        for test in tests:
            tname = test["test_data"]["name"]
            test_state = self.data_holder.getTestState(test['id'])
            self.test_btns[tname] = tk.Button(
                self.viewingFrame,
                pady=btn_pady,
                text=tname,
                height=btn_height,
                width=btn_width,
                font=btn_font,
                command=lambda x=tname: self.btn_test_action(_parent, x),
            )
            self.test_btns[tname].grid(column=0, row=test["idx"] + original_offset)

            if test_state["passed"]:
                self.test_btns[tname].config(state="disabled")
                GreenCheck_Label = tk.Label(
                    self.viewingFrame,
                    image=self.Green_Check_PhotoImage,
                    width=50,
                    height=50,
                    bg="#808080",
                )
                GreenCheck_Label.grid(row=test["idx"], column=1)
            elif test_state["completed"]:
                RedX_Label = tk.Label(
                    self.viewingFrame,
                    image=self.Red_X_PhotoImage,
                    width=50,
                    heighttest=50,
                    bg="#808080",
                )
                RedX_Label.grid(row=test["idx"], column=1)

        self.btn_summary = tk.Button(
            self.viewingFrame,
            pady=btn_pady,
            text="TEST SUMMARY",
            height=btn_height,
            width=btn_width,
            font=btn_font,
            command=lambda: self.btn_summary_action(_parent),
        )
        self.btn_summary.grid(
            column=0, row=original_offset + self.data_holder.total_tests
        )

        self.report_btn = tk.Button(
            self.viewingFrame,
            pady=btn_pady,
            text="Report Bug",
            height=btn_height,
            width=btn_width,
            font=("Kozuka Gothic Pr6N L", 8),
            command=lambda: self.report_bug(_parent),
        )
        self.report_btn.grid(
            column=0, row=original_offset + self.data_holder.total_tests + 1
        )

        self.grid_propagate(0)

    #################################################

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.mycanvas.yview_scroll(1, "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")

    #################################################

    def report_bug(self, _parent):
        _parent.report_bug(self)

    def btn_test_action(self, _parent, test_id):
        _parent.set_frame_test(test_id)

    def btn_summary_action(self, _parent):
        _parent.set_frame_test_summary()

    #################################################

    def disable_all_btns(self):
        self.btn_login.config(state="disabled")
        self.btn_scan.config(state="disabled")
        for btn in self.test_btns.values():
            btn.config(state="disabled")
        self.btn_summary.config(state="disabled")

    #################################################

    def disable_all_but_log_scan(self):
        for btn in self.test_btns.values():
            btn.config(state="disabled")
        self.btn_summary.config(state="disabled")

    #################################################

    def disable_all_btns_but_scan(self):
        self.btn_login.config(state="disabled")
        for btn in self.test_btns.values():
            btn.config(state="disabled")
        self.btn_summary.config(state="disabled")

    #################################################

    def disable_all_btns_but_login(self):
        self.btn_login.config(state="normal")
        self.btn_scan.config(state="disabled")
        for btn in self.test_btns.values():
            btn.config(state="disabled")
        self.btn_summary.config(state="disabled")

    #################################################

    def disable_log_scan(self):
        self.btn_login.config(state="disabled")
        self.btn_scan.config(state="disabled")

    #################################################

    def disable_login_button(self):
        self.btn_login.config(state="disabled")

    #################################################

    def disable_scan_button(self):
        self.btn_scan.config(state="disabled")

    #################################################


#################################################################################
