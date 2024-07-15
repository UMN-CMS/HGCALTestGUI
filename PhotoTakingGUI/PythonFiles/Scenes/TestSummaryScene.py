#################################################################################

import PythonFiles
import json, logging
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk as iTK
from PIL import Image
from matplotlib.pyplot import table
from pyparsing import col
import PythonFiles
import os

#################################################################################

logging.getLogger('PIL').setLevel(logging.WARNING)


logger = logging.getLogger('HGCAL_GUI')
FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Frame that shows all of the final test results
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class TestSummaryScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):

        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width = 1350, height = 850)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        logging.info("TestSummaryScene: Frame has been created.")

        self.data_holder = data_holder

        self.parent = parent

        self.create_frame(parent)

        self.create_style(parent)

        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)
    
    def create_style(self, _parent):
 
        self.s = ttk.Style()
 
        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')
 
        self.s.theme_use('awdark')

    #################################################

    def create_frame(self, parent):
        logging.debug("TestSummaryScene: Destroying old widgets on the TestSummaryScene.")
        print("TestSummaryScene: Destroying old widgets on the TestSummaryScene.")
        try:
            for widget in self.winfo_children():
                widget.destroy()
        except:
            logging.warning("TestSummaryScene: Widgets could not be found and/or destroyed (making room for new widgets.")
        else:
            logging.info("TestSummaryScene: Widgets destroyed successfully (making room for new widgets).")


        logging.debug("TestSummaryScene: Table is being created with the results.")
        print("\n\nTestSummaryScene: Table is being created with the results.")

        self.blank_frame = ttk.Frame(self)
        self.blank_frame.grid(row = 0, column = 0, padx = 80, pady = 20)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)

        # Adds the title to the TestSummary Frame
        self.title = ttk.Label(
                self,
                #fg='#0d0d0d',
                text = "Visual Inspection Finished!",
                font=('Arial',32,'bold')
                )
        self.title.grid(row= 0, column= 1, pady = 20)

        self.retake_prompt = ttk.Label(
                self,
                text = 'Click an image to retake it.',
                font=('Arial', 20),
        )
        self.retake_prompt.grid(row=1,column=1)

        row_offset = 0


        # Tries to add all of the images to the final screen
        # different formatting depending on the number of photos taken
        # images can be clicked to retake that photo
        for i, photo in enumerate(self.data_holder.image_holder):
            try:
                Board_image = self.data_holder.image_holder[photo]
                Board_image = Board_image.resize((350, 200), Image.LANCZOS)
                Board_PhotoImage = iTK.PhotoImage(Board_image)
                if i == 0:
                    retake_1 = ttk.Button(
                            self,
                            image = Board_PhotoImage,
                            command = lambda: self.btn_retake_action(parent, 0)
                            )
                    retake_1.image = Board_PhotoImage
                    retake_1.grid(column = i+1, row = 2)
                if i == 1:
                    retake_2 = ttk.Button(
                            self,
                            image = Board_PhotoImage,
                            command = lambda: self.btn_retake_action(parent, 1)
                            )
                    retake_2.image = Board_PhotoImage
                    retake_2.grid(column = i+1, row = 2)

            except Exception as e:
                print("TestSummaryScene: Could not find captured_image.")
                print(e)
                logging.debug("TestSummaryScene: Could not find captured_image.")
                logging.debug("Exception: {}".format(e))
                next

        logging.debug("TestSummaryScene: Creating the board image.")



       # Adds Board full id to the TestSummaryFrame
        self.lbl_full = ttk.Label(
                self,
                text = "Full ID: " + str(self.data_holder.data_dict['current_full_ID']),
                font=('Arial', 32)
                )
        self.lbl_full.grid(column = 1, row = 3 + row_offset, pady = 10)

        # Adds Tester Name to the TestSummary Frame
        self.lbl_tester = ttk.Label(
                self,
                text = "Tester: " + self.data_holder.data_dict['user_ID'],
                font=('Arial', 24)
                )
        self.lbl_tester.grid(column = 1, row = 4 + row_offset, pady = 10)


        # Creating frame for logout button
        frm_logout = ttk.Frame(self)
        frm_logout.grid(column = 1, row = 6 + row_offset, pady = 20)


        # Creating the next board button
        next_board_button = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Submit and Go to Next Board",
            command = lambda: self.btn_NextBoard_action(parent)
        )
        next_board_button.pack(anchor = 'ne', padx = 10, pady = 10)


        # Creating the logout button
        btn_logout = ttk.Button(
            frm_logout,
            #relief = tk.RAISED,
            text = "Logout",
            command = lambda: self.btn_logout_action(parent)
        )
        btn_logout.pack(anchor = 'n', padx = 10, pady = 20)




    #################################################

    def btn_NextBoard_action(self, parent):
        # this function saves the images
        self.data_holder.send_image()
        parent.set_frame_scan_frame()

    def btn_logout_action(self, parent):
        parent.set_frame_login_frame()

    def btn_retake_action(self, parent, photo_index):
        parent.retake_photo(photo_index)

    def get_submit_action(self):
        return self.btn_NextBoard_action

    def get_parent(self):
        return self.parent



    #################################################

    def update_frame(self):
        self.create_frame(self.parent)



#################################################################################
