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
import cv2
import PIL.Image, PIL.ImageTk
import time
import os

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
class CameraScene(tk.Frame):

    def __init__(self, parent, master_frame, data_holder, video_source=0 ):
        
        self.master_frame = master_frame
        
        logging.info("CameraScene: Beginning to instantiate the CameraScene.")
        print("\nCameraScene: Beginning to instantiate the CameraScene.")

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 650)

        logging.info("\nCameraScene: Frame has been created.")

        self.data_holder = data_holder
        self.parent = parent

        #self.canvas=tk.Canvas(self, width=self.vid.width, height =  self.vid.height)
        self.canvas=tk.Canvas(self, width=800, height = 600 )


        # Frame for the buttons
        btn_frame=tk.Frame(self, width = 800)
        #btn_frame.place(x=0,y=0, anchor="nw", width=800)
        btn_frame.pack(anchor="nw")

        # Snapshot button
        self.btn_snapshot=tk.Button(btn_frame, text="Snapshot",width=20, command=self.snapshot, fg="white")
        self.btn_snapshot.pack(side="left", padx=10, pady=10)

        # Help button
        self.btn_proses=tk.Button(
            btn_frame, 
            text="Help",
            width=10, 
            relief = tk.RAISED,
            command= lambda: self.help_action(parent),  
            fg="white"
        )
        self.btn_proses.pack(side="left", padx=10, pady=10)

        self.btn_about=tk.Button(
            btn_frame,
            text="Submit", 
            width=10, 
            command= lambda: self.submit_button_action(), 
            fg="white"
        )
        self.btn_about.pack(side="right", padx=10, pady=10)

        self.long_desc_label_text = tk.StringVar()
        self.long_desc_label_text.set("Photo Description")

        self.long_desc_label = tk.Label(
            master= btn_frame,
            textvariable = self.long_desc_label_text,
            font = ('Arial', 10),
        )
        self.long_desc_label.pack(side="right", padx=(20, 90), pady=10)
        


        self.desc_label_text = tk.StringVar()
        self.desc_label_text.set("Photo Type")

        self.desc_label = tk.Label(
            master= btn_frame,
            textvariable = self.desc_label_text,
            font = ('Arial', 19),
        )
        self.desc_label.pack(side="right", padx=(90, 20), pady=10)

        self.canvas.pack()
	# Prevents the frame from shrinking
        self.pack_propagate(0)


        # How long in between photo-frames on the GUI
        self.delay=10


    def update_preview(self):

        camera.start_preview(True, x = 500, y = 200, width = 1200, height = 800)
        camera.start()
        #camera.set_controls( {"AfMode" : controls.AfModeEnum.Manual} )

  

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)

    #################################################

    def set_text(self, index):
        self.current_index = index

        updated_title = self.data_holder.get_photo_list()[index]["name"]        
        updated_description = self.data_holder.get_photo_list()[index]["desc_short"]
        print("updated_title: ", updated_title)

        self.desc_label_text.set(updated_title)
        self.long_desc_label_text.set(updated_description)

        pass

    ################################################# 

    def snapshot(self):
        # Writes the image to a file with a name that includes the date
        # TODO Change this to be a more readable file name later
        shortened_pn = "captured_image{}.png".format(self.current_index)
        self.photo_name = "{}/Images/{}".format(PythonFiles.__path__[0], shortened_pn)
        print("self.photo_name: ", self.photo_name)

        # Sets the camera to a slower framerate, higher resolution
        capture_config = camera.create_still_configuration()

        # Automatically switches back to faster framerate
        camera.switch_mode_and_capture_image(self.photo_name)



        self.data_holder.image_data.append(self.photo_name)
        self.parent.set_image_name(shortened_pn)


    # Submits the photo and goes to the next screen
    def submit_button_action(self):
        camera.stop_preview()
        self.parent.set_frame_photo_frame()


    # Closes the video camera with the "release()" command
    # Important for closing gracefully
    def __del__(self):
        pass

    def remove_widgets(self, parent):
        camera.close()
        self.__del__()
