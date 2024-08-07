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

        super().__init__(self.master_frame, width = 1105, height = 850)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        logger.info("PostScanScene: Frame has been created.")

        self.parent = parent

        self.create_style(parent)
       
        self.create_frame(parent)        

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)

    #################################################

    def create_style(self, _parent):
        
        self.s = ttk.Style()
  
        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
  
        self.s.theme_use('awdark')

    def create_frame(self, parent):
        logger.debug("PostScanScene: Destroying old widgets on the PostScanScene.")
        print("PostScanScene: Destroying old widgets on the PostScanScene.")
        
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logger.warning("PostScanScene:Widgets could not be found and/or destroyed (making room for new widgets.")
        else:
            logger.info("PostScanScene: Widgets destroyed successfully (making room for new widgets).")
        
        self.canvas = tk.Canvas(self, width = 1105, height = 850, bg = "#33393b")
        self.frame = ttk.Frame(self.canvas, width = 1105, height = 850)

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
        self.title = ttk.Label(
                self.frame, 
                #fg='#0d0d0d', 
                text = "This Board has already been Checked In",
                font=('Arial',35,'bold')
                )
        self.title.grid(row= 0, column= 1, pady = 20)
            

        # Adds Board full id to the SummaryFrame
        self.id = ttk.Label(
                self.frame, 
                #fg='#0d0d0d', 
                text = "Full ID:  " + str(self.data_holder.data_dict['current_full_ID']),
                font=('Arial',24,'bold')
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
                    self.lbl_res = ttk.Label(
                            self.frame,
                            text = str(el) + ': ',
                            font=('Arial',14)
                            )
                    self.lbl_res.grid(row=idx+2, column=1)
                    if res_dict[el] == 'Passed':
                        self.lbl_img = ttk.Label(
                                self.frame,
                                image = green_check,
                                width=75,
                                #height=75,
                                font=('Arial',14)
                                )
                        self.lbl_img.image=green_check
                        self.lbl_img.grid(row=idx+2, column=2)
                    else:
                        self.lbl_img = ttk.Label(
                                self.frame,
                                image = redx,
                                width=75,
                                #height=75,
                                font=('Arial',14)
                                )
                        self.lbl_img.image=redx
                        self.lbl_img.grid(row=idx+2, column=2)
            else:
                self.lbl_res = ttk.Label(
                        self.frame,
                        text = str(self.data_holder.data_dict['prev_results']),
                        font=('Arial',14)
                        )
                self.lbl_res.grid(row=2, column=1)

        except Exception as e:
            print(e)
            self.lbl_err = ttk.Label(
                    self, 
                    text = "Some other error occured and Board was not entered. See logs for more info.",
                    font=('Arial', 14) 
                    )
            self.lbl_err.grid(column = 1, row = 2, pady = 10) 

 
        # Creating frame for logout button
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 3, row = 0, sticky= 'se')

        # Creating the proceed button
        proceed_button = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Proceed",
            command = lambda: self.btn_proceed_action(parent)
        )
        proceed_button.grid(row = 3, column = 0, padx = 10, pady = 25, sticky = 's')

        #creating the next board button
        next_board_button = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Change Boards",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.grid(row = 4,column =0 ,padx = 10, pady = 25, sticky = 's')

        #creating the component scan board button
        scan_components = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Check In Components",
            command = lambda: self.btn_components_action(parent)
        )
        scan_components.grid(row = 5,column =0 ,padx = 10, pady = 25, sticky = 's')

        # Creating the logout button
        btn_logout = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.grid(sticky = 's', padx = 10, pady = 0)

        # Creating the help button
        btn_help = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.grid(sticky = 's', padx = 10, pady = 10) 


    #################################################

    def btn_proceed_action(self, _parent):
        _parent.set_frame_inspection_frame()

    def btn_NextBoard_action(self, parent):
        parent.set_frame_scan_frame()

    def btn_components_action(self, parent):
        parent.first_frame_component_frame()

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
