################################################################################

# Importing necessary modules
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk as iTK
from PIL import Image
import logging
import PythonFiles
import os

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.SplashScene')

class SplashScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame):
        self.initialize_GUI(parent, master_frame)

    #################################################
    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark') 


    def initialize_GUI(self, parent, master_frame):
        super().__init__(master_frame, width=1300-213, height = 800)

        self.create_style(parent)

        # Creating Bethel Logo
        img_bethel_logo = Image.open("{}/Images/Bethel_Logo.png".format(PythonFiles.__path__[0]))
        img_bethel_logo = img_bethel_logo.resize((250,100), Image.LANCZOS)
        phimg_bethel_logo = iTK.PhotoImage(img_bethel_logo)
        lbl_bethel_logo = ttk.Label(self, image=phimg_bethel_logo, width=250)
        lbl_bethel_logo.image = phimg_bethel_logo

        lbl_bethel_logo.grid(row=0, column= 0, padx = 50, pady = 100)

        # Creating UMN Logo
        img_umn_logo = Image.open('{}/Images/UMN_Logo.png'.format(PythonFiles.__path__[0]))
        img_umn_logo = img_umn_logo.resize((250,100), Image.LANCZOS)
        phimg_umn_logo = iTK.PhotoImage(img_umn_logo)
        lbl_umn_logo = ttk.Label(self, image=phimg_umn_logo, width=250)
        lbl_umn_logo.image = phimg_umn_logo

        lbl_umn_logo.grid(row = 0 , column = 2, padx = 50, pady = 100)

        # Creating label for names
        lbl_names = ttk.Label(
            self,
            text = ' Created by:\n \n Bryan Crossman, \n Andrew Kirzeder, \n Garrett Schindler, \n & Rand Bovard',
            font = ('Arial', 15)
        )
        lbl_names.grid(row = 1, column = 1)

        self.grid_propagate(0)

    #################################################


#################################################################################
