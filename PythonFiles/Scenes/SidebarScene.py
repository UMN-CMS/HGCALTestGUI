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
import itertools as it


logger = logging.getLogger(__name__)


class SidebarScene(tk.Frame):
    def __init__(self, parent, sidebar_frame):
        self.parent = parent
        super().__init__(
            # sidebar_frame, width=213, height=650, bg="#808080", padx=10, pady=10
            sidebar_frame,
            bg="#808080",
            padx=10,
            pady=10,
        )
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.mycanvas = tk.Canvas(
            self, background="#808080"
        )  # , width=213, height=650)
        self.mycanvas.columnconfigure(0, weight=3)
        self.mycanvas.columnconfigure(1, weight=1)
        self.mycanvas.rowconfigure(0, weight=0)

        self.viewingFrame = ttk.Frame(self.mycanvas)
        self.scroller = ttk.Scrollbar(
            self, orient="vertical", command=self.mycanvas.yview
        )
        self.scroller.grid(row=0, column=0, sticky="nsew")
        self.mycanvas.grid(row=0, column=1, sticky="nsew")
        self.viewingFrame.grid(row=0, column=0, sticky="nsew")
        self.viewingFrame.columnconfigure(0, weight=1)

        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        # self.mycanvas.pack(side="right")
        # self.scroller.pack(side="left", fill="both", expand=True)

        self.canvas_window = self.mycanvas.create_window(
            (4, 4), window=self.viewingFrame, anchor="nw", tags="self.viewingFrame"
        )

        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind("<Enter>", self.onEnter)
        self.viewingFrame.bind("<Leave>", self.onLeave)

        self.onFrameConfigure(None)

    def setScenes(self, scenes, sidebar_groups):
        self.scenes = scenes
        self.groups = sidebar_groups
        self.createSidebar()

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

    def createSidebar(self):
        logger.info("Creating sidebar")
        # Variables for easy button editing
        btn_height = 3
        btn_font = ("Arial", 10)
        btn_pady = 5

        self.btns = {}
        for i, scene in enumerate(self.scenes):
            name = scene.scene_name
            sid = scene.scene_id
            btn = tk.Button(
                self.viewingFrame,
                pady=btn_pady,
                text=name,
                height=btn_height,
                font=btn_font,
                command=lambda x=sid: self.parent.gotoScene(x),
            )
            btn.grid(row=i, column=0, sticky="nsew")
            btn.orig_color = btn.cget("background")
            self.btns[scene.scene_id] = btn
        self.grid_propagate(0)

    def update_sidebar(self, parent):
        logger.info("SidebarScene: The sidebar has been updated.")
        scenes = self.scenes
        for i, scene in enumerate(scenes):
            logger.info(f"Updating button in sidebar for scene {scene.scene_id}")
            self.btns[scene.scene_id].config(
                bg="#98e5ed"
                if parent.current_scene_id == scene.scene_id
                else self.btns[scene.scene_id].orig_color
            )
            if scene.sidebar_annotation is not None:
                annot = scene.sidebar_annotation(self.viewingFrame)
                if annot:
                    annot.grid(row=i, column=1)
        self.grid_propagate(0)

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

    def report_bug(self, _parent):
        _parent.report_bug(self)

    def btn_test_action(self, _parent, test_id):
        _parent.set_frame_test(test_id)

    def btn_summary_action(self, _parent):
        _parent.set_frame_test_summary()

    def disable_all_btns(self):
        logger.debug("Disabling all buttons")

        for btn in self.btns.values():
            btn.config(state="disabled")

    def enable_all_btns(self):
        logger.debug("Enabling all buttons")
        for btn in self.btns.values():
            btn.config(state="normal")

    def enable_btn(self, scene_id):
        logger.debug(f"Enabling button {scene_id}")
        self.btns[scene_id].config(state="normal")

    def disable_btn(self, scene_id):
        logger.debug(f"Disabling button {scene_id}")
        self.btns[scene_id].config(state="disabled")
