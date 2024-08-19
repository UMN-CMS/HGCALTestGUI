#################################################################################

import PythonFiles
import json, logging
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk as iTK
from PIL import Image
from matplotlib.pyplot import table
from pyparsing import col
import PythonFiles
import os
import datetime

#################################################################################

logging.getLogger('PIL').setLevel(logging.WARNING)


logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.PostScanScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Frame that shows up after board has been entered with info about the board
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class PostScanScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        self.data_holder = data_holder

        self.master_frame = master_frame

        super().__init__(self.master_frame, width = 1300-213, height = 700)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        logger.info("PostScanScene: Frame has been created.")

        self.parent = parent
       
        self.create_frame(parent)        

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')

    def create_frame(self, parent):
        self.create_style(parent)

        logger.debug("PostScanScene: Destroying old widgets on the SummaryScene.")
        print("PostScanScene: Destroying old widgets on the SummaryScene.")
        
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logger.warning("PostScanScene:Widgets could not be found and/or destroyed (making room for new widgets.")
        else:
            logger.info("PostScanScene: Widgets destroyed successfully (making room for new widgets).")
        

        self.canvas = tk.Canvas(self)
        self.frame = ttk.Frame(self.canvas, width=800, height=500)
        self.scroller = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroller.set)

        self.canvas.grid(row = 0, column = 0, sticky='nsew')
        self.scroller.grid(row=0, column=1, sticky='nsw')
        self.window = self.canvas.create_window((0,0), window=self.frame, anchor='nw', tags='self.frame')
        
        #resizing
        self.frame.pack(fill='both', expand=True)

        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.frame.bind('<Enter>', self.onEnter)
        self.frame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)
        
        self.frame.grid_columnconfigure(1, weight = 1)
        self.frame.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        if self.data_holder.data_dict['prev_results']:

            # Adds the title to the Summary Frame
            self.title = ttk.Label(
                    self.frame, 
                    text = "Board Scanned!",
                    font = ('Arial', 32)
                    )
            self.title.grid(row= 0, column= 1,  pady = 20)

            # Adds Board Full ID to the SummaryFrame
            self.id = ttk.Label(
                    self.frame, 
                    text = str(self.data_holder.data_dict['current_full_ID']),
                    font=('Arial',32,'bold')
                    )
            self.id.grid(row= 0, column= 2, pady = 20)

            green_check = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
            green_check = green_check.resize((75, 75), Image.LANCZOS)
            green_check = iTK.PhotoImage(green_check)

            redx = Image.open('{}/Images/RedX.png'.format(PythonFiles.__path__[0]))
            redx = redx.resize((75, 75), Image.LANCZOS)
            redx = iTK.PhotoImage(redx)
            # adds previously run tests to the canvas with pass/fail info
            try:
                if self.data_holder.data_dict['test_names']:
                    res_dict = {}
                    for n in self.data_holder.data_dict['test_names']:
                        res_dict[n] = []
                    for idx,el in enumerate(self.data_holder.data_dict['prev_results']):
                        res_dict[el[0]] = el[1]

                    for idx,el in enumerate(res_dict.keys()):
                        self.lbl_res = ttk.Label(
                                self.frame,
                                text = str(el) + ': ',
                                font=('Arial',24)
                                )
                        self.lbl_res.grid(row=idx+5, column=1, pady = 7)
                        if res_dict[el] == 'Passed':
                            self.lbl_img = ttk.Label(
                                    self.frame,
                                    image = green_check,
                                    font=('Arial',24)
                                    )
                            self.lbl_img.image=green_check
                            self.lbl_img.grid(row=idx+5, column=2, pady = 7)
                        elif res_dict[el] == 'Failed':
                            self.lbl_img = ttk.Label(
                                    self.frame,
                                    image = redx,
                                    font=('Arial',24)
                                    )
                            self.lbl_img.image=redx
                            self.lbl_img.grid(row=idx+5, column=2, pady = 7)
                        else:
                            self.lbl_res = ttk.Label(
                                    self.frame,
                                    text = 'This test has not been run.',
                                    font=('Arial',24)
                                    )
                            self.lbl_res.grid(row=idx+5, column=2, pady = 7)
                            
                else:
                    self.lbl_res = ttk.Label(
                            self.frame,
                            text = str(self.data_holder.data_dict['prev_results']),
                            font=('Arial',24)
                            )
                    self.lbl_res.grid(row=2, column=1)

            except Exception as e:
                print(e)
                self.lbl_full = ttk.Label(
                        self, 
                        text = 'Error, No Results',
                        font=('Arial', 24) 
                        )
                self.lbl_full.grid(row = 2, column =1, pady = 10) 

            # Creating the proceed button
            proceed_button = ttk.Button(
                self,
                #relief = tk.RAISED,
                text = "Proceed",
                command = lambda: self.btn_proceed_action(parent)
            )
            proceed_button.grid(sticky = 's', padx = 10, pady = 25)

        else:
            self.lbl_1 = ttk.Label(
                    self, 
                    text = "This board hasn't been checked in.",
                    font=('Arial', 32) 
                    )
            self.lbl_1.grid(row = 0, column =0, pady = 10, sticky = 'n' ) 

            self.lbl_2 = ttk.Label(
                    self, 
                    text = "Please visit the check in and inspection station.",
                    font=('Arial', 32) 
                    )
            self.lbl_2.grid(row = 1, column =0, pady = 10, sticky = 'n') 

        logout_frm = ttk.Frame(self)
        logout_frm.grid(sticky = 'se')

        #creating the next board buttom
        next_board_button = ttk.Button(
            logout_frm,
            text = "Change Boards",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.grid(row=0, column=0, padx = 10, pady = 10)
 

        # Creating the logout button
        btn_logout = ttk.Button(
            logout_frm,
            #relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.grid(row=1, column=0, padx = 10, pady = 10)

 

    #################################################

    def btn_proceed_action(self, _parent):
        #_parent.scan_frame_progress()
        _parent.set_frame_camera_frame(0)

    def btn_NextBoard_action(self, parent):
        parent.set_frame_scan_frame()

    def btn_logout_action(self, parent):
        parent.set_frame_login_frame() 

    def get_submit_action(self):
        return self.btn_proceed_action

    def get_parent(self):
        return self.parent
        
    
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
