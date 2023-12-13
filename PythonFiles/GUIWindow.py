# Importing all neccessary modules
from pickle import NONE
import tkinter as tk
import multiprocessing as mp
import logging
from PIL import ImageTk as iTK
from PIL import Image
import os
import PythonFiles
from .GUIConfig import GUIConfig
from .Scenes.SidebarScene import SidebarScene
from .Scenes.LoginScene import LoginScene
from .Scenes.ScanScene import ScanScene
from .TestFailedPopup import TestFailedPopup
from .Scenes.TestSummaryScene import TestSummaryScene
from .Scenes.TestScene import *
from .Scenes.TestInProgressScene import TestInProgressScene
from .Data.DataHolder import DataHolder
from .Scenes.SplashScene import SplashScene
from .Scenes.TestInProgressScene import *
from .Scenes.AddUserScene import AddUserScene
from .Scenes.PostScanScene import PostScanScene
from .Scenes.GenericPhysicalScene import GenericPhysicalScene
from .update_config import update_config
import webbrowser
import itertools as it


logger = logging.getLogger(__name__)


class TestSidebarAnnot:
    @classmethod
    def initImages(cls):
        Green_Check_Image = Image.open(
            "{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0])
        )
        Green_Check_Image = Green_Check_Image.resize((50, 50), Image.LANCZOS)
        cls.Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
        Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        Red_X_Image = Red_X_Image.resize((50, 50), Image.LANCZOS)
        cls.Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)

    def __init__(self, data_holder, test_id):
        self.data_holder = data_holder
        self.test_id = test_id

    def __call__(self, parent):
        test = self.data_holder.getTest(self.test_id)
        tname = test["test_data"]["name"]
        test_state = self.data_holder.getTestState(self.test_id)
        if test_state["passed"]:
            annot = tk.Label(
                parent,
                image=self.Green_Check_PhotoImage,
                width=50,
                height=50,
                bg="#808080",
            )
        elif test_state["completed"]:
            annot = tk.Label(
                parent,
                image=self.Red_X_PhotoImage,
                width=50,
                heighttest=50,
                bg="#808080",
            )
        else:
            annot = None
        return annot


