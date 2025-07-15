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
from pathlib import Path

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Scenes.TestSummaryScene')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

# Frame that shows all of the final test results
# @param parent -> References a GUIWindow object
# @param master_frame -> Tkinter object that the frame is going to be placed on
# @param data_holder -> DataHolder object that stores all relevant data

class TestSummaryScene(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
    
        self.parent = parent
        self.create_style(parent)
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame, width=1300-213, height=800)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)


        self.id_text = tk.StringVar()

        self.data_holder = data_holder

        # Instantiates an updated table with the current data
        #self.create_updated_table(parent)

        self.parent = parent

        # Adds the title to the TestSummary Frame
        self.title = ttk.Label(
                self, 
                #fg='#0d0d0d', 
                text = "Testing Finished!",
                font=('Arial',28,'bold')
                )
        self.title.grid(row= 0, column= 1, pady = 20, sticky='ew')


        self.id_text.set("Full ID: " + str(self.data_holder.data_dict['current_full_ID']))       

        # Adds Board Full ID to the TestSummaryFrame
        self.lbl_id = ttk.Label(
                self, 
                textvariable = self.id_text,
                font=('Arial', 20)
                )
        self.lbl_id.grid(column = 2, row = 0, pady = 20, padx = 5, sticky='ew')
        
        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)


    #################################################
    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark')
    
    # Creates the table with the updated information from the data_holder
    # @param parent -> References the GUIWindow object that creates the class
    
    def create_updated_table(self, parent):

        logger.info("Summary table is being updated.")        
        
        self.list_of_tests =self.data_holder.getPhysicalNames() + self.data_holder.getTestNames()
        self.list_of_table_labels = ["Test Name", "Test Status", "Actions"]
        self.list_of_completed_tests = self.data_holder.data_lists['physical_completion'] +  self.data_holder.data_lists['test_completion']
        self.list_of_pass_fail = self.data_holder.data_lists['physical_results'] + self.data_holder.data_lists['test_results']

        self.test_results = self.data_holder.get_test_results()

        
        #Checks for duplicate test names, which cause problems with saving the json files
        prev_names = set()

        for name in self.list_of_tests:
            if name in prev_names:
                logger.warning(f'Warning, Duplicate test name found: {name}')
            else:
                prev_names.add(name)
            

        self.id_text.set("Full ID: " + str(self.data_holder.data_dict['current_full_ID']))       

        # Adds Tester Name to the TestSummary Frame
        self.lbl_tester = ttk.Label(
                self, 
                text = "Tester: " + self.data_holder.data_dict['user_ID'],
                font=('Arial', 24)
                )
        self.lbl_tester.grid(column = 3, row = 0, pady = 20, padx = 5, sticky='ew')
            
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)



        ##########

        self.mycanvas = tk.Canvas(self)
        self.viewingFrame = ttk.Frame(self.mycanvas)
        self.scroller = ttk.Scrollbar(self, orient="vertical", command=self.mycanvas.yview)
        self.mycanvas.configure(yscrollcommand=self.scroller.set)

        self.mycanvas.grid(row = 3, column = 0, columnspan = 4, sticky="nsew")
        self.scroller.grid(row = 3, column = 4, sticky = 'nsw')
    

        self.canvas_window = self.mycanvas.create_window((0,0), window=self.viewingFrame, anchor='nw', tags="self.viewingFrame")
        #self.viewingFrame.pack(fill='both', expand=True)


        self.viewingFrame.columnconfigure(0, weight = 1)
        self.viewingFrame.columnconfigure(1, weight = 1)
        self.viewingFrame.columnconfigure(2, weight = 1)
        self.viewingFrame.columnconfigure(3, weight = 1)
        self.rowconfigure(3, weight = 1)

        self.mycanvas.bind('<Configure>', self.onCanvasConfigure)
        self.viewingFrame.bind('<Configure>', self.onFrameConfigure)
        self.viewingFrame.bind('<Enter>', self.onEnter)
        self.viewingFrame.bind('<Leave>', self.onLeave)

 

        
        # Adds the labels to the top of the table
        for index in range(len(self.list_of_table_labels)):
            _label = ttk.Label(
                    self.viewingFrame, 
                    text = self.list_of_table_labels[index], 
                    #relief = 'ridge', 
                    width=25, 
                    #height=1, 
                    font=('Arial', 24, "bold")
                    )
            _label.grid(row= 3, column=index, sticky='nsew', padx = 15, pady = 15)

        Green_Check_Image = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
        Green_Check_Image = Green_Check_Image.resize((50,50), Image.LANCZOS)
        Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
        Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        Red_X_Image = Red_X_Image.resize((50,50), Image.LANCZOS)
        Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
        notrun_Image = Image.open("{}/Images/not_yet_run.png".format(PythonFiles.__path__[0]))
        notrun_Image = notrun_Image.resize((50,50), Image.LANCZOS)
        notrun_PhotoImage = iTK.PhotoImage(notrun_Image)

        for index,key in enumerate(self.list_of_tests):
            _label= ttk.Label(
                    self.viewingFrame, 
                    text = key, 
                    #relief = 'ridge', 
                    width=25, 
                    #height=3, 
                    font=('Arial', 16)
                    )
            _label.grid(row=index + 5, column=0, sticky='nsew', padx = 15, pady = 15)
            if self.test_results[key] == 'Passed':
                GreenCheck_Label = ttk.Label(self.viewingFrame, image=Green_Check_PhotoImage, width=75)
                GreenCheck_Label.image = Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + 5, column=1, pady = 15)

            elif self.test_results[key] == 'Failed':
                RedX_Label = ttk.Label(self.viewingFrame, image=Red_X_PhotoImage, width=75)
                RedX_Label.image = Red_X_PhotoImage

                RedX_Label.grid(row=index + 5, column=1, pady = 15)
            else:
                notrun_Label = ttk.Label(self.viewingFrame, image=notrun_PhotoImage, width=75)
                notrun_Label.image = notrun_PhotoImage

                notrun_Label.grid(row=index + 5, column=1, pady = 15)
            
            

        ## Adds the test names to the first column
        #for index in range(len(self.list_of_tests)):
        #    _label= ttk.Label(
        #            self.viewingFrame, 
        #            text = self.list_of_tests[index], 
        #            #relief = 'ridge', 
        #            width=25, 
        #            #height=3, 
        #            font=('Arial', 16)
        #            )
        #    _label.grid(row=index + 5, column=0, sticky='nsew', padx = 15, pady = 15)
        #


        ## Create Labels that tell whether or not a test was completed
        #for index in range(len(self.list_of_completed_tests)):
        #    
        #    # Instantiates a Label
        #    _label = ttk.Label(
        #                self.viewingFrame,
        #                width=25, 
        #                font=('Arial',16)
        #                )

        #    # if the test is completed, set the label to "Complete"
        #    if (self.list_of_completed_tests[index]):
        #        _label.config(
        #                text = "COMPLETED",
        #                justify = "center"
        #                )
        #    # else, set the label to "Unfinished"
        #    else:
        #        _label.config(
        #                text = "UNFINISHED",
        #                justify = "center"
        #                )

        #    # Puts the completed/unfinished label into the table       
        #    _label.grid(row=index + 5, column=1, sticky="ew", padx = 10, pady = 15)


        ## Adds the Image as to whether the test was completed or not
        #for index in range(len(self.list_of_pass_fail)):
        #    if(self.list_of_pass_fail[index]):
        #        # Create a photoimage object of the QR Code
        #        Green_Check_Image = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
        #        Green_Check_Image = Green_Check_Image.resize((50,50), Image.LANCZOS)
        #        Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
        #        GreenCheck_Label = ttk.Label(self.viewingFrame, image=Green_Check_PhotoImage, width=75)
        #        GreenCheck_Label.image = Green_Check_PhotoImage

        #        GreenCheck_Label.grid(row=index + 5, column=2, pady = 15)

        #    else:
        #        # Create a photoimage object of the QR Code
        #        Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        #        Red_X_Image = Red_X_Image.resize((50,50), Image.LANCZOS)
        #        Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
        #        RedX_Label = ttk.Label(self.viewingFrame, image=Red_X_PhotoImage, width=75)
        #        RedX_Label.image = Red_X_PhotoImage

        #        RedX_Label.grid(row=index + 5, column=2, pady = 15)


        self.create_retest_more_info_btns(parent)

    #################################################
    #################################################

    def onFrameConfigure(self, event):
        self.mycanvas.configure(scrollregion=self.mycanvas.bbox('all'))

    def onCanvasConfigure(self, event):
        self.mycanvas.itemconfig(self.canvas_window, width=event.width)


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

        rows = []
        retests = []
        more_infos = []

        for i in range(len(self.list_of_tests)):
            rows.append(ttk.Frame(self.viewingFrame))
            rows[i].grid(column = 2, row = i + 5)

            retests.append(ttk.Button(
                    rows[i], 
                    text = "RETEST",
                    #padx= 5,
                    #pady=3,  
                    command = lambda i=i: self.btn_retest_action(parent, i)
                    ))
            retests[i].grid(column = 0, row = i , pady = 15)

            more_infos.append(ttk.Button(
                    rows[i], 
                    text = "MORE INFO", 
                    #padx= 5,
                    #pady=3, 
                    command = lambda i=i: self.btn_more_info_action(parent, i)
                    ))
            more_infos[i].grid(column=1, row = i , pady = 15)
        
            rows[i].columnconfigure(0, weight=1)
            rows[i].columnconfigure(1, weight=1)

        btn_next_test = ttk.Button(
                self.viewingFrame, 
                text = "NEXT BOARD",
                #font = ('Arial', 15), 
                command = lambda: self.btn_next_test_action(parent)
                )
        btn_next_test.grid(column = 3, row = self.data_holder.getNumTest() + 5, sticky='se', pady=50, padx = 50)        
    
        
    #################################################

    # A function to be called within GUIWindow to create the console output
    # when the frame is being brought to the top
    def create_JSON_popup(self, JSON_String, test):
        try:
            # Creating a popup window for the JSON Details
            self.JSON_popup = tk.Toplevel()
            self.JSON_popup.geometry("500x300+750+100")
            self.JSON_popup.title("JSON Details")
            # self.JSON_popup.wm_attributes('-toolwindow', 'True')

            self.JSON_popup.grab_set()
            self.JSON_popup.attributes('-topmost', 'true') 
            self.JSON_popup.grid_rowconfigure(0, weight=1)
            self.JSON_popup.grid_columnconfigure(0, weight=1)
            self.JSON_popup.grid_propagate()

            # Creating a Frame For Console Output
            frm_JSON = ttk.Frame(self.JSON_popup, width = 500, height = 300)
            frm_JSON.pack_propagate(0)
            frm_JSON.grid(row=0, column=0, sticky='nsew')

            # Placing an entry box in the frm_console
            self.JSON_entry_box = tk.Text(
                frm_JSON, 
                bg = '#6e5e5d', 
                fg = 'white', 
                font = ('Arial', 14)
                )
            self.JSON_entry_box.pack(anchor = 'center', fill=tk.BOTH, expand=1)

            logger.debug(JSON_String)
            current_JSON_file = open(JSON_String)
            current_JSON_data = json.load(current_JSON_file)


            temp = ""
            temp = json.dumps(current_JSON_data, indent=2)
            #for key, value in current_JSON_data.items():
            #    temp = temp + "{} : {}".format(key, value) + "\n"


            self.JSON_entry_box.delete(1.0,"end")
            self.JSON_entry_box.insert(1.0, temp)
            
            current_JSON_file.close()   
        except Exception as e:
            logger.exception(e)
            logger.warning("More Info popup has failed to be created.")

            

    #################################################

    # All of the different methods for what the retest buttons should do
    def btn_retest_action(self, _parent, test_idx):
        _parent.set_frame_test(test_idx)

    #################################################

    def btn_more_info_action(self, _parent, test_idx):
        names = self.data_holder.getTestNames()
        logger.info('Opening JSON file for %s...' % names[test_idx])
        self.create_JSON_popup("{}/JSONFiles/Current_{}_JSON.json".format(Path.home(), names[test_idx].replace(" ", "").replace("/", "")), names[test_idx])

    #################################################

    # Next test button action
    def btn_next_test_action(self, _parent):
        self.data_holder.data_holder_new_test()
        self.lbl_id.destroy()
        _parent.reset_board()

    def get_submit_action(self):
        return self.btn_next_test_action

    def get_parent(self):
        return self.parent
        
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
