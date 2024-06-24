#################################################################################

# Importing all neccessary modules
from pickle import NONE
import tkinter as tk
from tkinter import ttk
from turtle import bgcolor
from PythonFiles.GUIConfig import GUIConfig
from PythonFiles.Data.DataHolder import DataHolder
from PythonFiles.Scenes.LoginScene import LoginScene
from PythonFiles.Scenes.ScanScene import ScanScene
from PythonFiles.Scenes.SplashScene import SplashScene
from PythonFiles.Scenes.TestSummaryScene import TestSummaryScene
from PythonFiles.Scenes.AddUserScene import AddUserScene
from PythonFiles.Scenes.PostScanScene import PostScanScene
from PythonFiles.update_config import update_config
from PythonFiles.Scenes.CameraScene import CameraScene
import logging
import os
import PythonFiles

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/visual_gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

#################################################################################


# Create a class for creating the basic GUI Window to be called by the main function to
# instantiate the actual object
class GUIWindow():

    #################################################

    def __init__(self, board_cfg, main_path):
        # Create the window named "master_window"
        # global makes master_window global and therefore accessible outside the function
        global master_window
        master_window = tk.Tk()

        master_window.title("Visual Inspection Window")

        # Creates the size of the window and disables resizing
        master_window.geometry("1350x850+25+100")
        master_window.pack_propagate(1) 

        #resizing master_frame, keeping sidebar same width
        master_window.grid_columnconfigure(0, weight=0)  # Make the sidebar resizable
        master_window.grid_columnconfigure(1, weight=1)  # Make the master frame resizable 
        master_window.grid_rowconfigure(0, weight=1)

        # Variables necessary for the help popup
        self.all_text = "No help available for this scene."
        self.label_text = tk.StringVar()

        self.main_path = main_path

        # Following line prevents the window from being resizable
        # master_window.resizable(0,0)

        # Removes the tkinter logo from the window
        # master_window.wm_attributes('-toolwindow', 'True')

        # Creates and packs a frame that exists on top of the master_frame
        master_frame = tk.Frame(master_window, width = 1350, height = 850)
        master_frame.grid(column = 0, row = 0, columnspan = 4, sticky="nsew")

        self.master_frame = master_frame

        # Object for taking care of instantiation of different test types
        self.gui_cfg = GUIConfig(board_cfg)

        # Creates the "Storage System" for the data during testing
        self.data_holder = DataHolder(self.gui_cfg)

        # Creates a static image for camera to replace
        blank_image = "EnginePhoto.png"
        self.set_image_name(blank_image)

        #################################################
        #   Creates all the different frames in layers  #
        #################################################

        # At top so it can be referenced by other frames' code... Order of creation matters
        self.test_summary_frame = TestSummaryScene(self, master_frame, self.data_holder)
        self.test_summary_frame.grid(row=0, column=0, sticky='nsew')

        self.post_scan_frame = PostScanScene(self, master_frame, self.data_holder)
        self.post_scan_frame.grid(row=0, column=0, sticky='nsew')

        self.login_frame = LoginScene(self, master_frame, self.data_holder)
        self.login_frame.grid(row=0, column=0, sticky='nsew')

        self.scan_frame = ScanScene(self, master_frame, self.data_holder)
        self.scan_frame.grid(row=0, column=0, sticky='nsew')

        self.add_user_frame = AddUserScene(self, master_frame, self.data_holder)
        self.add_user_frame.grid(row=0,column=0, sticky='nsew')

        # Near bottom so it can reference other frames with its code
        self.splash_frame = SplashScene(self, master_frame)
        self.splash_frame.grid(row=0, column=0, sticky='nsew')

        self.camera_frame = CameraScene(self, master_frame, self.data_holder, 0)
        self.camera_frame.grid(row=0, column=0, sticky='nsew')

        # indices to denote photo number and camera number to know when to finish
        self.camera_index = 0
        self.photo_index = 0
        # two bools, one indicates that a photo is to be retaken
        # the other indicates whether the photo has been retaken or not
        self.retake = False
        self.retaken = False

        #################################################
        #              End Frame Creation               #
        #################################################

        # Tells the master window that its exit window button is being given a new function
        master_window.protocol('WM_DELETE_WINDOW', self.exit_function)

        # Sets the current frame to the splash frame
        self.set_frame_splash_frame()

        master_frame.after(500, self.set_frame_login_frame)

        master_window.mainloop()


    #################################################

    # is called after a board is entered
    # sets the config to either Wagon or Engine depending on the SN entered
    def update_config(self):
        full = self.data_holder.get_full_ID()
        new_cfg = update_config(full)
        self.gui_cfg = new_cfg

    #################################################

    # function for retaking the photo at the end, takes in index of desired photo
    def retake_photo(self, photo_index):
        # need to decrease the index by 1 since next frame will increment
        self.camera_index = photo_index-1
        self.photo_index = photo_index-1

        # two bools, one indicates that a photo is to be retaken
        # the other indicates whether the photo has been retaken or not
        self.retake = True
        self.retaken = False
        self.next_frame_camera_frame()


    #################################################

    def set_frame_login_frame(self):
        self.scan_frame = ScanScene(self, self.master_frame, self.data_holder)
        self.scan_frame.grid(row=0, column=0)

        # resets retake variables if the login screen is opened
        self.retake = False
        self.retaken = False

        self.login_frame.update_frame(self)
        self.set_frame(self.login_frame)

        logging.debug("GUIWindow: The frame has been set to login_frame.")
        logging.debug("GUIWindow: Conclusion of the 'set_frame_login_frame(self)' method")

    #################################################

    def first_frame_camera_frame(self):

        # Trick for bypassing the increment in "next_frame_camera_frame"
        self.camera_index = -1
        self.photo_index = -1

        self.next_frame_camera_frame()


    def next_frame_camera_frame(self):
        self.camera_index += 1
        self.photo_index += 1
        logging.debug("GUIWindow: Trying to go to the next camera_frame.")
        photo_list = self.data_holder.get_photo_list()

        # goes back to summary after photo has been retaken
        if self.retake == True and self.retaken == True:
            self.set_frame_test_summary()
        else:
            # number of photos is determined in the data holder
            if (self.camera_index < len(photo_list)):
                self.set_frame_camera_frame(self.camera_index)
            else:
                self.set_frame_test_summary()


        logging.debug("GUIWindow: Frame has been set to the next camera_frame.")


    def return_frame_camera_frame(self):
        self.camera_index -= 1
        logging.debug("GUIWindow: Trying to go back to the previous camera_frame.")
        self.camera_index = self.photo_index
        self.set_frame_camera_frame(self.camera_index)


    def set_frame_camera_frame(self, index):
        print("GUIWindow: Going to camera frame #{}".format(index))
        logging.debug("GUIWindow: Going to camera frame #{}".format(index))
        self.camera_frame.set_text(index)
        self.camera_frame.update_preview()
        self.set_frame(self.camera_frame)

    #################################################

    def set_frame_scan_frame(self):
        self.camera_index = 0
        self.photo_index = 0
        self.scan_frame.is_current_scene = True
        self.set_frame(self.scan_frame)
        self.scan_frame.scan_QR_code(master_window)

     #################################################

    def set_frame_postscan(self):
        self.post_scan_frame.update_frame()
        self.set_frame(self.post_scan_frame)

    #################################################

    def set_frame_splash_frame(self):
        self.set_frame(self.splash_frame)

    #################################################

    def set_frame_test_summary(self):
        self.test_summary_frame.update_frame()
        self.set_frame(self.test_summary_frame)

    def set_frame_add_user_frame(self):
        self.set_frame(self.add_user_frame)

    #################################################

    # Called to change the frame to the argument _frame
    def set_frame(self, _frame):

        #############################################################################
        #  The Following Code Determines What Buttons Are Visible On The Side Bar   #
        #############################################################################



        # Hides the submit button on scan frame until an entry is given to the computer
        if (_frame is not self.scan_frame):
            self.scan_frame.is_current_scene = False
            self.scan_frame.hide_submit_button()

        self.set_help_text(_frame)
        #############################################################################
        #                        End Button Visibility Code                         #
        #############################################################################

        # Raises the passed in frame to be the current frame
        _frame.tkraise()

    #################################################


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

    # Called when the no button is pressed to destroy popup and return you to the main window
    def destroy_popup(self):
        try:
            self.popup.destroy()
        except:
            print("GUIWindow: Unable to close the popup")
            logging.error("GUIWindow: Unable to close the popup")
    #################################################

    def remove_all_widgets(self):
        self.inspection_frame.remove_widgets(self)
        self.add_user_frame.remove_widgets(self)


    #################################################

    def set_image_name(self, new_name):
        self.image_name = new_name



    #################################################


    def help_popup(self, current_window):

        logging.debug("GUIWindow: The user has requested a help window")
        logging.debug("Opening a help menu for {}".format(type(current_window)))
        print("\n\nOpening a help menu for {}".format(type(current_window)))

        # Creates a popup to confirm whether or not to exit out of the window
        self.popup = tk.Toplevel()
        self.popup.title("Help Window")
        self.popup.geometry("650x650+500+300")

        self.mycanvas = tk.Canvas(self.popup, background="#808080", width=630, height =650)
        self.viewingFrame = tk.Frame(self.mycanvas, width = 200, height = 200)
        self.scroller = ttk.Scrollbar(self.popup, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)



        self.canvas_window = self.mycanvas.create_window((4,4), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")


        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

        self.onFrameConfigure(None)


        self.set_help_text(current_window)

        # Creates label in the frame
        lbl_popup = tk.Label(
            self.viewingFrame,
            textvariable = self.label_text,
            font = ('Arial', 11)
            )
        lbl_popup.grid(column = 0, row = 0, pady = 5, padx = 50)


        self.mycanvas.pack(side="right")
        self.scroller.pack(side="left", fill="both", expand=True)




    #############################################

    def set_help_text(self, current_window):

        # Help text from file
        file = open("{}/HGCAL_Help/{}_help.txt".format(PythonFiles.__path__[0], type(current_window).__name__))
        self.all_text = file.read()

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

    # Called when the yes button is pressed to destroy both windows
    def destroy_function(self, event=None):
        try:
            self.camera_frame.remove_widgets(self)

            logging.info("GUIWindow: Exiting the GUI.")

            master_window.update()
            self.popup.update()

            self.scan_frame.kill_processes()

            # Destroys the popup and master window
            self.popup.destroy()
            self.popup.quit()


            logging.info("GUIWindow: Trying to quit master_window")
            print("\nQuitting master window\n\n")
            master_window.destroy()

            logging.info("GUIWindow: Trying to destroy master_window")
            print("Destroying master window\n")
            master_window.quit()


            logging.info("GUIWindow: The application has exited successfully.")
        except Exception as e:
            print(e)
            logging.debug("GUIWindow: " + repr(e))
            logging.error("GUIWindow: The application has failed to close.")

        exit()





    ################################################


#################################################################################
