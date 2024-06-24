'''
    CAMERA_SCENE
------------------
Instructions:
1. Ensure a version of python has been installed (created on Python 3.11.4)
2. Run the command "pip install Pillow"
3. Run the command "pip install opencv-python" 
------------------
'''
# import PythonFiles
import json, logging
import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import os


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
        logging.info("CameraScene: Beginning to instantiate the CameraScene.")
        print("\nCameraScene: Beginning to instantiate the CameraScene.")

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width=850, height=500)

        logging.info("\nCameraScene: Frame has been created.")

        self.data_holder = data_holder
        self.parent = parent

        # Creates instance variable of parameter video_source
        self.video_source=video_source

        # Adds the video capturing component to the canvas
        # Then packs the canvas to the frame
        self.vid= MyVideoCapture(self.video_source)
        self.canvas=tk.Canvas(self, width=self.vid.width, height =  self.vid.height)
        self.canvas.pack()

        # Frame for the buttons
        btn_frame=tk.Frame(self, background=self.from_rgb((117, 123, 129)))
        btn_frame.place(x=0,y=0, anchor="nw", width=self.vid.width+4)

        # Snapshot button
        self.btn_snapshot=tk.Button(btn_frame, text="Snapshot",width=20, command=self.snapshot, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_snapshot.pack(side="left", padx=10, pady=10)

        # Proses button
        # Empty command; could be linked with more features
        self.btn_proses=tk.Button(btn_frame, text="Proses", width=10, command=None, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_proses.pack(side="left", padx=10, pady=10)

        # About button
        # Empty command; could be linked with more features
        self.btn_about=tk.Button(btn_frame, text="About", width=10, command=None, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_about.pack(side="right", padx=10, pady=10)

        # How long in between photo-frames on the GUI
        self.delay=15

        # Updates the video constantly on this slide
        self.update()



    # Takes a snapshot of the video
    # Saves in the same directory as the 
    def snapshot(self):
        ret, frame=self.vid.get_frame()

        if ret:
            # Writes the image to a file with a name that includes the date
            # TODO Change this to be a more readable file name later
            self.photo_name = "frame-"+time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"

            try:
                cv2.imwrite(self.photo_name, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) )
                # self.data_holder.
            except:
                logging.warning("CameraScene: Unable to write the snapshot to a file")
                print("\nUnable to save photo to file {}".format(self.photo_name))

        else:
            print("\nUnable to take a snapshot.\n")

    # This is the key method to show the active camera on the GUI
    # Basically gets an image from the camera and updates the PIL Image Canvas
    # Updates the canvas after "self.delay" milliseconds
    def update(self):
        ret, frame=self.vid.get_frame()

        if ret:
            # Updates the canvas on the GUI
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, image=self.photo, anchor=tk.NW)

            # Recursive method; waits "self.delay" before calling itself
            self.window.after(self.delay,self.update)

    def from_rgb(self,rgb):
        return "#%02x%02x%02x" % rgb

# Class responsible for the video capturing feature
# Requires the import of cv2
class  MyVideoCapture:
    """docstring for  MyVideoCapture"""
    def __init__(self, video_source=0):
        # Instantiating a VideoCapture device from cv2 library
        self.vid = cv2.VideoCapture(video_source)
        
        # Throw an exception if the video source cannot be opened.
        if not self.vid.isOpened():
            raise ValueError("VideoCapture: Unable to open the video source. Check camera.", video_source)

        # Getting the camera width and height to correctly display resolution
        # Important component for a correct display
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Gets the VideoCapture video
    # Called by the update() method
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret,None)		
    
    # Closes the video camera with the "release()" command
    # Important for closing gracefully
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

