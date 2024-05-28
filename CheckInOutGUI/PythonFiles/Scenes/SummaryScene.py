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

# Frame that shows all of the final results
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class SummaryScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 850)

        logging.info("SummaryScene: Frame has been created.")

        self.data_holder = data_holder

        self.parent = parent
       
        self.create_frame(parent)        

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)

    #################################################
    
    def create_frame(self, parent):
        logging.debug("SummaryScene: Destroying old widgets on the SummaryScene.")
        print("SummaryScene: Destroying old widgets on the SummaryScene.")
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logging.warning("SummaryScene: Widgets could not be found and/or destroyed (making room for new widgets.")
        else:
            logging.info("SummaryScene: Widgets destroyed successfully (making room for new widgets).")
        

        logging.debug("SummaryScene: Table is being created with the results.")
        print("\n\nSummaryScene: Table is being created with the results.")
        
        self.canvas = tk.Canvas(self, width=800, height=500)
        self.frame = tk.Frame(self.canvas, width=800, height=500)
        self.scroller = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroller.set)
        self.canvas.grid(row = 0, column = 0)
        self.scroller.grid(row=0, column=1, sticky='NSEW')
        self.window = self.canvas.create_window((4,4), window=self.frame, anchor='n', tags='self.frame')

        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.frame.bind('<Enter>', self.onEnter)
        self.frame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)

        if self.data_holder.data_dict['in_id']:
            # Adds the title to the Summary Frame
            if self.data_holder.data_dict['check_ID'] == 'Check In':
                self.title = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "Board Checked In!",
                        font=('Arial',18,'bold')
                        )
                self.title.grid(row= 0, column= 1, pady = 20)

                self.id = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "Check In ID:" + str(self.data_holder.data_dict['in_id']),
                        font=('Arial',14,'bold')
                        )
                self.id.grid(row= 1, column= 1, pady = 20)

            if self.data_holder.data_dict['check_ID'] == 'Check Out':
                self.title = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "Board Checked Out!",
                        font=('Arial',18,'bold')
                        )
                self.title.grid(row= 0, column= 1, pady = 20)

                self.id = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "Check Out ID:" + str(self.data_holder.data_dict['in_id']),
                        font=('Arial',14,'bold')
                        )
                self.id.grid(row= 1, column= 1, pady = 20)

           # Adds Board Serial Number to the SummaryFrame
            self.lbl_snum = tk.Label(
                    self.frame, 
                    text = "Serial Number: " + str(self.data_holder.data_dict['current_serial_ID']),
                    font=('Arial', 14) 
                    )
            self.lbl_snum.grid(column = 1, row = 2, pady = 10) 


            # Adds Tester Name to the Summary Frame
            self.lbl_tester = tk.Label(
                    self.frame, 
                    text = "User: " + self.data_holder.data_dict['user_ID'],
                    font=('Arial', 14) 
                    )
            self.lbl_tester.grid(column = 1, row = 3, pady = 10)

            # Adds comments to the Summary Frame
            self.lbl_com = tk.Label(
                    self.frame, 
                    text = "Comments: " + self.data_holder.data_dict['comments'],
                    font=('Arial', 14) 
                    )
            self.lbl_com.grid(column = 1, row = 4, pady = 10)

            # Adds time to the Summary Frame
            self.lbl_time = tk.Label(
                    self.frame, 
                    text = str(datetime.datetime.now()),
                    font=('Arial', 14) 
                    )
            self.lbl_time.grid(column = 1, row = 5, pady = 10)

        else:
            # Adds the title to the Summary Frame
            if self.data_holder.data_dict['check_ID'] == 'Check In':
                self.title = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "This Board has already been Checked In",
                        font=('Arial',18,'bold')
                        )
                self.title.grid(row= 0, column= 1, pady = 20)
                
            if self.data_holder.data_dict['check_ID'] == 'Check Out':
                self.title = tk.Label(
                        self.frame, 
                        fg='#0d0d0d', 
                        text = "This Board has already been Checked Out",
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
                        else:
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
                            text = str(self.data_holder.data_dict['prev_results']),
                            font=('Arial',14)
                            )
                    self.lbl_res.grid(row=2, column=1)

            except Exception as e:
                print(e)
                self.lbl_snum = tk.Label(
                        self, 
                        text = "Some other error occured and Board was not entered. See logs for more info.",
                        font=('Arial', 14) 
                        )
                self.lbl_snum.grid(column = 1, row = 2, pady = 10) 

        #creating the next board buttom
        next_board_button = tk.Button(
            self.frame,
            relief = tk.RAISED,
            text = "Next Board",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.grid(row=1, column=3, padx = 10, pady = 10)
 

        # Creating the logout button
        btn_logout = tk.Button(
            self.frame,
            relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.grid(row=2, column=3, padx = 10, pady = 20)
    


    #################################################

    def btn_NextBoard_action(self, parent):
        parent.set_frame_scan_frame()

    def btn_logout_action(self, parent):
        parent.set_frame_login_frame() 

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
    
    #################################################

    def update_frame(self):
        self.create_frame(self.parent)



#################################################################################
