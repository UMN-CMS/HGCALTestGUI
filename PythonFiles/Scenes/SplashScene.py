################################################################################

# Importing necessary modules
import tkinter as tk
from PIL import ImageTk as iTK
from PIL import Image
import logging
import PythonFiles

#################################################################################

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/shared/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'w', format=FORMAT, level=logging.DEBUG)

class SplashScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame):
        self.initialize_GUI(parent, master_frame)

    #################################################
    
    def initialize_GUI(self, parent, master_frame):
        super().__init__(master_frame, width = 850, height = 500)

        logging.info("SplashScene: Frame has been initialized.")
        # Creating Bethel Logo
        img_bethel_logo = Image.open("{}/Images/Bethel_Logo.png".format(PythonFiles.__path__[0]))
        img_bethel_logo = img_bethel_logo.resize((250,100), Image.ANTIALIAS)
        phimg_bethel_logo = iTK.PhotoImage(img_bethel_logo)
        lbl_bethel_logo = tk.Label(self, image=phimg_bethel_logo, width=250, height=100)
        lbl_bethel_logo.image = phimg_bethel_logo

        lbl_bethel_logo.grid(row=0, column= 0, padx = 50, pady = 100)

        # Creating UMN Logo
        img_umn_logo = Image.open('{}/Images/UMN_Logo.png'.format(PythonFiles.__path__[0]))
        img_umn_logo = img_umn_logo.resize((250,100), Image.ANTIALIAS)
        phimg_umn_logo = iTK.PhotoImage(img_umn_logo)
        lbl_umn_logo = tk.Label(self, image=phimg_umn_logo, width=250, height=100)
        lbl_umn_logo.image = phimg_umn_logo

        lbl_umn_logo.grid(row = 0 , column = 2, padx = 50, pady = 100)

        # Creating label for names
        lbl_names = tk.Label(
            self,
            text = ' Created by:\n \n Bryan Crosman, \n Andrew Kirzeder, \n & \n Garrett Schindler',
            font = ('Arial', 15)
        )
        lbl_names.grid(row = 1, column = 1)

        self.grid_propagate(0)

    #################################################


#################################################################################
