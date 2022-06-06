import tkinter as tk
from PIL import ImageTk as iTK
from PIL import Image
from matplotlib.pyplot import table
from pyparsing import col

class TestFinishedSummary(tk.Frame):
    def __init__(self, parent, master_window):
        super().__init__(master_window, width=850, height=500, background='coral')


        self.list_of_tests = ["General Resistance Test", "ID Resistor Test", "I2C Comm. Test", "Bit Rate Test"]
        self.list_of_table_labels = ["Test Name", "Test Status", "Pass/Fail"]
        self.list_of_completed_tests = [True, True, True, False]
        self.list_of_pass_fail = [True, False, True, False]



        # Adds the title to the TestSummary Frame
        self.title = tk.Entry(self,  width=13, fg='#0d0d0d',
                               font=('Arial',18,'bold'), justify='center')
        self.title.insert(tk.END, "Testing Finished!")
        self.title.grid(row= 0, column= 1)
        
        
        # Creates the "table" as a frame object
        self.table = tk.Frame(self, padx= 10, pady=7)
        self.table.grid(row = 1, column= 1)


        # Ensures the frame is the correct size
        self.grid_propagate(0)

    
        # Adds the labels to the top of the table
        for index in range(len(self.list_of_table_labels)):
            _entry= tk.Text(self.table, width=25, height=1, fg='green', font=('Arial',11))
            _entry.insert(tk.END, self.list_of_table_labels[index])
            _entry.tag_configure("center", justify='center')
            _entry.tag_add("center", 1.0, "end")
            _entry.grid(row= 0, column=index)
            



        # Adds the test names to the first column
        for index in range(len(self.list_of_tests)):
            _entry= tk.Text(self.table, width=25, height=5, fg='green', font=('Arial',11))
            _entry.insert(tk.END, self.list_of_tests[index])
            _entry.tag_configure("center", justify='center')
            _entry.tag_add("center", 1.0, "end")
            _entry.grid(row=index + 1, column=0)
            


        for index in range(len(self.list_of_completed_tests)):
            _entry= tk.Text(self.table, width=25, height=5, fg='green', font=('Arial',11))

            if (self.list_of_completed_tests[index]):
                _entry.insert(tk.END, "COMPLETED")
            else:
                _entry.insert(tk.END, "UNFINISHED")

            _entry.tag_configure("center", justify='center')
            _entry.tag_add("center", 1.0, "end")
            _entry.grid(row=index + 1, column=1)

            




        # Adds the Image as to whether the test was completed or not
        for index in range(len(self.list_of_pass_fail)):
            if(self.list_of_pass_fail[index]):
                # Create a photoimage object of the QR Code
                Green_Check_Image = Image.open("./PythonFiles/GreenCheckMark.png")
                Green_Check_Image = Green_Check_Image.resize((75,75), Image.ANTIALIAS)
                Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
                GreenCheck_Label = tk.Label(self.table, image=Green_Check_PhotoImage, width=75, height=75)
                GreenCheck_Label.image = Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + 1, column=2)

            else:
                # Create a photoimage object of the QR Code
                Red_X_Image = Image.open("./PythonFiles/RedX.png")
                Red_X_Image = Red_X_Image.resize((75,75), Image.ANTIALIAS)
                Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
                RedX_Label = tk.Label(self.table, image=Red_X_PhotoImage, width=75, height=75)
                RedX_Label.image = Red_X_PhotoImage

                RedX_Label.grid(row=index + 1, column=2)

        
        for index in range(len(self.list_of_tests)):
            retest_button = tk.Button(self.table, text="RETEST")
            retest_button.grid(row=index + 1, column=3)






    def add_new_test(self, _list_of_completed_tests, _list_of_pass_fail):
        self.list_of_completed_tests = _list_of_completed_tests
        self.list_of_pass_fail = _list_of_pass_fail


                
        


