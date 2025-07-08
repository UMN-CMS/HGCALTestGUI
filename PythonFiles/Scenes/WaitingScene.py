import tkinter as tk
from tkinter import ttk

class WaitingScene(ttk.Frame):
    def __init__(self, parent, master_frame):
        super().__init__(master_frame, width=1300-213, height=800)
        self.parent = parent
        self.grid_propagate(0)

        self.label = ttk.Label(
                self,
                text="Please wait...\nChecking selected Channels.",
                font=('Arial', 28),
                anchor='center',
                justify='center'
            )
        self.label.place(relx=0.5, rely=0.5, anchor="center")
