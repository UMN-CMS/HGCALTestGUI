#################################################################################

# Importing all neccessary modules
from pickle import NONE
import tkinter as tk
#from turtle import bgcolor
import multiprocessing as mp
import logging
import os
#from pyparsing import trace_parse_action

# Importing all the neccessary files and classes from them
import PythonFiles
from PythonFiles.GUIConfig import GUIConfig
from PythonFiles.Scenes.SidebarScene import SidebarScene
from PythonFiles.Scenes.LoginScene import LoginScene
from PythonFiles.Scenes.ScanScene import ScanScene
from PythonFiles.Scenes.ScanManyScene import ScanManyScene
from PythonFiles.TestFailedPopup import TestFailedPopup
from PythonFiles.Scenes.TestSummaryScene import TestSummaryScene
from PythonFiles.Scenes.TestScene import *
from PythonFiles.Scenes.TestInProgressScene import TestInProgressScene
from PythonFiles.Data.DataHolder import DataHolder
from PythonFiles.Scenes.SplashScene import SplashScene
from PythonFiles.Scenes.TestInProgressScene import *
from PythonFiles.Scenes.AddUserScene import AddUserScene
from PythonFiles.Scenes.PostScanScene import PostScanScene
from PythonFiles.Scenes.AdminScene import AdminScene
from PythonFiles.Scenes.AdminScanScene import AdminScanScene
from PythonFiles.Scenes.AdminScanScene import interposer_Popup
from PythonFiles.Scenes.AdminScanScene import finished_Popup
from PythonFiles.Scenes.ComponentScanScene import TesterComponentScene
from PythonFiles.update_config import update_config
import webbrowser
import sys

from PythonFiles.Scenes.ThermalTestConfigScene import ThermalTestConfigScene
from PythonFiles.Scenes.ThermalTestSetupResultsScene import ThermalTestSetupResultsScene
from PythonFiles.Scenes.ThermalTestBeginScene import ThermalTestBeginScene
from PythonFiles.Scenes.ThermalTestInProgressScene import ThermalTestInProgressScene
from PythonFiles.Scenes.ThermalTestFinalResultsScene import ThermalTestFinalResultsScene


#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.GUIWindow')

