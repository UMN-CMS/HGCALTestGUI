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

logger = logging.getLogger(__name__)


class TestSummaryScene(tk.Frame):
    def __init__(self, parent, master_frame, data_holder):
        # Call to the super class's constructor
        # Super class is the tk.Frame class
        super().__init__(master_frame)

        Green_Check_Image = Image.open(
            "{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0])
        )
        Green_Check_Image = Green_Check_Image.resize((75, 75), Image.LANCZOS)
        Red_X_Image = Image.open("{}/Images/RedX.png".format(PythonFiles.__path__[0]))
        Red_X_Image = Red_X_Image.resize((75, 75), Image.LANCZOS)
        self.Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
        self.Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)

        self.parent = parent


        self.sn_text = tk.StringVar()

        logger.info("TestSummaryScene: Frame has been created.")

        self.data_holder = data_holder

        # Setting weights of columns so the column 4 is half the size of columns 0-3
        for i in range(self.data_holder.getNumTests()):
            self.columnconfigure(i, weight=2)
        self.columnconfigure(self.data_holder.getNumTests(), weight=1)
        # Instantiates an updated table with the current data
        self.create_updated_table(parent)

        # Adds the title to the TestSummary Frame
        self.title = tk.Label(
            self, fg="#0d0d0d", text="Testing Finished!", font=("Arial", 18, "bold")
        )
        self.title.grid(row=0, column=1, pady=20)

        self.sn_text.set(f"Serial Number: {self.data_holder.getActiveSerial()}")

        # Adds Board Serial Number to the TestSummaryFrame
        self.lbl_snum = tk.Label(self, textvariable=self.sn_text, font=("Arial", 14))
        self.lbl_snum.grid(column=2, row=0, pady=20, padx=5)
        # Fits the frame to set size rather than interior widgets
        self.grid_propagate(0)

    # Creates the table with the updated information from the data_holder
    def create_updated_table(self, parent):
        logger.debug("TestSummaryScene: Table is being updated.")

        self.tests = self.data_holder.getTests()
        self.sn_text.set(f"Serial Number: {self.data_holder.getActiveSerial()}")
        self.lbl_tester = tk.Label(
            self,
            text=f"Tester: {self.data_holder.getActiveUser()}",
            font=("Arial", 14),
        )
        self.lbl_tester.grid(column=3, row=0, pady=20, padx=5)
        self.mycanvas = tk.Canvas(self)
        self.viewingFrame = tk.Frame(self.mycanvas)
        self.scroller = ttk.Scrollbar(
            self, orient="vertical", command=self.mycanvas.yview
        )
        self.mycanvas.configure(yscrollcommand=self.scroller.set)
        self.mycanvas.grid(row=3, column=1, columnspan=4)
        self.scroller.grid(row=3, column=0, sticky="NS")

        self.canvas_window = self.mycanvas.create_window(
            (4, 4), window=self.viewingFrame, anchor="nw", tags="self.viewingFrame"
        )

        self.viewingFrame.bind("<Configure>", self.onFrameConfigure)
        self.mycanvas.bind("<Configure>", self.onCanvasConfigure)

        self.viewingFrame.bind("<Enter>", self.onEnter)
        self.viewingFrame.bind("<Leave>", self.onLeave)

        self.onFrameConfigure(None)

        # Setting weights of columns so the column 4 is half the size of columns 0-3
        for i in range(self.data_holder.getNumTests()):
            self.viewingFrame.columnconfigure(i, weight=2)
        self.viewingFrame.columnconfigure(self.data_holder.getNumTests(), weight=1)

        table_labels = ["l1", "l2", "l3"]
        for i, l in enumerate(table_labels):
            _label = tk.Label(
                self.viewingFrame,
                text=l,
                relief="ridge",
                width=25,
                height=1,
                font=("Arial", 11, "bold"),
            )
            _label.grid(row=0, column=i)

        # Adds the test names to the first column
        tests = self.data_holder.getTests()
        for test in tests:
            test_state = self.data_holder.getTestState(test['id'])
            idx = test["idx"] + 1
            _label = tk.Label(
                self.viewingFrame,
                text=test["test_data"]["name"],
                relief="ridge",
                width=25,
                height=3,
                font=("Arial", 11),
            )
            _label.grid(row=idx, column=0)
            _label = tk.Label(
                self.viewingFrame,
                relief="ridge",
                width=25,
                height=3,
                font=("Arial", 11),
            )
            if test_state["completed"]:
                _label.config(text="COMPLETED")
            else:
                _label.config(text="UNFINISHED")
            _label.grid(row=idx, column=1)
            if test_state["passed"]:
                GreenCheck_Label = tk.Label(
                    self.viewingFrame,
                    image=self.Green_Check_PhotoImage,
                    width=75,
                    height=75,
                )
                GreenCheck_Label.grid(row=idx, column=2)

            else:
                RedX_Label = tk.Label(
                    self.viewingFrame, image=self.Red_X_PhotoImage, width=75, height=75
                )
            RedX_Label.grid(row=idx, column=2)

        self.create_retest_more_info_btns(parent)

        new_width = self.viewingFrame.winfo_reqwidth()
        new_height = self.viewingFrame.winfo_reqheight()

        self.mycanvas.configure(width=new_width, height=new_height)
        logger.debug("Table finished update.")

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.mycanvas.configure(
            scrollregion=self.mycanvas.bbox("all")
        )  # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        """Reset the canvas window to encompass inner frame when required"""
        canvas_width = event.width

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        if event.num == 4:
            self.mycanvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.mycanvas.yview_scroll(1, "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        self.mycanvas.bind_all("<Button-4>", self.onMouseWheel)
        self.mycanvas.bind_all("<Button-5>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        self.mycanvas.unbind_all("<Button-4>")
        self.mycanvas.unbind_all("<Button-5>")

    # Creates all of the retest button
    def create_retest_more_info_btns(self, parent):
        logging.debug("Buttons are being created.")
        tests = self.data_holder.getTests()
        for test in tests:
            idx = test["idx"]
            tid = test["id"]
            vf = tk.Frame(self.viewingFrame)
            vf.grid(column=3, row=idx + 1)
            rt = tk.Button(
                vf,
                text="RETEST",
                padx=5,
                pady=3,
                command=lambda i=tid: self.btn_retest_action(parent, i),
            )
            rt.grid(column=1, row=0, padx=5, pady=5)
            mf = tk.Button(
                vf,
                text="MORE INFO",
                padx=5,
                pady=3,
                command=lambda i=tid: self.btn_more_info_action(parent, i),
            )
            mf.grid(column=0, row=0)

        btn_next_test = tk.Button(
            self.viewingFrame,
            text="NEXT BOARD",
            font=("Arial", 15),
            command=lambda: self.btn_next_test_action(parent),
        )
        btn_next_test.grid(column=3, row=self.data_holder.getNumTests() + 3)

        logger.debug("Buttons finshed being created.")

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
            self.JSON_popup.attributes("-topmost", "true")

            # Creating a Frame For Console Output
            frm_JSON = tk.Frame(self.JSON_popup, width=500, height=300, bg="green")
            frm_JSON.pack_propagate(0)
            frm_JSON.pack()

            # Placing an entry box in the frm_console
            self.JSON_entry_box = tk.Text(
                frm_JSON, bg="#6e5e5d", fg="white", font=("Arial", 14)
            )
            self.JSON_entry_box.pack(anchor="center", fill=tk.BOTH, expand=1)

            current_JSON_file = open(JSON_String)
            current_JSON_data = json.load(current_JSON_file)

            temp = ""
            for key, value in current_JSON_data.items():
                temp = temp + "{} : {}".format(key, value) + "\n"

            self.JSON_entry_box.delete(1.0, "end")
            self.JSON_entry_box.insert(1.0, temp)

            current_JSON_file.close()
        except Exception as e:
            logger.debug(e)
            logger.warning(
                "TestSummaryScene: More Info popup has failed to be created."
            )

    #################################################

    # All of the different methods for what the retest buttons should do
    def btn_retest_action(self, _parent, test_idx):
        _parent.set_frame_test(test_idx)

    def btn_more_info_action(self, _parent, test_idx):
        names = self.data_holder.getTestNames()
        self.create_JSON_popup(
            "{}/JSONFiles/Current_{}_JSON.json".format(
                PythonFiles.__path__[0],
                names[test_idx].replace(" ", "").replace("/", ""),
            )
        )

    def btn_next_test_action(self, _parent):
        self.data_holder.data_holder_new_test()
        self.lbl_snum.destroy()
        _parent.reset_board()
        logger.info("Starting a new test.")

    def update_frame(self):
        self.create_updated_table(self.parent)

    def add_new_test(self, _list_of_completed_tests, _list_of_pass_fail):
        self.list_of_completed_tests = _list_of_completed_tests
        self.list_of_pass_fail = _list_of_pass_fail
