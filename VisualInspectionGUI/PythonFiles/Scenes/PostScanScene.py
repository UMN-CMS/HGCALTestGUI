#################################################################################

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

#################################################################################

logging.getLogger('PIL').setLevel(logging.WARNING)


logger = logging.getLogger('HGCAL_GUI')
FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Frame that shows the results of any previous tests and asks the operator how they want to proceed

class PostScanScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 850)

        logging.info("PostScanScene: Frame has been created.")

        self.data_holder = data_holder

        self.parent = parent
       
        self.create_frame(parent)        

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)

    #################################################
    
    def create_frame(self, parent):
        logging.debug("PostScanScene: Destroying old widgets on the SummaryScene.")
        print("PostScanScene: Destroying old widgets on the SummaryScene.")
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logging.warning("PostScanScene:Widgets could not be found and/or destroyed (making room for new widgets.")
        else:
            logging.info("PostScanScene: Widgets destroyed successfully (making room for new widgets).")
        
        # creates a canvas to put things on
        # need a canvas to be able to scroll
        self.canvas = tk.Canvas(self, width=800, height=600)
        self.frame = tk.Frame(self.canvas, width=800, height=600)
        # allows for scrolling if tests go off the page
        self.scroller = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroller.set)
        self.canvas.grid(row = 0, column = 0)
        self.scroller.grid(row=0, column=1, sticky='NSEW')
        self.window = self.canvas.create_window((4,4), window=self.frame, anchor='n', tags='self.frame')

        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.frame.bind('<Enter>', self.onEnter)
        self.frame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)

        # Adds the title to the Summary Frame
        self.title = tk.Label(
                self.frame, 
                fg='#0d0d0d', 
                text = "Board Scanned!",
                font=('Arial',18,'bold')
                )
        self.title.grid(row= 0, column= 1, pady = 20)

        # Adds Board Serial Number to the SummaryFrame
        self.id = tk.Label(
                self.frame, 
                fg='#0d0d0d', 
                text = "Serial Number:" + str(self.data_holder.data_dict['current_serial_ID']),
                font=('Arial',14,'bold')
                )
        self.id.grid(row= 1, column= 1, pady = 20)

        green_check = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
        green_check = green_check.resize((75, 75), Image.LANCZOS)
        green_check = iTK.PhotoImage(green_check)

        redx = Image.open('{}//Images/RedX.png'.format(PythonFiles.__path__[0]))
        redx = redx.resize((75, 75), Image.LANCZOS)
        redx = iTK.PhotoImage(redx)
        # creates the table with the previous result data
        try:
            if self.data_holder.data_dict['test_names']:
                res_dict = {}
                for n in self.data_holder.data_dict['test_names']:
                    res_dict[n] = []
                for idx,el in enumerate(self.data_holder.data_dict['prev_results']):
                    res_dict[el[0]] = el[1]

                for idx,el in enumerate(res_dict.keys()):
                    self.lbl_res = tk.Label(
                            self.frame,
                            text = str(el) + ': ',
                            font=('Arial',14)
                            )
                    self.lbl_res.grid(row=idx+2, column=1)
                    if res_dict[el] == 'Passed':
                        self.lbl_img = tk.Label(
                                self.frame,
                                image = green_check,
                                width=75,
                                height=75,
                                font=('Arial',14)
                                )
                        self.lbl_img.image=green_check
                        self.lbl_img.grid(row=idx+2, column=2)
                    elif res_dict[el] == 'Failed':
                        self.lbl_img = tk.Label(
                                self.frame,
                                image = redx,
                                width=75,
                                height=75,
                                font=('Arial',14)
                                )
                        self.lbl_img.image=redx
                        self.lbl_img.grid(row=idx+2, column=2)
                    else:
                        self.lbl_res = tk.Label(
                                self.frame,
                                text = 'This test has not been run.',
                                font=('Arial',14)
                                )
                        self.lbl_res.grid(row=idx+2, column=2)
            else:
                self.lbl_res = tk.Label(
                        self.frame,
                        text = str(self.data_holder.data_dict['prev_results']),
                        font=('Arial',14)
                        )
                self.lbl_res.grid(row=2, column=1)

        except Exception as e:
            print(e)
            self.lbl_snum = tk.Label(
                    self, 
                    text = 'Error, No Results',
                    font=('Arial', 14) 
                    )
            self.lbl_snum.grid(row = 2, column =1, pady = 10) 

        

        # Creating the proceed buttons
        proc_button = tk.Button(
            self.frame,
            relief = tk.RAISED,
            text = "Next",
            command = lambda: self.btn_proc_action(parent)
        )
        proc_button.grid(row=1, column=3, padx = 10, pady = 10)

        #creating the next board buttom
        next_board_button = tk.Button(
            self.frame,
            relief = tk.RAISED,
            text = "Back to Scan",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.grid(row=2, column=3, padx = 10, pady = 10)
 

        # Creating the logout button
        btn_logout = tk.Button(
            self.frame,
            relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.grid(row=3, column=3, padx = 10, pady = 20)
 
    


    #################################################

    def btn_proc_action(self, parent):
        parent.set_frame_inspection_frame()

    def btn_NextBoard_action(self, parent):
        parent.set_frame_scan_frame()

    def btn_logout_action(self, parent):
        parent.set_frame_login_frame() 

        
    
    #################################################

    def update_frame(self):
        self.create_frame(self.parent)

    #################################################

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def onMouseWheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self.canvas.yview_scroll(1, 'units')

    def onEnter(self, event):
        self.canvas.bind_all('<Button-4>', self.onMouseWheel)
        self.canvas.bind_all('<Button-5>', self.onMouseWheel)

    def onLeave(self, event):
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')



#################################################################################
