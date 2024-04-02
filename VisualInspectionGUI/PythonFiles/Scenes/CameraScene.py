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
from PIL import ImageTk as iTK
import time
import os

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
class CameraScene(tk.Frame):

    def __init__(self, parent, master_frame, data_holder, video_source=0 ):

        self.photo_packed = False

        self.master_frame = master_frame

        logging.info("CameraScene: Beginning to instantiate the CameraScene.")
        print("\nCameraScene: Beginning to instantiate the CameraScene.")

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1105, height = 850)

        logging.info("\nCameraScene: Frame has been created.")

        self.data_holder = data_holder
        self.parent = parent


        # Frame for the buttons
        btn_frame=tk.Frame(self, width = 800)
        #btn_frame.place(x=0,y=0, anchor="nw", width=800)
        btn_frame.pack(anchor="nw")

        # Snapshot button
        self.btn_snapshot=tk.Button(btn_frame, text="Snapshot",width=20, command=self.snapshot, fg="white")
        self.btn_snapshot.pack(side="left", padx=10, pady=10)

        # Submit Button
        # self.btn_snapshot=tk.Button(btn_frame, text="Submit",width=20, command=self.submit_button_action, fg="white")
        # self.btn_snapshot.pack(side="right", padx=10, pady=10)

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

	# Prevents the frame from shrinking
        self.pack_propagate(0)


        # How long in between photo-frames on the GUI
        self.delay=10

        self.camera_created = False


    def update_preview(self):

        # Prevents the camera from being started twice
        # If the camera is started twice, throws exceptions
        if self.camera_created == False:

            self.camera_config = camera.create_still_configuration(main={"size": (2304, 1296)}, lores={'size': (854, 480)}, display='lores')

            camera.configure(self.camera_config)

            camera.start_preview(Preview.DRM, x = 900, y = 200, width = 854, height = 480)

            camera.start()

            self.camera_created = True

            print("Camera Preview started")

        camera.set_controls( {"AfMode" : controls.AfModeEnum.Continuous} )



    #################################################

    # Tells GUIWindow to open up the help popup
    def help_action(self, _parent):
        _parent.help_popup(self)

    #################################################

    # Updates the description for the image from the config file
    def set_text(self, index):
        self.current_index = index

        if self.data_holder.photos == 'Top and Bottom':
            updated_title = self.data_holder.get_photo_list()[index]["name"]
            updated_description = self.data_holder.get_photo_list()[index]["desc_short"]
            print("updated_title: ", updated_title)
        else:
            updated_title = 'Connector ' + str(index+1)
            updated_description = ''

        self.desc_label_text.set(updated_title)
        self.long_desc_label_text.set(updated_description)

    #################################################

    # Saves a picture of the currently shown camera
    def snapshot(self):
        # Writes the image to a file with a name that includes the date
        shortened_pn = "captured_image{}.png".format(self.current_index)
        self.photo_name = "{}/Images/{}".format(PythonFiles.__path__[0], shortened_pn)
        print("self.photo_name: ", self.photo_name)

        # Cannot be called unless camera is already started
        self.image = camera.switch_mode_and_capture_image(shortened_pn)

        #try:
        #    camera.stop_preview()
        #    camera.stop()
        #    self.camera_created = False
        #except:
        #    print("CameraScene: Unable to stop preview")
        #    logging.debug("CameraScene: Unable to stop preview")

        # Displays the image
        # Ensure that the camera aspect ratio matches the aspect ratio here
        # This may require some fine-tuning
        #self.Engine_image = PIL.Image.open(self.photo_name)
        self.data_holder.image_holder[self.photo_name] = self.image
        self.Engine_image = self.image
        self.Engine_image = self.Engine_image.resize((1067, 600), PIL.Image.LANCZOS)
        self.Engine_PhotoImage = iTK.PhotoImage(self.Engine_image)

        # Check to see if it should just replace the old image
        if self.photo_packed is False:
            self.Engine_label = tk.Label(self)
            self.Engine_label.configure(image=self.Engine_PhotoImage)
            self.Engine_label.image = self.Engine_PhotoImage

            self.Engine_label.pack()
            self.photo_packed = True
        else:
            self.Engine_label.configure(image=self.Engine_PhotoImage)
            self.Engine_label.image = self.Engine_PhotoImage
            print("\nreset image\n")

        self.data_holder.image_data.append(self.photo_name)
        self.parent.set_image_name(shortened_pn)

        #self.submit_button_action()

    def continuous_update(self):

        time.sleep(1)
        for i in range(100):

            self.snapshot()

            time.sleep(1)

    # Submits the photo and goes to the next screen
    # doesn't save the photo to disk initially for increased speed
    # photo is stored in a dictionary and all photos are saved at the end
    def submit_button_action(self):
        try:
            camera.stop_preview()
            camera.stop()
            self.camera_created = False
        except:
            print("CameraScene: Unable to stop preview")
            logging.debug("CameraScene: Unable to stop preview")
        if self.parent.retake == True:
            self.parent.retaken = True

        self.parent.next_frame_camera_frame()
        #self.parent.set_frame_photo_frame()


    # Closes the video camera with the "release()" command
    # Important for closing gracefully
    def __del__(self):
        pass

    def remove_widgets(self, parent):
        camera.close()
        self.__del__()
