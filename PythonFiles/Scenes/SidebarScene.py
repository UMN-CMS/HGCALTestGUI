#################################################################################

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Canvas
from tkinter import Scrollbar
from PIL import ImageTk as iTK
from PIL import Image
import logging
import PythonFiles
import os
import platform
import requests
import time



#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.SidebarScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

class SidebarScene(ttk.Frame):

    #################################################

    def __init__(self, parent, sidebar_frame, data_holder):
        super().__init__(sidebar_frame, width=225, height=850)


        self.mycanvas = tk.Canvas(self, width=225, height=850, bg="#33393b")
        self.viewingFrame = tk.Frame(self.mycanvas, background="#33393b", width=225, height=850)

        self.create_style(parent)

        self.Green_Check_Image = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
        self.Green_Check_Image = self.Green_Check_Image.resize((50,50), Image.LANCZOS)
        self.Green_Check_PhotoImage = iTK.PhotoImage(self.Green_Check_Image)
        self.Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        self.Red_X_Image = self.Red_X_Image.resize((50,50), Image.LANCZOS)
        self.Red_X_PhotoImage = iTK.PhotoImage(self.Red_X_Image)
        self.notrun_Image = Image.open("{}/Images/not_yet_run.png".format(PythonFiles.__path__[0]))
        self.notrun_Image = self.notrun_Image.resize((50,50), Image.LANCZOS)
        self.notrun_PhotoImage = iTK.PhotoImage(self.notrun_Image)
        

        ############        

        self.scroller = ttk.Scrollbar(self, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)
       
        sidebar_frame.grid_columnconfigure(0, weight=1)
        sidebar_frame.grid_rowconfigure(0, weight=1)

        #background="#808080"

        self.mycanvas.grid(row=0, column=0, sticky="ns") 
        self.scroller.grid(row=0, column=1, sticky="nsw")

        self.canvas_window = self.mycanvas.create_window((0, 0), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")
        self.viewingFrame.pack(fill='y', expand=True, side='left')
        

        """
        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)
        """

        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

        #self.onFrameConfigure(None)

        self.data_holder = data_holder

        self.update_sidebar(parent)

        '''Reset the scroll region to encompass the inner frame'''
        self.mycanvas.configure(scrollregion=self.mycanvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.
    """
    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.mycanvas.itemconfig(self, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.
    """
    
    
    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    #################################################

    def clean_up_btns(self):
        for btn in self.all_btns:
            btn.destroy()

    def update_sidebar(self, _parent):
       
        logger.info("SidebarScene: The sidebar has been updated.")

        # Variables for easy button editing
        btn_height = 3
        btn_width = 18
        btn_pady = 12
        btn_padx = 15

        self.btn_login = ttk.Button(
            self.viewingFrame,
            text = 'LOGIN PAGE',
            width = btn_width,
        )
        self.btn_login.grid(column = 0, row = 0, pady = btn_pady, padx = btn_padx)


    
        self.btn_scan = ttk.Button(
            self.viewingFrame,
            text = 'SCAN PAGE',
            width = btn_width,
        )
        self.btn_scan.grid(column = 0, row = 2, pady = btn_pady, padx = btn_padx)

        test_names = self.data_holder.getTestNames()
        physical_names = self.data_holder.getPhysicalNames()

        self.test_btns = []

        # Offset = number of buttons before the test buttons begin
        original_offset = 3
        
        # How much offset from the physical board tests


        for i in range(self.data_holder.getNumPhysicalTest()): 
            self.test_btns.append(ttk.Button(
                self.viewingFrame, 
                text = '{}'.format(physical_names[i]),
                width = btn_width,
                command = lambda i=i: self.btn_test_action(_parent, i)
                ))
            self.test_btns[i].grid(column = 0, row = 3 + i, pady = btn_pady, padx = btn_padx) #i + original_offset)


            if self.data_holder.data_dict['physical{}_pass'.format(i)] == True:
                self.test_btns[i].config(state = 'disabled')
            


        #
        ## For the digital buttons
        #
        digital_offset = 0

        for i in range(self.data_holder.getNumTest()):
            
            self.test_btns.append(ttk.Button(
                self.viewingFrame, 
                text = '{}'.format(test_names[i]),
                width = btn_width,
                command = lambda i=i: self.btn_test_action(_parent, i )
                ))
            self.test_btns[i].grid(column = 0, row = 3 + i, pady = btn_pady, padx = btn_pady) #original_offset + i)

            if self.data_holder.data_dict['test{}_pass'.format(i)] == True:
                self.test_btns[i].config(state = 'disabled')
            
            digital_offset = digital_offset + 1
       
        self.btn_summary = ttk.Button(
            self.viewingFrame, 
            #pady = btn_pady,
            text = 'TEST SUMMARY',
            #height = btn_height,
            width = btn_width,
            #font = btn_font,
            command = lambda: self.btn_summary_action(_parent)
            )
        self.btn_summary.grid(column = 0, row = 4 + self.data_holder.getNumTest(), pady = btn_pady)

        self.restart_server_btn = ttk.Button(
            self.viewingFrame, 
            #pady = btn_pady,
            text = 'Restart Server',
            #height = btn_height,
            width = btn_width,
            #font = ('Kozuka Gothic Pr6N L', 8),
            command = lambda: self.restart_server(_parent)
            )
        self.restart_server_btn.grid(column = 0, row = 5 + self.data_holder.getNumTest(), pady = btn_pady)
        
        self.reload_firmware_btn = ttk.Button(
            self.viewingFrame, 
            #pady = btn_pady,
            text = 'Reload Firmware',
            #height = btn_height,
            width = btn_width,
            #font = ('Kozuka Gothic Pr6N L', 8),
            command = lambda: self.reload_firmware(_parent)
            )
        self.reload_firmware_btn.grid(column = 0, row = 6 + self.data_holder.getNumTest(), pady = (btn_pady))
        
        self.reset_power_btn = ttk.Button(
            self.viewingFrame, 
            #pady = btn_pady,
            text = 'Reset Power',
            #height = btn_height,
            width = btn_width,
            #font = ('Kozuka Gothic Pr6N L', 8),
            command = lambda: self.reset_power(_parent)
            )
        self.reset_power_btn.grid(column = 0, row = 7 + self.data_holder.getNumTest(), pady = (btn_pady, 235))

        if (self.data_holder.tester_type == 'Thermal'):
            self.btn_scan.grid_forget()
            self.scroller.grid_forget()

        self.all_btns = [*self.test_btns, self.btn_summary, self.restart_server_btn, self.reload_firmware_btn, self.reset_power_btn]
        
        
        # List for creating check marks with for loop
        self.list_of_completion = self.data_holder.data_lists['test_completion']
        self.list_of_pass_fail = self.data_holder.data_lists['test_results']



        # For loop to create checkmarks based on pass/fail
        for index in range(len(self.list_of_pass_fail)):
            if self.list_of_completion[index] == True:
                if(self.list_of_pass_fail[index] == True):
                    # Create a photoimage object of the QR Code
                    GreenCheck_Label = tk.Label(self.viewingFrame, image=self.Green_Check_PhotoImage, width=50, height=50, bg = '#33393b')
                    GreenCheck_Label.image = self.Green_Check_PhotoImage
                    GreenCheck_Label.grid(row=index + original_offset , column=1, padx = btn_padx)

                else:
                    # Create a photoimage object of the QR Code
                    RedX_Label = tk.Label(self.viewingFrame, image=self.Red_X_PhotoImage, width=50, height=50, bg = '#33393b')
                    RedX_Label.image = self.Red_X_PhotoImage
                    RedX_Label.grid(row=index + original_offset , column=1, padx = btn_padx)
            else:
                notrun_Label = tk.Label(self.viewingFrame, image=self.notrun_PhotoImage, width=50, height=50, bg = '#33393b')
                notrun_Label.image = self.notrun_PhotoImage
                notrun_Label.grid(row=index + original_offset , column=1, padx = btn_padx)

        self.physical_pass_fail = self.data_holder.data_lists['physical_results']
        
        # For loop to create checkmarks based on pass/fail
        for index in range(len(self.physical_pass_fail)):
            if(self.physical_pass_fail[index] == True):
                # Create a photoimage object of the QR Code
                GreenCheck_Label = tk.Label(self.viewingFrame, image=self.Green_Check_PhotoImage, width=50, height=50, bg = '#33393b')
                GreenCheck_Label.image = self.Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + original_offset, column=1, padx = btn_padx)

            else:
                # Create a photoimage object of the QR Code
                RedX_Label = tk.Label(self.viewingFrame, image=self.Red_X_PhotoImage, width=50, height=50, bg = '#33393b')
                RedX_Label.image = self.Red_X_PhotoImage

                RedX_Label.grid(row=index + original_offset, column=1, padx = btn_padx)
 

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

    def restart_server(self, _parent):
        handler = _parent.gui_cfg.getTestHandler()
        r = requests.get('http://{}:8899/stop/server'.format(handler['remoteip']))
        print(r.text)
        time.sleep(1)
        r = requests.get('http://{}:8899/start/server'.format(handler['remoteip']))
        print(r.text)

    def reload_firmware(self, _parent):
        handler = _parent.gui_cfg.getTestHandler()
        r = requests.get('http://{}:8899/start/reloadfw'.format(handler['remoteip']))
        print(r.text)

    def reset_power(self, _parent):
        handler = _parent.gui_cfg.getTestHandler()
        r = requests.get('http://{}:8899/start/cycle_kconn_pwr'.format(handler['remoteip']))
        print(r.text)

    def btn_test_action(self, _parent, test_idx):
        print("\nSideBarScene.btn_test_action.test_idx: ", test_idx)
        _parent.set_frame_test(test_idx)



    def btn_summary_action(self, _parent):
        if (self.data_holder.tester_type != 'Thermal'):
            _parent.set_frame_test_summary()
        else:
            _parent.set_frame_thermal_final_results()
    #################################################

    def disable_all_btns(self):
        for btn in self.all_btns:
            btn.config(state = 'disabled')
        #self.btn_login.config(state = 'disabled')
        #self.btn_scan.config(state = 'disabled')
        #for btn in self.test_btns:
        #    btn.config(state = 'disabled')
        #self.btn_summary.config(state = 'disabled')

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
