#################################################################################

import PythonFiles
import json, logging
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk as iTK
from PIL import Image
from matplotlib.pyplot import table
from pyparsing import col
import PythonFiles
import os

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.TestSummaryScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Frame that shows all of the final test results
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class TestSummaryScene(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        self.parent = parent
        
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width=870, height=500)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        self.sn_text = tk.StringVar()

        logger.info("TestSummaryScene: Frame has been created.")

        self.data_holder = data_holder

        # Instantiates an updated table with the current data
        self.create_updated_table(parent)
        

    #################################################

    
    # Creates the table with the updated information from the data_holder
    # @param parent -> References the GUIWindow object that creates the class
    
    def create_updated_table(self, parent):

        logger.debug("TestSummaryScene: Table is being updated.")        
        
        self.list_of_tests =self.data_holder.getPhysicalNames() + self.data_holder.getTestNames()
        self.list_of_table_labels = ["Test Name", "Test Status", "Pass/Fail", "Actions"]
        self.list_of_completed_tests = self.data_holder.data_lists['physical_completion'] +  self.data_holder.data_lists['test_completion']
        self.list_of_pass_fail = self.data_holder.data_lists['physical_results'] + self.data_holder.data_lists['test_results']

        
        #Checks for duplicate test names, which cause problems with saving the json files
        prev_names = set()

        for name in self.list_of_tests:
            if name in prev_names:
                logger.debug(f'Warning, Duplicate test name found: {name}')
            else:
                prev_names.add(name)
            
        
        print(self.list_of_completed_tests)
        print(self.list_of_pass_fail)

        self.sn_text.set("Serial Number: " + str(self.data_holder.data_dict['current_serial_ID']))       
        ##########    

        # Adds the title to the TestSummary Frame
        self.title = tk.Label(
            self,
            fg='#0d0d0d',
            text="Testing Finished!",
            font=('Arial', 14)
        )
        self.title.grid(row=0, column=0, pady=5, sticky='ew')

        self.sn_text.set("Serial Number: " + str(self.data_holder.data_dict['current_serial_ID']))

        # Adds Board Serial Number to the TestSummaryFrame
        self.lbl_snum = tk.Label(
            self,
            textvariable=self.sn_text,
            font=('Arial', 14)
        )
        self.lbl_snum.grid(column=1, row=0, pady=5, padx=5, sticky='ew')

        # Adds Tester Name to the TestSummary Frame
        self.lbl_tester = tk.Label(
            self,
            text="Tester: " + self.data_holder.data_dict['user_ID'],
            font=('Arial', 14)
        )
        self.lbl_tester.grid(column=2, row=0, pady=5, padx=5, sticky='ew')
        
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)




        ##########

        self.mycanvas = tk.Canvas(self)
        self.viewingFrame = tk.Frame(self.mycanvas, width = 802, height = 400)
        self.scroller = ttk.Scrollbar(self, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        self.mycanvas.grid(row = 3, column = 0, columnspan = 4, sticky="nsew")
        self.scroller.grid(row = 3, column = 4, sticky = 'nsw')
    

        self.canvas_window = self.mycanvas.create_window((0,0), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")
        self.viewingFrame.pack(fill='both', expand=True)


        self.viewingFrame.columnconfigure(0, weight = 1)
        self.viewingFrame.columnconfigure(1, weight = 1)
        self.viewingFrame.columnconfigure(2, weight = 1)
        self.viewingFrame.columnconfigure(3, weight = 1)
        self.rowconfigure(3, weight = 1)

        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

        #self.onFrameConfigure(None)
 

        
        # Adds the labels to the top of the table
        for index in range(len(self.list_of_table_labels)):
            _label = tk.Label(
                    self.viewingFrame, 
                    text = self.list_of_table_labels[index], 
                    relief = 'ridge',  
                    font=('Arial', 11, "bold"),
                    padx=5,   # Horizontal padding
                    pady=5    # Vertical padding
                    )
            _label.grid(row= 0, column=index, sticky='nsew')
            

        # Adds the test names to the first column
        for index in range(len(self.list_of_tests)):
            _label= tk.Label(
                    self.viewingFrame, 
                    text = self.list_of_tests[index], 
                    font=('Arial', 11),
                    padx=5,   
                    pady=5    
                    )
            _label.grid(row=index + 1, column=0, sticky='nsew')
        


        # Create Labels that tell whether or not a test was completed
        for index in range(len(self.list_of_completed_tests)):
            
            # Instantiates a Label
            _label = tk.Label(
                        self.viewingFrame,
                        font=('Arial',11),
                        padx=5, 
                        pady=5    
                        )

            # if the test is completed, set the label to "Complete"
            if (self.list_of_completed_tests[index]):
                _label.config(
                        text = "COMPLETED"
                        )
            # else, set the label to "Unfinished"
            else:
                _label.config(
                        text = "UNFINISHED"
                        )

            # Puts the completed/unfinished label into the table       
            _label.grid(row=index + 1, column=1, sticky="ew")


        # Adds the Image as to whether the test was completed or not
        for index in range(len(self.list_of_pass_fail)):
            if(self.list_of_pass_fail[index]):
                # Create a photoimage object of the QR Code
                Green_Check_Image = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
                Green_Check_Image = Green_Check_Image.resize((50,50), Image.LANCZOS)
                Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
                GreenCheck_Label = tk.Label(self.viewingFrame, image=Green_Check_PhotoImage, width=50, height=50)
                GreenCheck_Label.image = Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + 1, column=2)

            else:
                # Create a photoimage object of the QR Code
                Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
                Red_X_Image = Red_X_Image.resize((50,50), Image.LANCZOS)
                Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
                RedX_Label = tk.Label(self.viewingFrame, image=Red_X_PhotoImage, width=50, height=50)
                RedX_Label.image = Red_X_PhotoImage

                RedX_Label.grid(row=index + 1, column=2)


        self.create_retest_more_info_btns(parent)
        

        #self.viewingFrame.update_idletasks()
        #self.mycanvas.update_idletasks()        

        new_width = self.viewingFrame.winfo_reqwidth()
        new_height = self.viewingFrame.winfo_reqheight()
        
        print("\nnew_width: {}, new_height: {}\n".format(new_width, new_height))


        self.mycanvas.configure(width = new_width, height = new_height)      

        #self.scrollerFrame.grid(row = 2, column = 1, columnspan = 4)

        logger.debug("TestSummaryScene: Table finished update.")     

    #################################################
    #################################################

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.mycanvas.configure(scrollregion=self.mycanvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.mycanvas.itemconfig(self, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.


    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll( -1, "units" )
        elif event.num == 5:
            self.mycanvas.yview_scroll( 1, "units" )

    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")



    #################################################
    

    #################################################

    # Creates all of the retest button
    def create_retest_more_info_btns(self, parent):

        logging.debug("TestSummaryScene: Buttons are being created.")

        rows = []
        retests = []
        more_infos = []

        for i in range(self.data_holder.getNumTest() + self.data_holder.getNumPhysicalTest()):
            rows.append(tk.Frame(self.viewingFrame))
            rows[i].grid(column = 3, row = i + 1)

            retests.append(tk.Button(
                    rows[i], 
                    text = "RETEST",
                    padx= 5,
                    pady=3,  
                    command = lambda i=i: self.btn_retest_action(parent, i)
                    ))
            retests[i].grid(column = 0, row = 0)

            more_infos.append(tk.Button(
                    rows[i], 
                    text = "MORE INFO", 
                    padx= 5,
                    pady=3, 
                    command = lambda i=i: self.btn_more_info_action(parent, i)
                    ))
            more_infos[i].grid(column=1, row = 0)
        
            rows[i].columnconfigure(0, weight=1)
            rows[i].columnconfigure(1, weight=1)

        btn_next_test = tk.Button(
                self.viewingFrame, 
                text = "NEXT BOARD",
                font = ('Arial', 15), 
                command = lambda: self.btn_next_test_action(parent)
                )
        btn_next_test.grid(column = 3, row = self.data_holder.getNumTest() + 3, sticky='se', padx=20, pady=50)
        

        logger.debug("TestSummaryScene: Buttons finshed being created.")
    
        
    #################################################

    # A function to be called within GUIWindow to create the console output
    # when the frame is being brought to the top
    def create_JSON_popup(self, JSON_String):
        try:
            # Creating a popup window for the JSON Details
            self.JSON_popup = tk.Toplevel()
            self.JSON_popup.geometry("500x300+750+100")
            self.JSON_popup.title("JSON Details")
            # self.JSON_popup.wm_attributes('-toolwindow', 'True')

            self.JSON_popup.grab_set()
            self.JSON_popup.attributes('-topmost', 'true') 

            # Creating a Frame For Console Output
            frm_JSON = tk.Frame(self.JSON_popup, width = 500, height = 300, bg = 'green')
            frm_JSON.pack_propagate(0)
            frm_JSON.pack()

            # Placing an entry box in the frm_console
            self.JSON_entry_box = tk.Text(
                frm_JSON, 
                bg = '#6e5e5d', 
                fg = 'white', 
                font = ('Arial', 14)
                )
            self.JSON_entry_box.pack(anchor = 'center', fill=tk.BOTH, expand=1)

            current_JSON_file = open(JSON_String)
            current_JSON_data = json.load(current_JSON_file)


            temp = ""
            for key, value in current_JSON_data.items():
                temp = temp + "{} : {}".format(key, value) + "\n"


            self.JSON_entry_box.delete(1.0,"end")
            self.JSON_entry_box.insert(1.0, temp)
            
            current_JSON_file.close()   
        except Exception as e:
            logger.debug(e)
            logger.warning("TestSummaryScene: More Info popup has failed to be created.")

            

    #################################################

    # All of the different methods for what the retest buttons should do
    def btn_retest_action(self, _parent, test_idx):
        _parent.set_frame_test(test_idx)

    def btn_retest1_action(self, _parent):
        _parent.set_frame(_parent.test1_frame)
 
    def btn_retest2_action(self, _parent):
        _parent.set_frame(_parent.test2_frame)
        
    def btn_retest3_action(self, _parent):
        _parent.set_frame(_parent.test3_frame)

    def btn_retest4_action(self, _parent):
        _parent.set_frame(_parent.test4_frame)

    #################################################

    def btn_more_info_action(self, _parent, test_idx):
        names = self.data_holder.getTestNames()
        self.create_JSON_popup("{}/JSONFiles/Current_{}_JSON.json".format(PythonFiles.__path__[0], names[test_idx].replace(" ", "").replace("/", "")))

    def btn_more_info1_action(self, _parent):
        self.create_JSON_popup("{}/JSONFiles/Current_GenRes_JSON.json".format(PythonFiles.__path__[0]))

    def btn_more_info2_action(self, _parent):
        self.create_JSON_popup("{}/JSONFiles/Current_IDRes_JSON.json".format(PythonFiles.__path__[0]))

    def btn_more_info3_action(self, _parent):
        self.create_JSON_popup("{}/JSONFiles/Current_IIC_JSON.json".format(PythonFiles.__path__[0]))
    
    def btn_more_info4_action(self, _parent):
        self.create_JSON_popup("{}/JSONFiles/Current_BERT_JSON.json".format(PythonFiles.__path__[0]))

    #################################################

    # Next test button action
    def btn_next_test_action(self, _parent):
        self.data_holder.data_holder_new_test()
        self.lbl_snum.destroy()
        _parent.reset_board()
        logger.info("TestSummaryScene: Starting a new test.")
        
    #################################################

    # Updates the frame to show current data
    def update_frame(self):
        self.create_updated_table(self.parent)

    #################################################

    # TODO Check what this is used for
    def add_new_test(self, _list_of_completed_tests, _list_of_pass_fail):
        self.list_of_completed_tests = _list_of_completed_tests
        self.list_of_pass_fail = _list_of_pass_fail

    #################################################

#################################################################################
