#################################################################################

# Importing all neccessary modules
from pickle import NONE
import tkinter as tk
print(tk.TkVersion)
#from turtle import bgcolor
import multiprocessing as mp
import logging
#from pyparsing import trace_parse_action

# Importing all the neccessary files and classes from them
import PythonFiles
from PythonFiles.GUIConfig import GUIConfig
from PythonFiles.Scenes.SidebarScene import SidebarScene
from PythonFiles.Scenes.LoginScene import LoginScene
from PythonFiles.Scenes.ScanScene import ScanScene
from PythonFiles.TestFailedPopup import TestFailedPopup
from PythonFiles.Scenes.TestSummaryScene import TestSummaryScene
from PythonFiles.Scenes.TestScene import *
from PythonFiles.Scenes.TestInProgressScene import TestInProgressScene
from PythonFiles.Data.DataHolder import DataHolder
from PythonFiles.Scenes.SplashScene import SplashScene
from PythonFiles.Scenes.TestInProgressScene import *
from PythonFiles.Scenes.Inspection1 import Inspection1
from PythonFiles.Scenes.AddUserScene import AddUserScene

#################################################################################



FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/shared/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'w', format=FORMAT, level=logging.DEBUG)
    

# Create a class for creating the basic GUI Window to be called by the main function to
# instantiate the actual object
class GUIWindow():

    #################################################

    def __init__(self, conn, queue, board_cfg):
        self.conn = conn
        self.queue = queue
        self.retry_attempt = False
        self.completed_window_alive = False
        self.current_test_index = 0
        self.gui_cfg = GUIConfig(board_cfg)
                             
        # Create the window named "self.master_window"
        # global makes self.master_window global and therefore accessible outside the function
        self.master_window = tk.Tk()
        self.master_window.title("HGCAL Test Window")
        # Creates the size of the window and disables resizing
        self.master_window.geometry("1063x500+25+100")
        self.master_window.resizable(0,0)

        # Removes the tkinter logo from the window
        # self.master_window.wm_attributes('-toolwindow', 'True')

        # Creates and packs a frame that exists on top of the master_frame
        self.master_frame = tk.Frame(self.master_window, width=850, height= 500)
        self.master_frame.grid(column = 1, row = 0, columnspan = 4)

        # Creates a frame to house the sidebar on self.master_window
        sidebar_frame = tk.Frame(self.master_window, width = 213, height = 500)
        sidebar_frame.grid(column = 0 , row = 0)

        # Creates the "Storage System" for the data during testing
        self.data_holder = DataHolder(self.gui_cfg)

        # Creates all the widgets on the sidebar
        self.sidebar = SidebarScene(self, sidebar_frame, self.data_holder)
        self.sidebar.pack()

        #################################################
        #   Creates all the different frames in layers  #
        #################################################

        # At top so it can be referenced by other frames' code... Order of creation matters

        self.test_summary_frame = TestSummaryScene(self, self.master_frame, self.data_holder)
        self.test_summary_frame.grid(row=0, column=0)

        self.login_frame = LoginScene(self, self.master_frame, self.data_holder)
        self.login_frame.grid(row=0, column=0)
        
        self.visual_frame = Inspection1(self, self.master_frame, self.data_holder)
        self.visual_frame.grid(row=0, column=0)
 
        self.scan_frame = ScanScene(self, self.master_frame, self.data_holder)
        self.scan_frame.grid(row=0, column=0)

        # Generalize test frames to use testing config
        # Grab list of tests from config file and create one scene for each test
        # Tests are indexed starting at 1 and using the order of the list in the config
        
        self.test_frames = []
        test_list = self.gui_cfg.getTests()
        
        for test_idx,test in enumerate(test_list):

            self.test_frames.append(TestScene(self, self.master_frame, self.data_holder, test["name"], queue, test_idx))
            self.test_frames[test_idx].grid(row=0, column=0)

        #self.test1_frame= Test1Scene(self, self.master_frame, self.data_holder, 
        #                    "General Resistance Test",
        #                    queue
        #                    )
        #self.test1_frame.grid(row=0, column=0)

        #self.test2_frame= Test2Scene(self, self.master_frame, self.data_holder,
        #                    "ID Resistor Test", 
        #                    queue
        #                    )
        #self.test2_frame.grid(row=0, column=0)
        #
        #self.test3_frame= Test3Scene(self, self.master_frame, self.data_holder, 
        #                    "I2C Comm. Test", 
        #                    queue
        #                    )
        #self.test3_frame.grid(row=0, column=0)

        #self.test4_frame= Test4Scene(self, self.master_frame, self.data_holder, 
        #                    "Bit Rate Test", 
        #                    queue
        #                    )
        #self.test4_frame.grid(row=0, column=0)

        self.test_in_progress_frame = TestInProgressScene(self, self.master_frame, self.data_holder, queue, conn)
        self.test_in_progress_frame.grid(row=0, column=0)

        
        self.add_user_frame = AddUserScene(self, self.master_frame, self.data_holder)
        self.add_user_frame.grid(row=0, column=0)

        # Near bottom so it can reference other frames with its code
        self.splash_frame = SplashScene(self, self.master_frame)
        self.splash_frame.grid(row=0, column=0)

        #################################################
        #              End Frame Creation               #
        #################################################
        
        logging.info("GUIWindow: All frames have been created.")


        # Tells the master window that its exit window button is being given a new function
        self.master_window.protocol('WM_DELETE_WINDOW', self.exit_function)
        
        # Sets the current frame to the splash frame
        self.set_frame_splash_frame()
        self.master_frame.update() 
        self.master_frame.after(50, self.set_frame_login_frame)

        self.master_window.mainloop()
        

    #################################################

    def set_frame_test_choice_frame(self):
        
        

        logging.debug("GUIWindow: The frame has been set to test_choice_frame.")

    #################################################

    def set_frame_add_user_frame(self):
        self.add_user_frame.update_frame(self)
        self.set_frame(self.add_user_frame)
        
        logging.debug("GUIWindow: The frame has been set to add_user_frame.")

    #################################################

    def set_frame_login_frame(self):  

        self.login_frame.update_frame(self)
        self.set_frame(self.login_frame)        

        logging.debug("GUIWindow: The frame has been set to login_frame.")
    #################################################

    def set_frame_scan_frame(self):

        self.scan_frame.is_current_scene = True
        self.set_frame(self.scan_frame)
        self.scan_frame.scan_QR_code(self.master_window)
        
        logging.debug("GUIWindow: The frame has been set to scan_frame.")

    #################################################

    def set_frame_splash_frame(self):

        self.set_frame(self.splash_frame)

        # Disables all buttons when the splash frame is the only frame
        self.sidebar.disable_all_btns()

        logging.debug("GUIWindow: The frame has been set to splash_frame.")

    #################################################

    def set_frame_visual_frame(self):
        self.visual_frame.update_frame(self)
        self.set_frame(self.visual_frame)

        logging.debug("GUIWindow: The frame has been set to visual_frame.")


    #################################################

    def scan_frame_progress(self):
        if self.data_holder.data_dict['is_new_board'] == True:
            self.set_frame_visual_frame()
        elif self.data_holder.data_dict['is_new_board'] == False:
            self.go_to_next_test()


    #################################################

    # For example, when we set the frame to test2_frame, we want to send the results
    # of test1 because it just completed.



    def set_frame_test_summary(self):
        self.test_summary_frame.update_frame()
        self.check_if_test_passed()
        self.set_frame(self.test_summary_frame)
        

        logging.debug("GUIWindow: The frame has been set to test_summary_frame.")

    #################################################

    def set_frame_test(self, test_idx):

        self.data_holder.setTestIdx(test_idx)

        selected_test_frame = self.test_frames[test_idx]
        print("Setting frame to test {}".format(test_idx))
        selected_test_frame.update_frame(self)
        print("Frame updated!")
        
        self.set_frame(selected_test_frame)
        print("Frame set!")

        logging.debug("GUIWindow: The frame has been set to test {}.".format(test_idx))

    #################################################

    def set_frame_test1(self):
        self.test1_frame.update_frame(self)
        self.set_frame(self.test1_frame)

        logging.debug("GUIWindow: The frame has been set to test1_frame.")
    #################################################

    def set_frame_test2(self):
        self.test2_frame.update_frame(self)
        self.set_frame(self.test2_frame)


        logging.debug("GUIWindow: The frame has been set to test2_frame.")
    #################################################

    def set_frame_test3(self):
        self.test3_frame.update_frame(self)
        self.set_frame(self.test3_frame)
        

        logging.debug("GUIWindow: The frame has been set to test3_frame.")
    #################################################

    def set_frame_test4(self):
        self.test4_frame.update_frame(self)
        self.set_frame(self.test4_frame)


        logging.debug("GUIWindow: The frame has been set to test4_frame.")
    #################################################

    def set_frame_test_in_progress(self, queue):
        self.set_frame(self.test_in_progress_frame)
        self.sidebar.disable_all_btns()
        self.test_in_progress_frame.begin_update(self.master_window, queue)
        self.go_to_next_test()   

        logging.debug("GUIWindow: The frame has been set to test_in_progress_frame.")
    #################################################

    def check_if_test_passed(self):
        logging.debug("GUIWindow: The method check_if_test_passed(self) has been called. This method is empty.")
    #################################################

    def go_to_next_test(self):
        
        # Array of potentially uncompleted tests
        test_completed_list = self.data_holder.data_lists['test_completion']
        

        test_incomplete = False
        

        logging.info("GUIWindow: Testing which tests have been completed.")
        # Checks tells the function which frame to set based on what frame is currently up
        for index, test in enumerate(test_completed_list):            

            if test == True and index >=  self.current_test_index:
                print("Test", index + 1, "== True")
                if self.completed_window_alive == False:
                    self.completed_window_popup()
                else:
                    pass
            elif test == True:
                pass
            else:
                test_incomplete = True
                print(self.current_test_index)
                self.set_frame_test(self.current_test_index)
                self.current_test_index += 1
                break
                #if (index ==0):
                #    self.set_frame_test()
                #    self.current_test_index = 1
                #elif (index == 1):
                #    self.set_frame_test2()
                #    self.current_test_index = 2
                #elif (index == 2):
                #    self.set_frame_test3()
                #    self.current_test_index = 3
                #elif (index == 3):
                #    self.set_frame_test4()
                #    self.current_test_index = 4
                #break
        


        # Tests if all the tests have been completed
        # if true, brings user to Test Summary Frame rather than the next test
        if (not test_incomplete):
            self.set_frame_test_summary()

    def reset_board(self):
        self.current_test_index = 0
        self.set_frame_scan_frame()

    #################################################

    # Called to change the frame to the argument _frame
    def set_frame(self, _frame):
        
        # Updates the sidebar every time the frame is set
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
        
        logging.debug("GUIWindow: Sidebar buttons have been updated.")

        # Brings up the test_failed popup if the test is false, continues on if not
        # Also tests the current test index so that in the event you are retrying a test it will not prompt 
        # the user about the previous test failing
        #if _frame == self.test2_frame and self.current_test_index == 1:
        #   if self.data_holder.data_dict['test1_pass'] == False:
        #        TestFailedPopup(self, self.test1_frame, self.data_holder)
        #if _frame == self.test3_frame and self.current_test_index == 2:
        #    if self.data_holder.data_dict['test2_pass'] == False:
        #        TestFailedPopup(self, self.test2_frame, self.data_holder)
        #if _frame == self.test4_frame and self.current_test_index == 3:
        #    if self.data_holder.data_dict['test3_pass'] == False:
        #        TestFailedPopup(self, self.test3_frame, self.data_holder)
        #if _frame == self.test_summary_frame and self.current_test_index == 4:
        #    if self.data_holder.data_dict['test4_pass'] == False:
        #        TestFailedPopup(self, self.test4_frame, self.data_holder)
        # Raises the passed in frame to be the current frame
        _frame.tkraise()

        logging.info("GUIWindow: The frame has been raised.")

    #################################################


    def unable_to_exit(self):
        
        logging.debug("GUIWindow: The user tried to exit during a test in progress.")

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
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
            height = 2,
            text = "OK",
            font = ('Arial', 12),
            relief = tk.RAISED,
            command = lambda: self.destroy_popup()
        )
        btn_ok.grid(column = 0, row = 1, columnspan=2)

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
    # Called when the no button is pressed to destroy popup and return you to the main window
    def destroy_popup(self):
        try:
            self.popup.destroy()
            self.completed_window_alive = False
            logging.debug("GUIWindow: The popup has been destroyed.")
        except:
            logging.error("GUIWindow: The popup has not been destroyed.")
    # New function for clicking on the exit button
    def exit_function(self):

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
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
            text = "Are you sure you would like to exit?",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0, columnspan = 2, pady = 25)

        # Creates yes and no buttons for exiting
        btn_yes = tk.Button(
            frm_popup,     
            width = 12,
            height = 2,
            text = "Yes", 
            relief = tk.RAISED,
            font = ('Arial', 12), 
            command = lambda: self.destroy_function()
            )
        btn_yes.grid(column = 0, row = 1)

        btn_no = tk.Button(
            frm_popup,
            width = 12,
            height = 2,
            text = "No",
            relief = tk.RAISED,
            font = ('Arial', 12),
            command = lambda: self.destroy_popup()
        )
        btn_no.grid(column = 1, row = 1)
        


    #################################################


    # Called when the yes button is pressed to destroy both windows
    def destroy_function(self):
        try:
            logging.info("GUIWindow: Exiting the GUI.")

            self.master_window.update()
            self.popup.update()

            if self.scan_frame.is_current_scene == True:
                self.test_in_progress_frame.close_prgbar()
                self.scan_frame.kill_processes()

            # Destroys the popup and master window
            self.popup.destroy()
            self.popup.quit()

            self.master_window.destroy()
            self.master_window.quit()

            logging.info("GUIWindow: The application has exited successfully.")
        except Exception as e:
            print(e)
            logging.debug("GUIWindow: " + repr(e))
            logging.error("GUIWindow: The application has failed to close.")
            if self.retry_attempt == False:    
                logging.info("GUIWindow: Retrying...")
                #self.destroy_function()
                self.retry_attempt = True


    #################################################

    
#################################################################################