# Create a class for creating the basic GUI Window to be called by the main function to
# instantiate the actual object
class GUIWindow():

    #################################################

    def __init__(self, conn, conn_trigger, queue, board_cfg, main_path):
        
        self.conn = conn
        self.conn_trigger = conn_trigger
        self.queue = queue
        self.retry_attempt = False
        self.completed_window_alive = False
        self.current_test_index = 0
        self.gui_cfg = GUIConfig(board_cfg)
        self.main_path = main_path

        # Create the window named "self.master_window"
        self.master_window = tk.Tk()
        self.master_window.title("HGCAL Test Window")

        self.master_window.report_callback_exception = self.log_callback_exception

        # Creates the size of the window
        width = self.master_window.winfo_screenwidth()
        height = self.master_window.winfo_screenheight()

        self.master_window.geometry("{}x{}".format(width, height))
        self.master_window.pack_propagate(1) 

        #resizing master_frame, keeping sidebar same width
        self.master_window.grid_columnconfigure(0, weight=0)  # Make the sidebar resizable
        self.master_window.grid_columnconfigure(1, weight=1)  # Make the master frame resizable 
        self.master_window.grid_rowconfigure(0, weight=1)

        # Variables necessary for the help popup
        self.all_text = "No help available for this scene."
        self.label_text = tk.StringVar()
        
        self.run_all_tests_bool = False
        
        # resizable with following code commented out
        #self.master_window.resizable(0,0)

        # Removes the tkinter logo from the window
        # self.master_window.wm_attributes('-toolwindow', 'True')


        # Creates and packs a frame that exists on top of the master_frame
        self.master_frame = tk.Frame(self.master_window, width=1400-225, height=900)
        self.master_frame.grid(column = 1, row = 0, columnspan = 4, sticky="nsew")

        # Creates a frame to house the sidebar on self.master_window
        sidebar_frame = tk.Frame(self.master_window, width = 225, height=900)
        sidebar_frame.grid(column = 0 , row = 0, sticky="nsw")


        # Creates the "Storage System" for the data during testing
        self.data_holder = DataHolder(self.gui_cfg)
        self.data_holder.data_dict['queue'] = queue

        # Creates all the widgets on the sidebar
        self.sidebar = SidebarScene(self, sidebar_frame, self.data_holder)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        #################################################
        #   Creates all the different frames in layers  #
        #################################################

        # At top so it can be referenced by other frames' code... Order of creation matters

        self.test_summary_frame = TestSummaryScene(self, self.master_frame, self.data_holder)
        self.test_summary_frame.grid(row=0, column=0, sticky='nsew')

        self.login_frame = LoginScene(self, self.master_frame, self.data_holder)
        self.login_frame.grid(row=0, column=0, sticky = 'nsew')

        self.post_scan_frame = PostScanScene(self, self.master_frame, self.data_holder)
        self.post_scan_frame.grid(row=0, column=0, sticky = 'nsew')

        self.scan_frame = ScanScene(self, self.master_frame, self.data_holder)        
        self.scan_frame.grid(row=0, column=0, sticky = 'nsew')

        self.scan_many_frame = ScanManyScene(self, self.master_frame, self.data_holder)        
        self.scan_many_frame.grid(row=0, column=0, sticky = 'nsew')

        self.test_in_progress_frame = TestInProgressScene(self, self.master_frame, self.data_holder, queue, conn)
        self.test_in_progress_frame.grid(row=0, column=0, sticky = 'nsew')

        self.admin_scan_frame = AdminScanScene(self, self.master_frame, self.data_holder)
        self.admin_scan_frame.grid(row=0, column=0, sticky = 'nsew')

        self.admin_frame = AdminScene(self, self.master_frame, self.data_holder)
        self.admin_frame.grid(row=0, column=0, sticky = 'nsew')

        self.tester_component_frame = TesterComponentScene(self, self.master_frame, self.data_holder)
        self.tester_component_frame.grid(row=0, column=0, sticky = 'nsew')

        self.add_user_frame = AddUserScene(self, self.master_frame, self.data_holder)
        self.add_user_frame.grid(row=0, column=0, sticky= 'nsew')

        self.splash_frame = SplashScene(self, self.master_frame)
        self.splash_frame.grid(row=0, column=0, sticky = 'nsew')

        if (self.data_holder.tester_type == 'Thermal'):
            self.thermal_in_progress_frame = ThermalTestInProgressScene(self, self.master_frame, self.data_holder, queue, self.conn_trigger)
            self.thermal_in_progress_frame.grid(row=0, column=0, sticky='nsew')

            self.thermal_begin_frame = ThermalTestBeginScene(self, self.master_frame, self.data_holder, queue, conn)
            self.thermal_begin_frame.grid(row=0, column=0, sticky='nsew')

            self.thermal_config_frame = ThermalTestConfigScene(self, self.master_frame, self.data_holder, queue, self.conn_trigger)
            self.thermal_config_frame.grid(row=0, column=0, sticky='nsew')

            self.thermal_setup_results_frame = ThermalTestSetupResultsScene(self, self.master_frame, self.data_holder, queue, conn)
            self.thermal_setup_results_frame.grid(row=0, column=0, sticky='nsew')
            
            self.thermal_final_results_frame = ThermalTestFinalResultsScene(self, self.master_frame, self.data_holder, queue, conn)
            self.thermal_final_results_frame.grid(row=0, column=0, sticky='nsew')
             

        #################################################
        #              End Frame Creation               #
        #################################################
        
        logger.info("All frames have been created.")

        # Tells the master window that its exit window button is being given a new function
        self.master_window.protocol('WM_DELETE_WINDOW', self.exit_function)
        
        # Sets the current frame to the splash frame
        self.set_frame_splash_frame()
        self.master_frame.update() 
        self.master_frame.after(100, self.set_frame_login_frame)
        
        self.master_window.mainloop()
       
    def log_callback_exception(self, exc_type, exc_value, exc_traceback):
        logger.error("Exception in Tkinter callback", exc_info=(exc_type, exc_value, exc_traceback))

    def create_style(self):

        self.s = tk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(self.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')

    #################################################

    def create_test_frames(self, queue):
        # Generalize test frames to use testing config
        # Grab list of tests from config file and create one scene for each test
        # Tests are indexed starting at 1 and using the order of the list in the config
        
        self.test_frames = []
        test_list = self.gui_cfg.getTests()
        physical_list = self.gui_cfg.getPhysicalTests()        

        offset = 0
        
        # For the digital tests
        for test_idx,test in enumerate(test_list):

            self.test_frames.append(TestScene(self, self.master_frame, self.data_holder, test["name"], test["desc_short"], test["desc_long"], queue, self.conn_trigger, test_idx))
            self.test_frames[test_idx + offset].grid(row=0, column=0, sticky='nsew')


    #################################################

    def update_config(self):
        #switch between Wagon and Engine config depending on the full id entered
        full = self.data_holder.get_full_ID()
        if not self.gui_cfg.getSerialCheckSafe():
            return
        new_cfg = update_config(full)
        self.gui_cfg = new_cfg

    #################################################


    def run_all_tests(self):

        logger.info("Run all tests method has been selected.")

        self.running_all_idx = 0
        self.current_test_index = 0
        self.data_holder.setTestIdx(self.current_test_index)
        self.run_all_tests_bool = True
        cur_name = self.gui_cfg.getTests()[self.current_test_index]['name']

        test_client = REQClient(self.gui_cfg, cur_name.strip().replace(" ", ""), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'], self.conn_trigger)
        #test_client = REQClient(self.gui_cfg, 'test{}'.format(self.running_all_idx), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'], self.conn_trigger)
        #test_client = REQClient('test{}'.format(self.running_all_idx), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'])
        self.set_frame_test_in_progress(self.queue)


    #################################################

    def set_frame_add_user_frame(self):

        logger.info("Setting frame to add_user_frame")

        self.add_user_frame.update_frame(self)
        self.set_frame(self.add_user_frame)

    #################################################

    def set_frame_admin_frame(self):
        logger.info("Setting frame to admin_frame")

        self.admin_frame.update_frame(self)
        self.set_frame(self.admin_frame)

    def set_frame_admin_scan(self):
        logger.info("Setting frame to admin_scan_frame")

        self.component_index = 0

        self.admin_scan_frame.is_current_scene = True
        self.admin_scan_frame.update_frame(self, self.component_index)
        self.set_frame(self.admin_scan_frame)
        self.admin_scan_frame.scan_QR_code(self.master_window)

        logger.debug('Component Index: ' + str(self.component_index))

    def next_frame_admin_scan(self):
        self.component_index += 1
        logger.debug('Component Index: ' + str(self.component_index))

        if self.data_holder.tester_type == 'Wagon':
            if self.component_index < 3+int(self.data_holder.wagon_tester_info['num_wagon_wheels']):
                self.admin_scan_frame.update_frame(self, self.component_index)
                if list(self.data_holder.wagon_tester_info)[self.component_index] == 'Interposer':
                    interposer_popup = interposer_Popup(self, self.data_holder)

                self.admin_scan_frame.scan_QR_code(self.master_window)
            else:
                finished_Popup(self, self.data_holder)
                logger.debug(self.data_holder.wagon_tester_info)

                self.data_holder.upload_test_stand_info()
                self.set_frame_login_frame()

        if self.data_holder.tester_type == 'Engine':
            if self.component_index == 5:
                if self.data_holder.engine_tester_info["Major Type"] == "LD":
                    self.component_index += 1

            if self.component_index == 6:
                if self.data_holder.engine_tester_info["Major Type"] == "HD":
                    self.component_index = 10


            if self.component_index < 8:
                self.admin_scan_frame.update_frame(self, self.component_index)
                self.admin_scan_frame.scan_QR_code(self.master_window)
            else:
                finished_Popup(self, self.data_holder)
                logger.debug(self.data_holder.engine_tester_info)

                self.data_holder.upload_test_stand_info()
                self.set_frame_login_frame()

    #################################################


    def set_frame_tester_component_frame(self):

        logger.info("Setting frame to tester_component_frame")

        self.tester_component_frame.is_current_scene = True
        self.set_frame(self.tester_component_frame)
        self.tester_component_frame.scan_QR_code(self.master_window)

    #################################################

    def set_frame_login_frame(self):  

        logger.info("The frame has been set to login_frame")

        self.sidebar.clean_up_btns()
        self.sidebar.update_sidebar(self)
        self.login_frame.update_frame(self)
        self.set_frame(self.login_frame)        

    #################################################

    def set_frame_scan_frame(self):
        if (self.data_holder.tester_type == 'Thermal'):
            logger.info("set_frame_scan_frame has been bypassed, setting Thermal Config Frame")
            self.set_frame_thermal_config()
        else:
            logger.info("Setting frame to scan_frame")
            
            self.scan_frame.is_current_scene = True
            self.set_frame(self.scan_frame)
            self.scan_frame.scan_QR_code(self.master_window)
            
    #################################################

    def set_frame_scan_many_frame(self):
        
        logger.info("Setting frame to scan_many_frame")

        self.scan_many_frame.is_current_scene = True
        self.set_frame(self.scan_many_frame)
        self.scan_many_frame.scan_QR_code(self.master_window)

    #################################################

    def set_frame_splash_frame(self):

        logger.info("Setting frame to splash_frame")

        self.set_frame(self.splash_frame)

        # Disables all buttons when the splash frame is the only frame
        self.sidebar.disable_all_btns()

    #################################################

    def set_frame_postscan(self):

        logger.info("Setting frame to post_scan_frame")

        self.post_scan_frame.update_frame()
        self.set_frame(self.post_scan_frame)

    #################################################

    # Used to be the visual inspection method

    #################################################

    def scan_frame_progress(self):
        self.go_to_next_test()


    #################################################


    def set_frame_test_summary(self):
        
        logger.info("Setting frame to test_summary_frame")

        self.test_summary_frame.update_frame()
        self.set_frame(self.test_summary_frame)

    #################################################

    def set_frame_test(self, test_idx):

        logger.info("Setting frame to test {}".format(test_idx))

        self.current_test_index = test_idx
        self.data_holder.setTestIdx(test_idx)

        selected_test_frame = self.test_frames[test_idx]
        
        self.set_frame(selected_test_frame)

    #################################################  
    # Navigation for the Thermal Testing GUI

    def set_frame_thermal_begin(self):
        logger.info("Setting frame to thermal_begin_frame")
        self.set_frame(self.thermal_begin_frame)

    def set_frame_thermal_config(self):
        logger.info("Setting frame to thermal_config_frame")
        self.set_frame(self.thermal_config_frame)

    def set_frame_thermal_final_results(self):
        logger.info("Setting frame to thermal_final_results_frame.")
        self.set_frame(self.thermal_final_results_frame)
        # self.thermal_final_results_frame.send_REQ(self.master_window, self.queue, self)
        self.thermal_final_results_frame.send_REQ(self)

    def set_frame_thermal_test_in_progress(self):
        logger.info("Setting frame to thermal_test_in_progress_frame.")
        self.thermal_in_progress_frame.update_frame(self)
        # self.thermal_in_progress_frame.begin_update(self.master_window, self.queue, self)
        self.set_frame(self.thermal_in_progress_frame)

    def set_frame_thermal_setup_results(self):
        logger.info("Setting frame to thermal_setup_results_frame.")
        self.thermal_setup_results_frame.update_frame(self)
        self.set_frame(self.thermal_setup_results_frame)
        self.thermal_setup_results_frame.begin_update(self.master_window, self.queue, self)
        
    #################################################

    def set_frame_test_in_progress(self, queue):

        logger.info("Setting frame to test_in_progress_frame")

        self.test_in_progress_frame.remove_stop_txt()
        self.set_frame(self.test_in_progress_frame)
        
        self.sidebar.disable_all_btns()
        passed = self.test_in_progress_frame.begin_update(self.master_window, queue, self)
        self.go_to_next_test()   

    #################################################

    def return_to_current_test(self):
        self.current_test_index -= 1
        self.running_all_idx -= 1
        self.set_frame_test(self.current_test_index)

        self.data_holder.setTestIdx(self.current_test_index)

    def go_to_next_test(self):
            
        # Updates the sidebar every time the frame is set
        self.sidebar.clean_up_btns()
        self.sidebar.update_sidebar(self)

        total_num_tests = self.data_holder.total_test_num
        num_digital = self.data_holder.getNumTest()
        #num_physical = self.data_holder.getNumPhysicalTest()
        

        if not self.run_all_tests_bool:        

            if (self.current_test_index < total_num_tests):
                cur_name = self.gui_cfg.getTests()[self.current_test_index]['name']
                logger.debug('Current test is: %s' % cur_name)
                self.set_frame_test(self.current_test_index)
                self.current_test_index += 1
            else:
                self.set_frame_test_summary()
            
        else:
            self.running_all_idx += 1
        
            if (self.running_all_idx < total_num_tests):

                self.current_test_index += 1
                self.data_holder.setTestIdx(self.running_all_idx)
                
                gui_cfg = self.data_holder.getGUIcfg()

                cur_name = gui_cfg.getTests()[self.current_test_index]['name']
                logger.debug('Current test is: %s' % cur_name)

                test_client = REQClient(self.gui_cfg, cur_name.strip().replace(" ", ""), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'], self.conn_trigger)
                #test_client = REQClient(gui_cfg, 'test{}'.format(self.running_all_idx), self.data_holder.data_dict['current_full_ID'], self.data_holder.data_dict['user_ID'], self.conn_trigger)
                self.set_frame_test_in_progress(self.queue)
            

            else: 
                self.run_all_tests_bool = False
                self.set_frame_test_summary()


    def reset_board(self):
        self.current_test_index = 0
        self.set_frame_scan_frame()

    #################################################

    # Called to change the frame to the argument _frame
    def set_frame(self, _frame):

        #Binding return button to next frame
        try: 
            bind_func = _frame.get_submit_action()
            _frame.bind_all("<Return>", lambda event: bind_func(_frame.get_parent()))
        except: 
            logger.warning("No bind function for " + str(_frame))

        try:
            bind_func_2 = _frame.run_all_action
            _frame.bind_all("<Shift-Return>", lambda event: bind_func_2(_frame.get_parent()))
        except Exception as e:
            pass
 

        # Updates the sidebar every time the frame is set
        self.sidebar.clean_up_btns()
        self.sidebar.update_sidebar(self)

        # If frame is test_in_progress frame, disable the close program button
        # Tells the master window that its exit window button is being given a new function
        if _frame is self.test_in_progress_frame:
            self.master_window.protocol('WM_DELETE_WINDOW', self.unable_to_exit)
        else:
            # Tells the master window that its exit window button is being given a new function
            self.master_window.protocol('WM_DELETE_WINDOW', self.exit_function)
 
        #############################################################################
        #  The Following Code Determines What Buttons Are Visible On The Side Bar   #
        #############################################################################

        # Disables all but login button when on login_frame
        if _frame is self.login_frame:
            self.sidebar.disable_all_btns_but_login()

        # Disables all but scan button when on scan_frame
        if _frame is self.scan_frame:
            self.sidebar.disable_all_btns_but_scan()

        # Disables the sidebar login button when the login frame is not the current frame
        # or when scan_frame is not the current frame
        if (_frame is not self.login_frame):
            self.sidebar.disable_login_button()
            

        # Hides the submit button on scan frame until an entry is given to the computer
        if (_frame is not self.scan_frame):
            self.scan_frame.is_current_scene = False
            self.scan_frame.hide_submit_button()
            
            # Disables the sidebar scan button when the scan frame is not the current frame
            self.sidebar.disable_scan_button()

        #############################################################################
        #                        End Button Visibility Code                         #
        #############################################################################

        # Raises the passed in frame to be the current frame
        _frame.tkraise()

        self.set_help_text(_frame)

        self.master_frame.update()
        self.master_window.update()

    #################################################


    def unable_to_exit(self):
        
        logger.warning("The user tried to exit during a test in progress.")

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
        self.popup.create_style(self)

       # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Exit Window") 
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()
       

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup, 
            text = " You cannot exit the program \n during a test! ",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2, pady = 25)


        btn_ok = tk.Button(
            frm_popup,
            width = 12,
            text = "OK",
            font = ('Arial', 12),
            command = lambda: self.destroy_popup()
        )
        btn_ok.grid(column = 0, row = 1, columnspan=2)



    #################################################

    # Creates the popup window to show the text for current scene
    def help_popup(self, current_window):
        
        logger.info("The user requested a help window")
        logger.info("Opening help menu for {}".format(type(current_window)))

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
        # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Help Window") 
        self.popup.geometry("650x650+500+300")
        
        # "grab_set()" makes sure that you cannot do anything else while this window is open
        #self.popup.grab_set()
       
        self.mycanvas = tk.Canvas(self.popup, background="#808080", width=630, height =650)
        self.viewingFrame = tk.Frame(self.mycanvas, width = 200, height = 200)
        self.scroller = tk.Scrollbar(self.popup, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)



        self.canvas_window = self.mycanvas.create_window((4,4), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")


        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)
 
        
        self.set_help_text(current_window)
        
        # Creates frame in the new window
        #frm_popup = tk.Frame(self.mycanvas)
        #frm_popup.pack()

   
        # Creates label in the frame
        lbl_popup = tk.Label(
            self.viewingFrame, 
            textvariable = self.label_text,
            font = ('Arial', 11)
            )
        lbl_popup.grid(column = 0, row = 0, pady = 5, padx = 50)


        self.mycanvas.pack(side="right")
        self.scroller.pack(side="left", fill="both", expand=True)
      

        #btn_ok = tk.Button(
        #    frm_popup,
        #    width = 8,
        #    height = 2,
        #    text = "OK",
        #    font = ('Arial', 8),
        #    relief = tk.RAISED,
        #    command = lambda: self.destroy_popup()
        #)
        #btn_ok.grid(column = 0, row = 0)


    #############################################


    def set_help_text(self, current_window):


        # Help from file
        file = open("{}/HGCAL_Help/{}_help.txt".format(PythonFiles.__path__[0], type(current_window).__name__))
        self.all_text = file.read()

        #print("\nall_text: ", self.all_text)

        self.label_text.set(self.all_text)

    #################################################

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.mycanvas.configure(scrollregion=self.mycanvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.mycanvas.itemconfig(self, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.


    #################################################
    #################################################


    def onMouseWheel(self, event):             # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll( -1, "units" )
        elif event.num == 5:
            self.mycanvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                  # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):                  # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")




    #################################################

    def report_bug(self, current_window):
        url = 'https://github.com/UMN-CMS/HGCALTestGUI/issues'
        webbrowser.open(url, new = 1)

    #################################################
    
    # Called when a test is skipped because it has been previously passed
    def completed_window_popup(self):

        self.completed_window_alive = True
       
        # Creates a popup to inform user about the passing of a test
        self.popup = tk.Toplevel()
        # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Information Window") 
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()
       

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup, 
            text = "A test has been skipped because it\n has been previously passed.",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, pady = 25)

        # Creates yes and no buttons for exiting
        btn_okay = tk.Button(
            frm_popup,     
            width = 12,
            height = 2,
            text = "OK", 
            relief = tk.RAISED,
            font = ('Arial', 12), 
            command = lambda: self.destroy_popup()
            )
        btn_okay.grid(column = 0, row = 1)
    
    def test_error_popup(self, message):
        
        self.completed_window_alive = True
       
        # Creates a popup to inform user about the passing of a test
        self.popup = tk.Toplevel()
        # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Error Window") 
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()
       

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup, 
            text = message,
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, pady = 25)

        # Creates yes and no buttons for exiting
        btn_okay = tk.Button(
            frm_popup,     
            width = 12,
            height = 2,
            text = "OK", 
            relief = tk.RAISED,
            font = ('Arial', 12), 
            command = lambda: self.destroy_popup()
            )
        btn_okay.grid(column = 0, row = 1)
    


    # Called when the no button is pressed to destroy popup and return you to the main window
    def destroy_popup(self):
        try:
            self.popup.destroy()
            self.completed_window_alive = False
        except:
            logger.error("The popup was unable to be destroyed.")
    

    # New function for clicking on the exit button
    def exit_function(self):

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()

        # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Exit Window") 
        self.popup.geometry("300x200+500+300")
        self.popup.pack_propagate(1)
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()
 

        # Creates frame in the new window
        frm_popup = tk.Frame(self.popup, width = 300, height = 200)
        frm_popup.grid()
        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_columnconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)
        frm_popup.grid_rowconfigure(2, weight=1)

        # Creates label in the frame
        lbl_popup = tk.Label(
            frm_popup, 
            text = "Are you sure you would like to exit?",
            font = ('Arial', 14)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2, pady = 25)

        # Creates yes and no buttons for exiting
        btn_yes = tk.Button(
            frm_popup,     
            width = 12,
            text = "Yes", 
            command = lambda: self.destroy_function()
            )
        btn_yes.grid(column = 0, row = 1)

        btn_no = tk.Button(
            frm_popup,
            width = 12,
            text = "No",
            command = lambda: self.destroy_popup()
        )
        btn_no.grid(column = 1, row = 1)
        


    #################################################

    # Function for stopping tests gracefully
    def stop_tests(self):
        #self.sidebar.disable_all_btns()
        self.run_all_tests_bool = False

    # Called when the yes button is pressed to destroy both windows
    def destroy_function(self):
        try:
            logger.info("Exiting the GUI.")

            self.master_window.update()
            self.popup.update()

            #if self.scan_frame.is_current_scene == True:
                #self.test_in_progress_frame.close_prgbar()
            self.scan_frame.kill_processes()
            self.admin_scan_frame.kill_processes()

            # Destroys the popup and master window
            self.popup.destroy()
            self.popup.quit()

            self.master_window.destroy()
            self.master_window.quit()

            logger.info("The application has exited successfully.")
        except Exception as e:
            logger.exception(e)
            logger.error("The application has failed to close.")
            if self.retry_attempt == False:    
                logger.info("Retrying...")
                self.retry_attempt = True


    #################################################
    
#################################################################################
