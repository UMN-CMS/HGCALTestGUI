#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.font as font
import logging
import PythonFiles

# Importing Necessary Files
from PythonFiles.utils.REQClient import REQClient

#################################################################################

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/shared/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'w', format=FORMAT, level=logging.DEBUG)

# Creating class for the window
class TestScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, test_name, queue, test_idx):
        super().__init__(master_frame, width=850, height=500)
        self.queue = queue
        self.test_name = test_name
        self.data_holder = data_holder
        self.test_idx = test_idx
        print("Making test scene with index".format(self.test_idx))
        
        self.update_frame(parent)

    #################################################

    def update_frame(self, parent):
        logging.debug("ParentTestClass: A test frame has been updated.")
        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 15)

        # Create a centralized window for information
        frm_window = tk.Frame(self, width = 850, height = 500)
        frm_window.grid(column=1, row=1, padx = 223, pady = 100)

        # Create a label for the tester's name
        lbl_tester = tk.Label(
            frm_window, 
            text = "Tester: ", 
            font = font_scene
            )
        lbl_tester.pack(side = 'top')

        # Create an entry for the tester's name
        ent_tester = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_tester.insert(0, self.data_holder.data_dict['user_ID'])
        ent_tester.pack(side = 'top')
        ent_tester.config(state = "disabled")

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            frm_window, 
            text = "Serial Number: ", 
            font = font_scene
            )
        lbl_snum.pack(side = 'top')

        # Create a entry for the serial number box
        ent_snum = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_snum.insert(0, self.data_holder.data_dict['current_serial_ID'])
        ent_snum.pack(side = 'top')
        ent_snum.config(state = "disabled")

        # Create a label for the test about to be run
        lbl_test = tk.Label(
            frm_window, 
            text = "Current Test: ", 
            font = font_scene
            )
        lbl_test.pack(side = 'top')


        # Create a entry for the test type
        self.ent_test = tk.Entry(
            frm_window, 
            font = font_scene
            )
        self.ent_test.pack(side = 'top')
        self.ent_test.insert(0, self.test_name)
        self.ent_test.config(state = "disabled")

        # Create a label for confirming test
        lbl_confirm = tk.Label(
            frm_window, 
            text = "Are you ready to begin the test?", 
            font = font_scene
            )
        lbl_confirm.pack(side = 'top')

        # Create a button for confirming test
        btn_confirm = tk.Button(
            frm_window, 
            text = "Confirm", 
            relief = tk.RAISED, 
            command = lambda:self.btn_confirm_action(parent)
            )
        btn_confirm.pack(side = 'top')
        btn_confirm['font'] = font.Font(family = 'Arial', size = 13)

        # Create frame for logout button
        frm_logout = tk.Frame(self)
        frm_logout.grid(column = 2, row = 2, sticky = 'n')

        # Create a logout button
        btn_logout = tk.Button(
            frm_logout, 
            text = "Logout", 
            relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'center')

        # Create a frame for the back button
        frm_back = tk.Frame(self)
        frm_back.grid(column = 2, row = 0, sticky = 'n')

        # Create a rescan button
        btn_rescan = tk.Button(
            frm_back, 
            text = "Change Boards", 
            relief = tk.RAISED, 
            command = lambda: self.btn_rescan_action(parent))
        btn_rescan.pack(anchor = 'n')


        

        self.grid_propagate(0)
        
    #################################################

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.reset_board()
    
    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        print("Confirm button sending test{}".format(self.test_idx))
        test_client = REQClient('test{}'.format(self.test_idx), self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
        _parent.set_frame_test_in_progress(self.queue)

    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        _parent.set_frame_login_frame()

    #################################################


#################################################################################


class Test1Scene(TestScene):
    
    logging.info("Test1Scene: Frame has successfully been created.")

    # Override to add specific functionality
    def btn_confirm_action(self, _parent):

        self.data_holder.print()
        super().btn_confirm_action(_parent)
        test_1_client = REQClient('test1', self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
        _parent.set_frame_test_in_progress(self.queue)

#################################################################################


class Test2Scene(TestScene):

    logging.info("Test2Scene: Frame has successfully been created.")

    # Override to add specific functionality
    def btn_confirm_action(self, _parent):
        self.data_holder.print()
        super().btn_confirm_action(_parent)
        test_2_client = REQClient('test2', self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
        _parent.set_frame_test_in_progress(self.queue)
        


#################################################################################


class Test3Scene(TestScene):

    logging.info("Test3Scene: Frame has successfully been created.")

    # Override to add specific functionality
    def btn_confirm_action(self, _parent):

        self.data_holder.print()
        super().btn_confirm_action(_parent)
        test_3_client = REQClient('test3', self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
        _parent.set_frame_test_in_progress(self.queue)


#################################################################################


class Test4Scene(TestScene):

    logging.info("Test4Scene: Frame has successfully been created.")

    # Override to add specific functionality
    def btn_confirm_action(self, _parent):

        self.data_holder.print()
        super().btn_confirm_action(_parent)
        test_4_client = REQClient('test4', self.data_holder.data_dict['current_serial_ID'], self.data_holder.data_dict['user_ID'])
        _parent.set_frame_test_in_progress(self.queue)

#################################################################################

