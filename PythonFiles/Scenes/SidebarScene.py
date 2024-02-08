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

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.SidebarScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

class SidebarScene(tk.Frame):

    #################################################

    def __init__(self, parent, sidebar_frame, data_holder):


        super().__init__( sidebar_frame, width=213, height = 650, bg = '#808080', padx = 10, pady=10)

        self.Green_Check_Image = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
        self.Green_Check_Image = self.Green_Check_Image.resize((50,50), Image.LANCZOS)
        self.Green_Check_PhotoImage = iTK.PhotoImage(self.Green_Check_Image)
        self.Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        self.Red_X_Image = self.Red_X_Image.resize((50,50), Image.LANCZOS)
        self.Red_X_PhotoImage = iTK.PhotoImage(self.Red_X_Image)
        

        ############        
        
        self.mycanvas = tk.Canvas(self, background="#808080", width=213, height =650)
        self.viewingFrame = tk.Frame(self.mycanvas, background = "#808080", width = 213, height = 650)
        self.scroller = ttk.Scrollbar(self, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        self.mycanvas.pack(side="right")
        self.scroller.pack(side="left", fill="both", expand=True)


        self.canvas_window = self.mycanvas.create_window((4,4), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")





        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)


        self.data_holder = data_holder

        self.update_sidebar(parent)

    #################################################

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.mycanvas.configure(scrollregion=self.mycanvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        pass
        #canvas_width = event.width
        #self.mycanvas.itemconfig(self, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.


    #################################################
    def update_sidebar(self, _parent):
        
        logger.info("SidebarScene: The sidebar has been updated.")

                # Variables for easy button editing
        btn_height = 3
        btn_width = 18
        btn_font = ('Arial', 10)
        btn_pady = 5

        self.btn_login = tk.Button(
            self.viewingFrame,
            pady = btn_pady,
            text = 'LOGIN PAGE',
            height = btn_height,
            width = btn_width,
            font = btn_font
        )
        self.btn_login.grid(column = 0, row = 0)

        self.btn_scan = tk.Button(
            self.viewingFrame,
            pady = btn_pady,
            text = 'SCAN PAGE',
            height = btn_height,
            width = btn_width,
            font = btn_font
        )
        self.btn_scan.grid(column = 0, row = 1)

        test_names = self.data_holder.getTestNames()
        physical_names = self.data_holder.getPhysicalNames()
        print('\n\n\n\n\n\n\n\n')
        print(test_names)
        print(physical_names)

        self.test_btns = []

        # Offset = number of buttons before the test buttons begin
        original_offset = 2
        
        # How much offset from the physical board tests
        physical_offset = 0

        print("\nThere are {} physical tests\n".format(self.data_holder.getNumPhysicalTest()))

        for i in range(self.data_holder.getNumPhysicalTest()): 
            #print("Physical Button should point to the {} test".format(i + physical_offset))
            self.test_btns.append(tk.Button(
                self.viewingFrame, 
                pady = btn_pady,
                text = '{}'.format(physical_names[i]),
                height = btn_height,
                width = btn_width,
                font = btn_font,
                command = lambda i=i: self.btn_test_action(_parent, i)
                ))
            self.test_btns[i].grid(column = 0, row = i + original_offset)

            #print(self.data_holder.data_dict)

            if self.data_holder.data_dict['physical{}_pass'.format(i+1)] == True:
                self.test_btns[i].config(state = 'disabled')
            
            physical_offset = physical_offset + 1


        #
        ## For the digital buttons
        #
        digital_offset = 0

        for i in range(self.data_holder.getNumTest()):
            
            #print("Digi Button should point to the {} test".format(i + physical_offset))
            self.test_btns.append(tk.Button(
                self.viewingFrame, 
                pady = btn_pady,
                text = '{}'.format(test_names[i]),
                height = btn_height,
                width = btn_width,
                font = btn_font,
                command = lambda i=i: self.btn_test_action(_parent, i + physical_offset)
                ))
            self.test_btns[i+physical_offset].grid(column = 0, row = physical_offset + original_offset + i)

            if self.data_holder.data_dict['test{}_pass'.format(i+1)] == True:
                self.test_btns[i+physical_offset].config(state = 'disabled')
            
            digital_offset = digital_offset + 1
        
        self.btn_summary = tk.Button(
            self.viewingFrame, 
            pady = btn_pady,
            text = 'TEST SUMMARY',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_summary_action(_parent)
            )
        self.btn_summary.grid(column = 0, row = physical_offset + original_offset + digital_offset)

        
        self.report_btn = tk.Button(
            self.viewingFrame, 
            pady = btn_pady,
            text = 'Report Bug',
            height = btn_height,
            width = btn_width,
            font = ('Kozuka Gothic Pr6N L', 8),
            command = lambda: self.report_bug(_parent)
            )
        self.report_btn.grid(column = 0, row = physical_offset + original_offset + digital_offset + 1)
        


        # List for creating check marks with for loop
        self.list_of_pass_fail = self.data_holder.data_lists['test_results']



        # For loop to create checkmarks based on pass/fail
        for index in range(len(self.list_of_pass_fail)):
            #print("Pass fail:", self.list_of_pass_fail)
            if(self.list_of_pass_fail[index] == True):
                # Create a photoimage object of the QR Code
                GreenCheck_Label = tk.Label(self.viewingFrame, image=self.Green_Check_PhotoImage, width=50, height=50, bg = '#808080')
                GreenCheck_Label.image = self.Green_Check_PhotoImage
                GreenCheck_Label.grid(row=index + original_offset + physical_offset, column=1)

            else:
                # Create a photoimage object of the QR Code
                RedX_Label = tk.Label(self.viewingFrame, image=self.Red_X_PhotoImage, width=50, height=50, bg = '#808080')
                RedX_Label.image = self.Red_X_PhotoImage
                RedX_Label.grid(row=index + original_offset + physical_offset, column=1)

        self.physical_pass_fail = self.data_holder.data_lists['physical_results']
        
        # For loop to create checkmarks based on pass/fail
        for index in range(len(self.physical_pass_fail)):
            #print("Pass fail:", self.physical_pass_fail)
            if(self.physical_pass_fail[index] == True):
                # Create a photoimage object of the QR Code
                GreenCheck_Label = tk.Label(self.viewingFrame, image=self.Green_Check_PhotoImage, width=50, height=50, bg = '#808080')
                GreenCheck_Label.image = self.Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + original_offset, column=1)

            else:
                # Create a photoimage object of the QR Code
                RedX_Label = tk.Label(self.viewingFrame, image=self.Red_X_PhotoImage, width=50, height=50, bg = '#808080')
                RedX_Label.image = self.Red_X_PhotoImage

                RedX_Label.grid(row=index + original_offset, column=1)



        self.grid_propagate(0)

    #################################################


    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll( -1, "units" )
        elif event.num == 5:
            self.mycanvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")




    #################################################

    def report_bug(self, _parent):
        _parent.report_bug(self)

    def btn_test_action(self, _parent, test_idx):
        print("\nSideBarScene.btn_test_action.test_idx: ", test_idx)
        _parent.set_frame_test(test_idx)

    def btn_summary_action(self, _parent):
        _parent.set_frame_test_summary()

    #################################################

    def disable_all_btns(self):
        self.btn_login.config(state = 'disabled')
        self.btn_scan.config(state = 'disabled')
        for btn in self.test_btns:
            btn.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_but_log_scan(self):
        for btn in self.test_btns:
            btn.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_btns_but_scan(self):
        self.btn_login.config(state = 'disabled')
        for btn in self.test_btns:
            btn.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_btns_but_login(self):
        self.btn_login.config(state = 'normal')
        self.btn_scan.config(state = 'disabled')
        for btn in self.test_btns:
            btn.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_log_scan(self):
        self.btn_login.config(state = 'disabled')
        self.btn_scan.config(state = 'disabled')

    #################################################
        
    def disable_login_button(self):
        self.btn_login.config(state = 'disabled')

    #################################################

    def disable_scan_button(self):
        self.btn_scan.config(state = 'disabled')
    
    #################################################


#################################################################################
