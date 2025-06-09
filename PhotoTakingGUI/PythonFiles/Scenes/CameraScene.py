'''
    CAMERA_SCENE
------------------
Instructions:
1. Ensure a version of python has been installed (created on Python 3.11.4)
2. Run the command "pip install Pillow"
3. Run the command "pip install opencv-python"
------------------
'''
import PythonFiles
import json, logging
from picamera2 import Picamera2, Preview
import tkinter as tk
import tkinter.ttk as ttk
import cv2
import PIL.Image, PIL.ImageTk
from PIL import ImageTk as iTK
from PIL import ImageChops
import time
import os
import numpy as np

from libcamera import controls

global camera
camera = Picamera2()

#################################################################################

# Instantiating logging
# Code that should go in every file in the GUI(s)
logging.getLogger('PIL').setLevel(logging.WARNING)
logger = logging.getLogger('HGCAL_GUI')
FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/visual_gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)


# Frame class for basic webcam functionality
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data
class CameraScene(ttk.Frame):

    def __init__(self, parent, master_frame, data_holder, video_source=0 ):

        # variables to determine what to do with photo and prompting text
        self.photo_packed = False
        self.flip = False

        self.master_frame = master_frame

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 850)

        self.data_holder = data_holder
        self.parent = parent

        # Add the style
        self.create_style(parent)

        # Frame for the buttons
        btn_frame=ttk.Frame(self, width = 800)
        btn_frame.pack(anchor="nw")

        # Snapshot button
        self.btn_snapshot=ttk.Button(btn_frame, text="Snapshot",width=20, command=self.snapshot)
        self.btn_snapshot.pack(side="left", padx=10, pady=10)

        # Help button
        self.btn_proses=ttk.Button(
            btn_frame,
            text="Help",
            width=10,
            #relief = tk.RAISED,
            command= lambda: self.help_action(parent),
        )
        self.btn_proses.pack(side="left", padx=10, pady=10)

        self.btn_about=ttk.Button(
            btn_frame,
            text="Submit",
            width=10,
            command= lambda: self.submit_button_action(),
        )
        self.btn_about.pack(side="right", padx=10, pady=10)

        self.long_desc_label_text = tk.StringVar()
        self.long_desc_label_text.set("Photo Description")

        self.long_desc_label = ttk.Label(
            master= btn_frame,
            textvariable = self.long_desc_label_text,
            font = ('Arial', 24),
        )
        self.long_desc_label.pack(side="right", padx=(20, 90), pady=10)

        self.desc_label_text = tk.StringVar()
        self.desc_label_text.set("Photo Type")

        self.desc_label = ttk.Label(
            master= btn_frame,
            textvariable = self.desc_label_text,
            font = ('Arial', 24),
        )
        self.desc_label.pack(side="right", padx=(90, 20), pady=10)

        # Prevents the frame from shrinking
        self.pack_propagate(0)


        # How long in between photo-frames on the GUI
        self.delay=10

        self.camera_created = False

    def create_style(self, _parent):
  
        self.s = ttk.Style()
  
        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
  
        self.s.theme_use('awdark')


    def update_preview(self):

        # gets rid of any old image
        if self.photo_packed == True:
            self.Engine_label.destroy() 
            self.photo_packed = False
            

        # Prevents the camera from being started twice
        # If the camera is started twice, throws exceptions
        if self.camera_created == False:

            self.camera_config = camera.create_still_configuration(main={"size": (2304, 1296)}, lores={'size': (854, 480)}, display='lores')

            camera.configure(self.camera_config)

            camera.start_preview(Preview.DRM, x = 900, y = 200, width = 854, height = 480)

            camera.start()

            self.camera_created = True

        camera.set_controls( {"AfMode" : controls.AfModeEnum.Continuous} )



    #################################################

    # Tells GUIWindow to open up the help popup
    def help_action(self, _parent):
        _parent.help_popup(self)

    #################################################

    # Updates the description for the image from the config file
    def set_text(self, index):
        self.current_index = index

        updated_title = self.data_holder.get_photo_list()[index]["name"]
        updated_description = self.data_holder.get_photo_list()[index]["desc_short"]

        self.desc_label_text.set(updated_title)
        self.long_desc_label_text.set(updated_description)

        if self.flip == True:
            self.flip_label.destroy()
            self.flip_label = False

        # adds text saying to flip the board over if it's the first time the bottom picture is being taken
        if self.parent.retake == True:
            pass
        elif updated_title == 'Bottom': 
            self.flip_label = ttk.Label(
                master = self,
                text = 'Flip Board Over',
                font = ('Arial', 20),
        )
            self.flip_label.pack()
            self.flip = True


    #################################################

    # Saves a picture of the currently shown camera
    def snapshot(self):
        # sets up a name for the file
        shortened_pn = "captured_image{}.png".format(self.current_index)
        self.photo_name = "{}/Images/{}".format(PythonFiles.__path__[0], shortened_pn)

        # Cannot be called unless camera is already started
        self.image = camera.switch_mode_and_capture_image(shortened_pn)
        min_area = 25000
        padding = 50

        img_rgb = np.array(self.image)
        if img_rgb.shape[-1] == 4:
            img_rgb = img_rgb[:, : , :3]
        height, width, _ = img_rgb.shape
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        # select pixels that aren't white
        lower = np.array([0, 30, 30])
        upper = np.array([180, 255, 255])
        non_white_mask = cv2.inRange(hsv, lower, upper)

        kernel = np.ones((5, 5), np.uint8)
        clean_mask = cv2.morphologyEx(non_white_mask, cv2.MORPH_OPEN, kernel)
        clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, kernel)

        # select edges around non white objects
        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best = None
        best_score = 0

        for c in contours:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            # filter out small dust particles and such
            if area < min_area:
                continue

            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            if hull_area == 0:
                continue

            # how solid is the object? closer to 1 = more solid
            solidity = area / hull_area
            score = solidity * area
            # saves the largest and most solid object, should always be the board
            if score > best_score:
                best = (x, y, w, h)
                best_score = score

        if best is not None:
            x, y, w, h = best
            # don't go over the bounds of the image
            x_start = max(x - padding, 0)
            y_start = max(y - padding, 0)
            x_end = min(x + w + padding, width)
            y_end = min(y + h + padding, height)

            imageBox = (x_start, y_start, x_end, y_end)
            self.image = self.image.crop(imageBox)

        # stores the image in the data holder
        # doesn't try to write it to disk, uses more ram but saves time
        self.data_holder.image_holder[self.photo_name] = self.image
        # scales the image to fit the gui window after it's been cropped
        # this doesn't affect the size of the actual image that goes into the Database
        width = int(self.image.size[0]*(800/self.image.size[1]))
        self.Engine_image = self.image.resize((width, 800), PIL.Image.LANCZOS)
        if width > 1000:
            height = int(self.image.size[1]*(1000/self.image.size[0]))
            self.Engine_image = self.image.resize((1000, height), PIL.Image.LANCZOS)
        self.Engine_PhotoImage = iTK.PhotoImage(self.Engine_image)

        # if the flip prompt exists, destroy it
        if self.flip == True:
            self.flip_label.destroy()
            self.flip = False

        # if there isn't an image currently displayed, add one
        if self.photo_packed == False:
            self.Engine_label = ttk.Label(self)
            self.Engine_label.configure(image=self.Engine_PhotoImage)
            self.Engine_label.image = self.Engine_PhotoImage

            self.Engine_label.pack()
            self.photo_packed = True
        # else, replace the previous image
        # this is used when retaking the image before clicking submit
        else:
            self.Engine_label.configure(image=self.Engine_PhotoImage)
            self.Engine_label.image = self.Engine_PhotoImage

        self.data_holder.image_data.append(self.photo_name)
        self.parent.set_image_name(shortened_pn)

    def continuous_update(self):

        time.sleep(1)
        for i in range(100):

            self.snapshot()

            time.sleep(1)

    # goes to the next screen
    def submit_button_action(self):
        try:
            camera.stop_preview()
            camera.stop()
            self.camera_created = False
        except:
            print("CameraScene: Unable to stop preview")
            logging.debug("CameraScene: Unable to stop preview")

        # if a photo is being retaken, set the retaken value to true
        if self.parent.retake == True:
            self.parent.retaken = True

        self.parent.next_frame_camera_frame()

    def get_submit_action(self):
        return self.submit_button_action

    def get_parent(self):
        return self.parent


    # Closes the video camera with the "release()" command
    # Important for closing gracefully
    def __del__(self):
        pass

    def remove_widgets(self, parent):
        camera.close()
        self.__del__()
