################################################################################

# Imports all the necessary modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from xml.dom.expatbuilder import parseFragmentString
import time
import logging
import PythonFiles
import os

#################################################################################
logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.TestInProgressScene')

# Creating the frame itself
class TestInProgressScene(ttk.Frame):
    def __init__(self, parent, master_frame, data_holder, queue, _conn):
        
        super().__init__(master_frame, width=1300-213, height = 800)

        self.create_style(parent)
        self.queue = queue
        self.data_holder = data_holder
        self.is_current_scene = False
        self.initialize_scene(parent, master_frame)
        self.conn = _conn

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')

    ##################################################

    # A function for the stop button
    #def btn_stop_action(self, _parent):
    #    self.window_closed = True
    #    _parent.go_to_next_test()

    #    
    #    # Destroys the console window
    #    self.console_destroy()
        
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
        
        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side = "right", fill = 'y')


        # Placing an entry box in the frm_console
        global ent_console
        ent_console = tk.Text(
            self, 
            bg = 'black', 
            fg = 'white', 
            height= 15,
            width= 75,
            font = ('Arial', 15),
            yscrollcommand = scrollbar.set
            )
        

        # Adding scrollbar functionality
        scrollbar.config(command = ent_console.yview)


        # Creating the main title in the frame
        lbl_title = ttk.Label(self, 
            text = "Test in progress. Please wait.", 
            font = ('Arial', 32)
            )
        lbl_title.pack(padx = 0, pady = 50)

        # Create a progress bar that does not track progress but adds motion to the window
        self.progressbar = ttk.Progressbar(
            self, 
            orient = 'horizontal',
            mode = 'indeterminate', length = 350)
        self.progressbar.pack(padx = 50)
        self.stop_txt = ttk.Label(self,
            text='Waiting for test to finish...',
            font=('Arial', 15)
        )
        self.stop_txt.pack_forget()
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
        #_parent.return_to_current_test()
        self.progressbar.stop()
        self.stop_txt.pack(padx=0, pady=50)
        _parent.stop_tests()
        #self.queue.put('Stop')

    def remove_stop_txt(self):
        self.stop_txt.pack_forget()

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
            logger.info("TestInProgressScene: Beginning the while loop")
            
            information_received = False
            while 1>0:
                master_window.update()
                if not queue.empty():    
                    information_received = True
                    text = queue.get()
                    logger.debug(text)
                    ent_console.insert(tk.END, text.strip('\r\n'))
                    # need this twice since the first one is stripped from the original text
                    ent_console.insert(tk.END, "\n")
                    ent_console.insert(tk.END, "\n")
                    ent_console.see('end')

                    if "Done." in text:
                        logger.info("Stopping Progress Bar.")
                        self.progressbar.stop()

                    if "Exit." in text:
                        self.progressbar.stop()
                        time.sleep(1)
                        parent.test_error_popup("Unable to run test")
                        logger.error("Unable to run test.")
                        break

                    if "Results received successfully." in text:
                    
                        message =  self.conn.recv()
                        self.data_holder.update_from_json_string(message) 
                        
                        logger.info("JSON Received.")
                        logger.debug(message)
#                        FinishedTestPopup(parent, self.data_holder, queue)
#
#                    if "Closing Test Window." in text:
                        logger.info("TestInProgressScene: ending loop")
                        try:
                            master_window.update()
                        except Exception as e:
                            logger.warning('Unable to update master_window')
                            logger.exception(e)

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

            logger.exception(e)

            # Throw a message box that shows the error message
            # Logs the message
            time_sec = counter*refresh_break
            logger.error('Timeout Error', "Exception received -> Process timed out after 10 seconds")

            messagebox.showwarning('Timeout Error', "TestInProgressScene: Process timed out after 10 seconds")
            logger.info("Trying to go back to the login frame.")
            parent.set_frame_login_frame()
            return False
        
        #except Exception as e:
            
        #    print("\n\nException:  ", e, "\n\n")

        return True    

#########################################################


class FinishedTestPopup():
    
    #################################################

    def __init__(self, parent, data_holder, queue):
        self.create_style(parent)
        self.finished_popup(data_holder)
        self.parent = parent    
        self.queue = queue

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
        
        self.s.theme_use('awdark')

    #################################################

    def finished_popup(self, data_holder):
        self.data_holder = data_holder
        logger.info("Test Finished")
        # Creates a popup to ask whether or not to retry the test
        self.popup = tk.Toplevel()
        self.popup.title("Test Completed") 
        self.popup.geometry("300x200+500+300")
        self.popup.pack_propagate(1) 
        self.popup.grid_columnconfigure(0, weight=1)  # Make the master frame resizable 
        self.popup.grid_rowconfigure(0, weight=1)
        self.popup.grab_set()

        # Creates frame in the new window
        frm_popup = ttk.Frame(self.popup, width=300, height=200)
        frm_popup.grid(row=0, column=0, sticky='nsew')

        bind_func = self.continue_function
        frm_popup.bind_all("<Return>", lambda event: bind_func(self.parent))

        # Creates label in the frame
        lbl_popup = ttk.Label(
            frm_popup, 
            text = "Test has finished running.",
            font = ('Arial', 13)
            )
        lbl_popup.grid(column = 0, row = 0)

        btn_continue = ttk.Button(
            frm_popup,
            text = "Continue",
            command = lambda: self.continue_function(self.parent)
        )
        btn_continue.grid(column = 0, row = 1)

        frm_popup.grid_columnconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(0, weight=1)
        frm_popup.grid_rowconfigure(1, weight=1)

        
    #################################################

    # Called to continue on in the testing procedure
    def continue_function(self, _parent):  
        self.popup.destroy()
        self.queue.put('Closing Test Window.')


