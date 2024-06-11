'''
    CAMERA GUI
------------------
Instructions:
1. Ensure a version of python has been installed (created on Python 3.11.4)
2. Run the command "pip install Pillow"
3. Run the command "pip install opencv-python" 
4. Run the command "pip install tkinter"
5. Run the GUI; "python ./MainFunction.py"
------------------

'''

import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time

# GUI class for basic webcam functionality
# Sample class instantiation: App(tkinter.Tk(),"tkinter ad OpenCV")
class App:

    def __init__(self, window, window_title, video_source=0):
		
        # Sets up the tkinter window
        self.window=window
        self.window.title=(window_title)

        # Creates instance variable of parameter video_source
        self.video_source=video_source

        # Adds the video capturing component to the canvas
        # Then packs the canvas to the frame
        self.vid= MyVideoCapture(self.video_source)
        self.canvas=tkinter.Canvas(window, width=self.vid.width, height =  self.vid.height)
        self.canvas.pack()

        # Frame for the buttons
        btn_frame=tkinter.Frame(window, background=self.from_rgb((117, 123, 129)))
        btn_frame.place(x=0,y=0, anchor="nw", width=self.vid.width+4)

        # Snapshot button
        self.btn_snapshot=tkinter.Button(btn_frame, text="Snapshot",width=20, command=self.snapshot, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_snapshot.pack(side="left", padx=10, pady=10)

        # Proses button
        # Empty command; could be linked with more features
        self.btn_proses=tkinter.Button(btn_frame, text="Proses", width=10, command=None, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_proses.pack(side="left", padx=10, pady=10)

        # About button
        # Empty command; could be linked with more features
        self.btn_about=tkinter.Button(btn_frame, text="About", width=10, command=None, bg=self.from_rgb((52, 61, 70)), fg="white")
        self.btn_about.pack(side="right", padx=10, pady=10)

        # How long in between photo-frames on the GUI
        self.delay=15

        self.update()

        # Required for tkinter to stay open
        # Closing the mainloop will close the program
        self.window.mainloop()

    # Takes a snapshot of the video
    # Saves in the same directory as the 
    def snapshot(self):
        ret, frame=self.vid.get_frame()

        if ret:
            # Writes the image to a file with a name that includes the date
            # TODO Change this to be a more readable file name later
            cv2.imwrite("frame-"+time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) )
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
            self.canvas.create_image(0,0, image=self.photo, anchor=tkinter.NW)

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

# How to instantiate this GUI
App(tkinter.Tk(),"tkinter ad OpenCV")
