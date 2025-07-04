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

logger = logging.getLogger('HGCAL_VI.PythonFiles.Scenes.SummaryScene')

# Frame that shows all of the final results
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class SummaryScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 850)

        self.create_style(parent)

        self.data_holder = data_holder

        self.parent = parent
       
        self.create_frame(parent)        

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)

    #################################################
    
    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    def create_frame(self, parent):
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            #logger.warning("SummaryScene: Widgets could not be found and/or destroyed (making room for new widgets.")
            pass
        else:
            #logger.info("SummaryScene: Widgets destroyed successfully (making room for new widgets).")
            pass
        
        self.canvas = tk.Canvas(self, width = 1105, height = 850, background = '#33393b')
        self.frame = ttk.Frame(self.canvas, width=1105, height=850)
        self.scroller = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroller.set)
        self.canvas.grid(row = 0, column = 0)
        self.scroller.grid(row=0, column=1, sticky='NSEW')
        self.window = self.canvas.create_window((4,4), window=self.frame, anchor='n', tags='self.frame')

        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.frame.bind('<Enter>', self.onEnter)
        self.frame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)

        if self.data_holder.data_dict['is_new_board'] == True:
            # Adds the title to the Summary Frame
            self.title = ttk.Label(
                    self.frame, 
                    #fg='#0d0d0d', 
                    text = "Board Checked in and Inspection Completed!",
                    font=('Arial',32,'bold')
                    )
            self.title.grid(row= 0, column= 1, pady = 50)

            self.id = ttk.Label(
                    self.frame, 
                    #fg='#0d0d0d', 
                    text = "Check In ID:" + str(self.data_holder.data_dict['in_id']),
                    font=('Arial',24,'bold')
                    )
            self.id.grid(row= 1, column= 1, pady = 20)

        else:
            # Adds the title to the Summary Frame
            self.title = ttk.Label(
                    self.frame, 
                    #fg='#0d0d0d', 
                    text = "Inspection Completed!",
                    font=('Arial',36,'bold')
                    )
            self.title.grid(row= 0, column= 1, pady = 20)


       # Adds Board full id to the SummaryFrame
        self.lbl_full = ttk.Label(
                self.frame, 
                text = "Full ID: " + str(self.data_holder.data_dict['current_full_ID']),
                font=('Arial', 18) 
                )
        self.lbl_full.grid(column = 1, row = 2, pady = 10) 


        # Adds Tester Name to the Summary Frame
        self.lbl_tester = ttk.Label(
                self.frame, 
                text = "User: " + self.data_holder.data_dict['user_ID'],
                font=('Arial', 18) 
                )
        self.lbl_tester.grid(column = 1, row = 3, pady = 10)

        # Adds comments to the Summary Frame
        self.lbl_com = ttk.Label(
                self.frame, 
                text = "Comments: " + self.data_holder.data_dict['comments'],
                font=('Arial', 18) 
                )
        self.lbl_com.grid(column = 1, row = 4, pady = 10)

        # Adds time to the Summary Frame
        self.lbl_time = ttk.Label(
                self.frame, 
                text = str(datetime.datetime.now()),
                font=('Arial', 18) 
                )
        self.lbl_time.grid(column = 1, row = 5, pady = (15, 150))

        # Creates the "table" as a frame object
        self.frm_table = ttk.Frame(self.frame)
        self.frm_table.grid(row = 8, column = 1, sticky = 's')

        # Where to start putting the JSON information
        starting_row = 4
        # Number of keys the data_holder.inspection_data dictionary
        key_count = 0

        # Loop through all of the keys in the data_holder.inspection_data dictionary
        for index,box in enumerate(self.data_holder.all_checkboxes[0]):
            key_count = key_count + 1

            key_label = ttk.Label(
                    self.frm_table,
                    text = box['text'],
                    #relief = 'ridge',
                    width=40,
                    #height=1,
                    font=('Arial', 30, "bold")
                    )
            key_label.grid(row = key_count , sticky = 'sw', column=1, padx = 15)

            # Correctly displays the booleans
            # If not a string, show as a boolean true/false
            l_text = "UNDEFINED"
            if not isinstance(box['value'], str):
                if (box['value']):
                    l_text = "True"
                else:
                    l_text = "False"
            else:
                l_text = value['value']

            result_label = ttk.Label(
                    self.frm_table,
                    text = l_text,
                    #relief = 'ridge',
                    width=40,
                    #height=1,
                    font=('Arial', 30, "bold")
                    )
            result_label.grid(row=key_count, column=3)

        comment_index = 0
        comment_title_text = "Comments:"
        comment_title = ttk.Label(
               self.frm_table,
               text = comment_title_text,
               #relief = 'ridge',
               width=40,
               #height=2,
               font=('Arial', 24, "bold")
               )
        comment_title.grid(row=key_count + 1, column=0)

        comment_text = str(self.data_holder.get_comment_dict(comment_index))
        comment_label = ttk.Label(
               self.frm_table,
               text = comment_text,
               #relief = 'ridge',
               width=40,
              #height=2,
               font=('Arial', 18, "bold")
               )
        comment_label.grid(row=key_count + 1, column=1)

        # Create frame for logout button
        nav_frame = ttk.Frame(self)
        nav_frame.grid(column = 3, row = 0, sticky = 'se', padx =5)

        #creating the next board button
        next_board_button = ttk.Button(
            nav_frame,
            #relief = tk.RAISED,
            text = "Submit and go to Next Board",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.grid(pady = 5,row=key_count+2, column=1, padx = 5)

        #creating redo check in button
        redo_checkin_button = ttk.Button(
            nav_frame,
            text = "Cancel and Start Over",
            command = lambda: self.btn_redo_action(parent)
        )
        redo_checkin_button.grid(pady = 5,row=key_count+3, column=1, padx = 5)

        # Creating the logout button
        btn_logout = ttk.Button(
            nav_frame,
            #relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.grid(row=key_count+4,pady = 5, column=1, padx = 5)
    


    #################################################

    def btn_NextBoard_action(self, parent):
        test_id = self.data_holder.send_to_DB()
        if test_id:
            parent.set_frame_scan_frame()

    def btn_logout_action(self, parent):
        parent.set_frame_login_frame() 
    
    def btn_redo_action(self, parent):
        parent.set_frame_scan_frame()

    def get_submit_action(self):
        return self.btn_NextBoard_action

    def get_parent(self):
        return self.parent

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