class GuiScene:
    def __init__(
        self,
        frame,
        scene_id,
        scene_name=None,
        pre_enter=None,
        post_enter=None,
        pre_exit=None,
        post_exit=None,
        sidebar_idx=None,
        sidebar_group=None,
        sidebar_annotation=None,
    ):
        self.frame = frame
        self.scene_id = scene_id
        self.scene_name = scene_name or self.scene_id
        self.pre_enter = pre_enter if pre_enter is not None else (lambda *x: None)
        self.pre_exit = pre_exit if pre_exit is not None else (lambda *x: None)
        self.post_enter = post_enter if post_enter is not None else (lambda *x: None)
        self.post_exit = post_exit if post_exit is not None else (lambda *x: None)
        self.sidebar_annotation = sidebar_annotation
        self.sidebar_group = sidebar_group
        self.sidebar_idx = sidebar_idx

    def getSidebarIdx(self):
        if self.sidebar_idx is None:
            return None
        elif callable(self.sidebar_idx):
            return self.sidebar_idx()
        else:
            return self.sidebar_idx

    def __repr__(self):
        return f"GuiScene({self.scene_id})"


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

        self.scene_stack = []

        self.scenes = {}
        self.sidebar_groups = ["pre_test", "tests", "post_test"]
        self.current_scene_id = None

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
        self.sidebar = SidebarScene(self, sidebar_frame)
        self.sidebar.pack()

        #   Creates all the different frames in layers  #

        # At top so it can be referenced by other frames' code... Order of creation matters
        self.addGeneralScene(
            "login",
            LoginScene(self, self.master_frame, self.data_holder),
            "User Login",
            "pre_test",
            0,
            post_enter=lambda x: self.sidebar.disable_all_btns(),
            post_exit=lambda x: self.sidebar.enable_all_btns(),
        )
        self.addGeneralScene(
            "scan",
            ScanScene(self, self.master_frame, self.data_holder),
            "Scan",
            "pre_test",
            1,
            pre_enter=lambda x: (
                self.sidebar.disable_all_btns(),
                self.sidebar.enable_btn("login"),
            ),
            post_enter=lambda x: (
                self.sidebar.disable_all_btns(),
                self.sidebar.enable_btn("login"),
                x.scan_QR_code(self.master_window),
            ),
            post_exit=lambda x: self.sidebar.enable_all_btns(),
        )
        self.addGeneralScene(
            "post_scan",
            PostScanScene(self, self.master_frame, self.data_holder),
            "Post Scan",
        )

        self.addGeneralScene(
            "test_summary",
            TestSummaryScene(self, self.master_frame, self.data_holder),
            "Test Summary",
            "post_test",
            0,
            pre_enter=lambda *x: self.check_if_test_passed(),
        )
        self.addGeneralScene(
            "splash",
            SplashScene(self, self.master_frame),
            pre_enter=lambda x: self.sidebar.disable_all_btns(),
        )
        TestSidebarAnnot.initImages()
        self.create_test_scenes(queue)
        self.addGeneralScene(
            "test_in_progress",
            TestInProgressScene(self, self.master_frame, self.data_holder, queue, conn),
            pre_enter=lambda x: self.master_window.protocol(
                "WM_DELETE_WINDOW", self.unable_to_exit
            ),
            post_enter=lambda x: self.master_window.protocol(
                "WM_DELETE_WINDOW", self.exit_function
            ),
        )

        self.addGeneralScene(
            "add_user", AddUserScene(self, self.master_frame, self.data_holder)
        )

        logging.info("All frames have been created.")

        # Tells the master window that its exit window button is being given a new function
        self.master_window.protocol("WM_DELETE_WINDOW", self.exit_function)

        # Sets the current frame to the splash frame
        self.sidebar.setScenes(self.getScenes(), self.sidebar_groups)
        self.sidebar.update_sidebar(self)
        self.current_scene_id = "splash"
        self.gotoScene("splash")
        self.master_frame.update()
        self.master_frame.after(100, lambda *x: self.gotoScene("login"))
        self.master_window.mainloop()

    def getScenes(self):
        scenes = it.groupby(self.scenes.values(), key=lambda x: x.sidebar_group)
        scenes = [
            (x, sorted(list(y), key=lambda x: x.getSidebarIdx()))
            for x, y in scenes
            if x is not None
        ]
        scenes = sorted(scenes, key=lambda x: self.sidebar_groups.index(x[0]))
        scenes = [x for y in scenes for x in y[1]]
        return scenes

    def getNextSceneId(self):
        current = self.current_scene_id
        scenes = self.getScenes()
        scene_names = [s.scene_id for s in scenes]
        cidx = scene_names.index(current)
        next_idx = cidx + 1
        if next_idx >= len(scene_names):
            return None
        else:
            return scene_names[next_idx]

    def gotoNext(self):
        return self.gotoScene(self.getNextSceneId())

    def gotoGroup(self, scene_group):
        scenes = self.getScenes()
        s = next(x for x in scenes if x.sidebar_group == scene_group)
        self.gotoScene(s.scene_id)

    def testFrameFactory(self, test_type, test, queue):
        if test_type == "physical":
            ret = GenericPhysicalScene(
                self, self.master_frame, self.data_holder, test["id"], test["test_data"]
            )
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
        return GuiScene(
            ret,
            test["id"],
            sidebar_group="tests",
            sidebar_idx=lambda: self.data_holder.getTestIdx(test["id"]),
            sidebar_annotation=TestSidebarAnnot(self.data_holder, test["id"]),
        )

    def addGeneralScene(
        self,
        scene_id,
        frame,
        scene_name=None,
        sidebar_group=None,
        sidebar_idx=None,
        pre_enter=None,
        pre_exit=None,
        post_enter=None,
        post_exit=None,
    ):
        frame.grid(column=0, row=0)
        self.scenes[scene_id] = GuiScene(
            frame,
            scene_id,
            scene_name=scene_name,
            pre_enter=pre_enter,
            pre_exit=pre_exit,
            post_enter=post_enter,
            post_exit=post_exit,
            sidebar_group=sidebar_group,
            sidebar_idx=sidebar_idx,
        )

    def create_test_scenes(self, queue):
        test_list = self.data_holder.getTests()
        offset = 0
        for test in test_list:
            self.scenes[test["id"]] = self.testFrameFactory(test["type"], test, queue)

    def update_config(self):
        sn = self.data_holder.get_serial_ID()
        if not self.gui_cfg.getSerialCheckSafe():
            return
        new_cfg = update_config(sn)
        self.gui_cfg = new_cfg

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

    def gotoScene(self, scene_id):
        logger.info(f"Going to scene {scene_id}")
        prev_frame = self.scenes[self.current_scene_id].frame
        next_frame = self.scenes[scene_id].frame

        logger.info(f"Executing pre-exit actions for scene {self.current_scene_id}")
        self.scenes[self.current_scene_id].pre_exit(prev_frame)
        logger.info(f"Executing pre-enter actions for scene {scene_id}")
        self.scenes[scene_id].pre_enter(next_frame)

        prev_scene = self.current_scene_id
        self.scene_stack.append(self.current_scene_id)
        self.scene_stack = self.scene_stack[-100:]

        self.current_scene_id = scene_id

        next_frame.tkraise()

        logger.info(f"Executing post-exit actions for scene {prev_scene}")
        self.scenes[prev_scene].post_exit(prev_frame)
        logger.info(f"Executing post-enter actions for scene {self.current_scene_id}")
        self.scenes[self.current_scene_id].post_enter(next_frame)
        next_frame.update_frame(self)

        logger.info(f"The scene {scene_id} has been raised.")
        if hasattr(next_frame, "help_text"):
            self.set_help_text(next_frame.help_text)
        else:
            self.set_help_text("No help available for this frame")
        self.sidebar.update_sidebar(self)
        self.master_frame.update()
        self.master_window.update_idletasks()
        logger.info(f"Updated master frame.")

    def check_if_test_passed(self):
        logger.debug(
            "The method check_if_test_passed(self) has been called. This method is empty."
        )

    def critical_failure_popup(self):
        logger.debug("Critical test failed. Cannot proceed with testing")

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

    def unable_to_exit(self):
        logger.debug("The user tried to exit during a test in progress.")

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

    # Creates the popup window to show the text for current scene
    def help_popup(self, current_window):
        logger.debug("The user has requested a help window")
        logger.debug("Opening a help menu for {}".format(type(current_window)))

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

    def set_help_text(self, text):
        self.label_text.set(text)

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

    def report_bug(self, current_window):
        url = "https://github.com/UMN-CMS/HGCALTestGUI/issues"
        webbrowser.open(url, new=1)

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

    # Called when the yes button is pressed to destroy both windows
    def destroy_function(self):
        try:
            logger.info("Exiting the GUI.")
            self.master_window.update()
            self.popup.update()
            self.scenes["scan"].frame.kill_processes()

            # Destroys the popup and master window
            self.popup.destroy()
            self.popup.quit()

            self.master_window.destroy()
            self.master_window.quit()

            logger.info("The application has exited successfully.")
        except Exception as e:
            logger.info(e, exc_info=True)
            logging.debug("GUIWindow: " + repr(e))
            logging.error("GUIWindow: The application has failed to close.")
            if self.retry_attempt == False:
                logging.info("GUIWindow: Retrying...")
                self.retry_attempt = True
