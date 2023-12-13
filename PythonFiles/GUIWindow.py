# Importing all neccessary modules

from pickle import NONE
import tkinter as tk
import multiprocessing as mp
import logging
import os
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
from PythonFiles.Scenes.AddUserScene import AddUserScene
from PythonFiles.Scenes.PostScanScene import PostScanScene
from PythonFiles.Scenes.GenericPhysicalScene import GenericPhysicalScene
from PythonFiles.update_config import update_config
import webbrowser

#################################################################################

logger = logging.getLogger(__name__)
# FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
# logging.basicConfig(filename=guiLogPath, filemode = 'a', format=FORMAT, level=logging.DEBUG)
logger.info("Test Logging from GUIWindow")



class GuiFrame:
    def __init__(self, frame, pre_enter=None, pre_exit=None):
        self.frame = frame
        self.pre_enter = pre_enter
        self.pre_exit = pre_exit
    


# Create a class for creating the basic GUI Window to be called by the main function to
# instantiate the actual object
class GUIWindow:
    def __init__(self, conn, conn_trigger, queue, board_cfg):
        self.conn = conn
        self.conn_trigger = conn_trigger
        self.queue = queue
        self.retry_attempt = False
        self.completed_window_alive = False
        self.current_test_index = 0
        self.gui_cfg = GUIConfig(board_cfg)
        self.data_holder = DataHolder(self.gui_cfg)


        self.test_frames = {}

        # Create the window named "self.master_window"
        # global makes self.master_window global and therefore accessible outside the function
        self.master_window = tk.Tk()
        self.master_window.title("HGCAL Test Window")
        # Creates the size of the window and disables resizing
        self.master_window.geometry("1300x700+25+100")

        # Variables necessary for the help popup
        self.all_text = "No help available for this scene."
        self.label_text = tk.StringVar()

        # Running all tests in succession?
        self.run_all_tests_bool = False

        # Should be resizable with following code commented out
        # self.master_window.resizable(0,0)

        # Removes the tkinter logo from the window
        # self.master_window.wm_attributes('-toolwindow', 'True')

        # Creates and packs a frame that exists on top of the master_frame
        self.master_frame = tk.Frame(self.master_window, width=870, height=650)
        self.master_frame.grid(column=1, row=0, columnspan=4)

        # Creates a frame to house the sidebar on self.master_window
        sidebar_frame = tk.Frame(self.master_window, width=213, height=650)
        sidebar_frame.grid(column=0, row=0)

        # Creates all the widgets on the sidebar
        self.sidebar = SidebarScene(self, sidebar_frame, self.data_holder)
        self.sidebar.pack()

        #################################################
        #   Creates all the different frames in layers  #
        #################################################

        # At top so it can be referenced by other frames' code... Order of creation matters

        self.test_summary_frame = TestSummaryScene(
            self, self.master_frame, self.data_holder
        )
        self.test_summary_frame.grid(row=0, column=0)

        self.login_frame = LoginScene(self, self.master_frame, self.data_holder)
        self.login_frame.grid(row=0, column=0)

        self.post_scan_frame = PostScanScene(self, self.master_frame, self.data_holder)
        self.post_scan_frame.grid(row=0, column=0)

        self.scan_frame = ScanScene(self, self.master_frame, self.data_holder)
        self.scan_frame.grid(row=0, column=0)

        self.create_test_frames(queue)

        self.test_in_progress_frame = TestInProgressScene(
            self, self.master_frame, self.data_holder, queue, conn
        )
        self.test_in_progress_frame.grid(row=0, column=0)

        self.add_user_frame = AddUserScene(self, self.master_frame, self.data_holder)
        self.add_user_frame.grid(row=0, column=0)

        # Near bottom so it can reference other frames with its code
        self.splash_frame = SplashScene(self, self.master_frame)
        self.splash_frame.grid(row=0, column=0)

        #################################################
        #              End Frame Creation               #
        #################################################

        logging.info("All frames have been created.")

        # Tells the master window that its exit window button is being given a new function
        self.master_window.protocol("WM_DELETE_WINDOW", self.exit_function)

        # Sets the current frame to the splash frame
        self.set_frame_splash_frame()
        self.master_frame.update()
        self.master_frame.after(100, self.set_frame_login_frame)

        self.master_window.mainloop()

    #################################################

    def addScene(scene_class, scene_id, pre_enter, pre_exit, *args,**kwargs):
        scene = scene_class(*args, **kwargs)
        self.test_frames[scene_id] = GuiFrame(scene)

    def testFrameFactory(self, test_type, test, queue):
        if test_type == "physical":
            ret = GenericPhysicalScene(self, self.master_frame, self.data_holder, test["id"], test["test_data"])
        elif test_type:
            ret = TestScene(
                self,
                self.master_frame,
                self.data_holder,
                test["id"],
                test["test_data"],
                queue,
                self.conn_trigger,
            )
        ret.grid(row=0, column=0)
        return ret

    def create_test_frames(self, queue):
        test_list = self.data_holder.getTests()
        offset = 0
        for test in test_list:
            self.test_frames[test["id"]] = self.testFrameFactory(test["type"], test, queue)

    #################################################

    def update_config(self):
        sn = self.data_holder.get_serial_ID()
        if not self.gui_cfg.getSerialCheckSafe():
            return
        new_cfg = update_config(sn)
        self.gui_cfg = new_cfg

    #################################################

    def run_all_tests(self, test_idx):
        self.running_all_idx = test_idx
        self.run_all_tests_bool = True

        try:
            test_client = REQClient(
                self.gui_cfg,
                "test{}".format(self.running_all_idx),
                self.data_holder.data_dict["current_serial_ID"],
                self.data_holder.data_dict["user_ID"],
                self.conn_trigger,
            )
            # test_client = REQClient('test{}'.format(self.running_all_idx), self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
            self.set_frame_test_in_progress(self.queue)
        except Exception as e:
            messagebox.showerror("Exception", e)

        logger.info("Confirm button sending test{}".format(self.running_all_idx))

    #################################################

    def set_frame_add_user_frame(self):
        self.add_user_frame.update_frame(self)
        self.set_frame(self.add_user_frame)

        logging.debug("GUIWindow: The frame has been set to add_user_frame.")

    #################################################

    def set_frame_login_frame(self):
        self.sidebar.update_sidebar(self)
        self.login_frame.update_frame(self)
        self.set_frame(self.login_frame)

        logging.debug("GUIWindow: The frame has been set to login_frame.")

    #################################################

    def set_frame_scan_frame(self):
        self.scan_frame.is_current_scene = True
        self.set_frame(self.scan_frame)
        self.scan_frame.scan_QR_code(self.master_window)

        logging.debug("The frame has been set to scan_frame.")

    #################################################

    def set_frame_splash_frame(self):
        self.set_frame(self.splash_frame)

        # Disables all buttons when the splash frame is the only frame
        self.sidebar.disable_all_btns()

        logging.debug("GUIWindow: The frame has been set to splash_frame.")

    #################################################

    def set_frame_postscan(self):
        self.post_scan_frame.update_frame()
        self.set_frame(self.post_scan_frame)

    #################################################

    # Used to be the visual inspection method

    #################################################

    def scan_frame_progress(self):
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

    def set_frame_test(self, test_id):
        selected_test_frame = self.test_frames[test_id]
        logger.info("Setting frame to test {}".format(test_id))
        self.set_frame(selected_test_frame)
        logging.debug("The frame has been set to test {}.".format(test_id))

    #################################################

    def set_frame_test_in_progress(self, queue):
        self.set_frame(self.test_in_progress_frame)

        logging.debug("GUIWindow: The frame has been set to test_in_progress_frame.")
        # self.sidebar.disable_all_btns()
        passed = self.test_in_progress_frame.begin_update(
            self.master_window, queue, self
        )
        if passed:
            self.go_to_next_test()
        else:
            return

    #################################################

    def check_if_test_passed(self):
        logging.debug(
            "GUIWindow: The method check_if_test_passed(self) has been called. This method is empty."
        )

    #################################################

    def return_to_current_test(self):
        self.current_test_index -= 1
        self.set_frame_test(self.current_test_index)

        self.data_holder.setTestIdx(self.current_test_index)

    def go_to_next_test(self):
        self.sidebar.update_sidebar(self)
        total_num_tests = self.data_holder.total_tests
        current_test_idx = self.data_holder.getActiveTest()["idx"]

        if not self.run_all_tests_bool:
            if current_test_idx < total_num_tests:
                next_test = self.data_holder.getByIndex(current_test_idx + 1)
                logger.info(f"Next test is {next_test}")
                self.data_holder.current_active_test = next_test["id"]
                self.set_frame_test(next_test["id"])
            else:
                self.set_frame_test_summary()

        else:
            self.running_all_idx += 1

            if self.running_all_idx < total_num_tests:
                self.data_holder.setTestIdx(self.current_test_index)
                self.current_test_index += 1

                try:
                    gui_cfg = self.data_holder.getGUIcfg()
                    test_client = REQClient(
                        gui_cfg,
                        "test{}".format(self.running_all_idx),
                        self.data_holder.data_dict["current_serial_ID"],
                        self.data_holder.data_dict["user_ID"],
                        conn_trigger,
                    )
                    self.set_frame_test_in_progress(self.queue)
                except Exception as e:
                    messagebox.showerror("Exception", e)

                logger.info(
                    "Confirm button sending test{}".format(self.running_all_idx)
                )

            else:
                self.run_all_tests_bool = False
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
            self.master_window.protocol("WM_DELETE_WINDOW", self.unable_to_exit)
        else:
            # Tells the master window that its exit window button is being given a new function
            self.master_window.protocol("WM_DELETE_WINDOW", self.exit_function)

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
        if _frame is not self.login_frame:
            self.sidebar.disable_login_button()

        # Hides the submit button on scan frame until an entry is given to the computer
        if _frame is not self.scan_frame:
            self.scan_frame.is_current_scene = False
            self.scan_frame.hide_submit_button()

            # Disables the sidebar scan button when the scan frame is not the current frame
            self.sidebar.disable_scan_button()

        #############################################################################
        #                        End Button Visibility Code                         #
        #############################################################################

        logging.debug("GUIWindow: Sidebar buttons have been updated.")

        # Raises the passed in frame to be the current frame
        _frame.tkraise()

        logging.info("GUIWindow: The frame has been raised.")

        self.set_help_text(_frame)

        self.master_frame.update()
        self.master_window.update()

    #################################################

    def critical_failure_popup(self):
        logging.debug("GUIWindow: Critical test failed. Cannot proceed with testing")

        self.popup = tk.Toplevel()
        self.popup.title("Critical Failure")
        self.popup.geometry("300x150+500+300")
        self.popup.grab_set()

        frm_popup = tk.Frame(self.popup)
        frm_popup.pack()

        lbl_popup = tk.Label(
            frm_popup,
            text=" This board has failed to pass\n a physical test. Cannot proceed.",
            font=("Arial", 13),
        )
        lbl_popup.grid(column=0, row=0, columnspan=2, pady=25)

        def action():
            self.destroy_popup()
            self.reset_board()

        btn_ok = tk.Button(
            frm_popup,
            width=12,
            height=2,
            text="Exit",
            font=("Arial", 12),
            relief=tk.RAISED,
            command=lambda: action(),
        )
        btn_ok.grid(column=0, row=1, columnspan=2)

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
            text=" You cannot exit the program \n during a test! ",
            font=("Arial", 13),
        )
        lbl_popup.grid(column=0, row=0, columnspan=2, pady=25)

        btn_ok = tk.Button(
            frm_popup,
            width=12,
            height=2,
            text="OK",
            font=("Arial", 12),
            relief=tk.RAISED,
            command=lambda: self.destroy_popup(),
        )
        btn_ok.grid(column=0, row=1, columnspan=2)

    #################################################

    # Creates the popup window to show the text for current scene
    def help_popup(self, current_window):
        logging.debug("GUIWindow: The user has requested a help window")
        logging.debug("Opening a help menu for {}".format(type(current_window)))

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
        # popup.wm_attributes('-toolwindow', 'True')
        self.popup.title("Help Window")
        self.popup.geometry("650x650+500+300")

        # "grab_set()" makes sure that you cannot do anything else while this window is open
        # self.popup.grab_set()

        self.mycanvas = tk.Canvas(
            self.popup, background="#808080", width=630, height=650
        )
        self.viewingFrame = tk.Frame(self.mycanvas, width=200, height=200)
        self.scroller = ttk.Scrollbar(
            self.popup, orient="vertical", command=self.mycanvas.yview
        )
        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        self.canvas_window = self.mycanvas.create_window(
            (4, 4), window=self.viewingFrame, anchor="nw", tags="self.viewingFrame"
        )

        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind("<Enter>", self.onEnter)
        self.viewingFrame.bind("<Leave>", self.onLeave)

        self.onFrameConfigure(None)

        self.set_help_text(current_window)

        # Creates frame in the new window
        # frm_popup = tk.Frame(self.mycanvas)
        # frm_popup.pack()

        # Creates label in the frame
        lbl_popup = tk.Label(
            self.viewingFrame, textvariable=self.label_text, font=("Arial", 11)
        )
        lbl_popup.grid(column=0, row=0, pady=5, padx=50)

        self.mycanvas.pack(side="right")
        self.scroller.pack(side="left", fill="both", expand=True)

        # btn_ok = tk.Button(
        #    frm_popup,
        #    width = 8,
        #    height = 2,
        #    text = "OK",
        #    font = ('Arial', 8),
        #    relief = tk.RAISED,
        #    command = lambda: self.destroy_popup()
        # )
        # btn_ok.grid(column = 0, row = 0)

    #############################################

    def set_help_text(self, current_window):
        # Help from file
        file = open(
            "{}/HGCAL_Help/{}_help.txt".format(
                PythonFiles.__path__[0], type(current_window).__name__
            )
        )
        self.all_text = file.read()

        # print("\nall_text: ", self.all_text)

        self.label_text.set(self.all_text)

    #################################################

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.mycanvas.configure(
            scrollregion=self.mycanvas.bbox("all")
        )  # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        """Reset the canvas window to encompass inner frame when required"""
        canvas_width = event.width
        self.mycanvas.itemconfig(
            self, width=canvas_width
        )  # whenever the size of the canvas changes alter the window region respectively.

    #################################################
    #################################################

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.mycanvas.yview_scroll(1, "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")

    #################################################

    def report_bug(self, current_window):
        url = "https://github.com/UMN-CMS/HGCALTestGUI/issues"
        webbrowser.open(url, new=1)

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
            text="A test has been skipped because it\n has been previously passed.",
            font=("Arial", 13),
        )
        lbl_popup.grid(column=0, row=0, pady=25)

        # Creates yes and no buttons for exiting
        btn_okay = tk.Button(
            frm_popup,
            width=12,
            height=2,
            text="OK",
            relief=tk.RAISED,
            font=("Arial", 12),
            command=lambda: self.destroy_popup(),
        )
        btn_okay.grid(column=0, row=1)

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
            frm_popup, text="Are you sure you would like to exit?", font=("Arial", 13)
        )
        lbl_popup.grid(column=0, row=0, columnspan=2, pady=25)

        # Creates yes and no buttons for exiting
        btn_yes = tk.Button(
            frm_popup,
            width=12,
            height=2,
            text="Yes",
            relief=tk.RAISED,
            font=("Arial", 12),
            command=lambda: self.destroy_function(),
        )
        btn_yes.grid(column=0, row=1)

        btn_no = tk.Button(
            frm_popup,
            width=12,
            height=2,
            text="No",
            relief=tk.RAISED,
            font=("Arial", 12),
            command=lambda: self.destroy_popup(),
        )
        btn_no.grid(column=1, row=1)

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
            logger.info(e, exc_info=True)
        except Exception as e:
            logger.info(e, exc_info=True)
            logging.debug("GUIWindow: " + repr(e))
            logging.error("GUIWindow: The application has failed to close.")
            if self.retry_attempt == False:
                logging.info("GUIWindow: Retrying...")
                self.retry_attempt = True

    #################################################


#################################################################################
