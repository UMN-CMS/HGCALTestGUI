################################################################################

# Imports all the necessary modules
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from xml.dom.expatbuilder import parseFragmentString
import time
import logging
logging.getLogger('PIL').setLevel(logging.WARNING)
import PythonFiles
import os

#################################################################################
logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.TestInProgressScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Creating the frame itself
class TestInProgressScene(tk.Frame):
    def __init__(self, parent, master_frame, data_holder, queue, _conn):
        logger.info("TestInProgressScene: Beginning the initialization of the TestInProgressScene.")
        
        super().__init__(master_frame, width=870, height = 650)

        self.queue = queue
        self.data_holder = data_holder
        self.is_current_scene = False
        self.initialize_scene(parent, master_frame)
        self.conn = _conn

    ##################################################

    # A function for the stop button
    def btn_stop_action(self, _parent):
        self.window_closed = True
        _parent.go_to_next_test()

        
        # Destroys the console window
        self.console_destroy()
        
    #################################################    

    # Goes to the next scene after the progress scene is complete
    def go_to_next_frame(self, _parent):
        _parent.go_to_next_test()

    #################################################    

    # Used to bring the user back to the test that just failed
    def go_to_previous_frame(self, _parent, previous_frame):
        self.previous_frame = previous_frame
        _parent.set_frame(previous_frame)


    # Used to initialize the frame that is on the main window
    # next_frame is used to progress to the next scene and is passed in from GUIWindow
    def initialize_scene(self, parent, master_frame):
        
        logger.info("TestInProgressScene: The frame has been initialized.")
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side = "right", fill = 'y')


        # Placing an entry box in the frm_console
        global ent_console
        ent_console = tk.Text(
            self, 
            bg = 'black', 
            fg = 'white', 
            height= 15,
            width= 400,
            font = ('Arial', 15),
            yscrollcommand = scrollbar.set
            )
        

        # Adding scrollbar functionality
        scrollbar.config(command = ent_console.yview)


        # Creating the main title in the frame
        lbl_title = tk.Label(self, 
            text = "Test in progress. Please wait.", 
            font = ('Arial', 20)
            )
        lbl_title.pack(padx = 0, pady = 50)

        # Create a progress bar that does not track progress but adds motion to the window
        self.progressbar = ttk.Progressbar(
            self, 
            orient = 'horizontal',
            mode = 'indeterminate', length = 350)
        self.progressbar.pack(padx = 50)
        # A Button To Stop the Progress Bar and Progress Forward (Temporary until we link to actual progress)
        btn_stop = ttk.Button(
            self, 
            text='Stop', 
            command= lambda: self.btn_stop_action(parent))
        btn_stop.pack(padx = 0, pady = 25)

        ent_console.pack(anchor = 'center')



        # Forces the frame to stay the size of the master_frame
        self.pack_propagate(0)

    # A function for the stop button
    def btn_stop_action(self, _parent):
        _parent.return_to_current_test()
        self.progressbar.stop()
        #self.queue.put('Stop')



    # Goes to the next scene after the progress scene is complete
    def go_to_next_frame(self, _parent):
        _parent.go_to_next_test()
        self.window_closed = True
        

    # Used to bring the user back to the test that just failed
    def go_to_previous_frame(self, _parent, previous_frame):
        self.previous_frame = previous_frame
        _parent.set_frame(previous_frame)

    #################################################

    def begin_update(self, master_window, queue, parent):

        logger.info("TestInProgressScene: Started console update loop.")
        
        # How long before the queue is being checked (if empty)
        # units of seconds
        refresh_break = 0.01

        # Time spent in the waiting phase; in units of refresh_break
        # Time waiting (sec) = counter * refresh_break
        counter = 0

        self.progressbar.start(10)

        self.window_closed = False

        # Maximum timeout in seconds
        Timeout_after = 10
        MAX_TIMEOUT = Timeout_after / 2.5
        try:
            print("\n\nTestInProgressScene: Beginning the while loop\n\n") 
            logger.info("TestInProgressScene: While-loop - Beginning try catch for receiving data through the pipeline.")
            
            information_received = False
            while 1>0:
                #try:
                #print("\nUpdating master_window")
                master_window.update()
                #print("Queue: ")
                #print(queue)
                if not queue.empty():    
                    #print("\n\nTestInProgressScene: the queue is not empty") 
                    information_received = True
                    logger.info("TestInProgressScene: Waiting for queue objects...")
                    text = queue.get()
                    print(text)
                    ent_console.insert(tk.END, text)
                    ent_console.insert(tk.END, "\n")
                    ent_console.see('end')

                    if "Done." in text:
                        print('Stopping Progress Bar')
                        self.progressbar.stop()

                    if "Exit." in text:
                        self.progressbar.stop()
                        time.sleep(1)
                        parent.test_error_popup("Unable to run test")
                        break

                    if text == "Results received successfully.":
                    
                        message =  self.conn.recv()
                        print(message)   
                        self.data_holder.update_from_json_string(message) 
                        
                        logger.info("TestInProgressScene: JSON Received.")
                        try:
                            master_window.update()
                        except Exception as e:
                            print("\nTestInProgressScene: Unable to update master_window\n")
                            print("Exception: ", e)

                        time.sleep(0.02)
                        break

                if self.window_closed == True:
                    self.progressbar.destroy()
                    break
                    
                #else:
                #
                #    print("TestInProgressScene: The queue is empty, going to sleep for {} seconds".format(refresh_break))

                #    # Sleep before looking for more information
                #    time.sleep(refresh_break)

                #    # Increment the counter of time spent sleeping
                #    counter = counter + 1

                #    # If beyond the MAX_TIMEOUT range -> raise an exception
                #    if (counter > MAX_TIMEOUT/refresh_break) and not information_received:
                #        print("\n\nTestInProcessScene: Raising an exception now\n")
                #        logger.info("TestInProgressScene: Raising Exception -> Timeout Reached - 10 seconds")
                #        raise ValueError("Process timed out after 10 seconds")
                #        time.sleep(1)
                #        break
        except ValueError as e:
            
            print("\n\nException:  ", e)

            # Throw a message box that shows the error message
            # Logs the message
            time_sec = counter*refresh_break
            logger.info('TestInProgressScene: Timeout Error', "Exception received -> Process timed out after 10 seconds")

            messagebox.showwarning('Timeout Error', "TestInProgressScene: Process timed out after 10 seconds")
            logger.info("TestInProgressScene: Trying to go back to the login frame.")
            parent.set_frame_login_frame()
            return False
        
        #except Exception as e:
            
        #    print("\n\nException:  ", e, "\n\n")

        return True    

