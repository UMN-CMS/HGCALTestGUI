#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.font as font


#################################################################################


# Creating class for the window
class Inspection1(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder, test_idx):
        super().__init__(master_frame, width=870, height=500)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        self.test_name = "SOMETHING STRING"
        self.data_holder = data_holder
        
        self.test_idx = test_idx
        self.parent = parent
        self.update_frame(parent)

    #################################################

    def update_frame(self, parent):

        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 12)
        font_scene_14 = ('Arial', 14)

        # Create a centralized window for information
        frm_window = tk.Frame(self, width = 1105, height = 650)
        frm_window.grid(column=0, row=0, sticky='new')
        
        frm_window.grid_rowconfigure(0, weight=1)
        frm_window.grid_columnconfigure(0, weight=1)

        # Create a label for the tester's name
        lbl_tester = tk.Label(
            frm_window, 
            text = "Tester: ", 
            font = font_scene
            )
        lbl_tester.grid(row=0, column=0, pady=15, sticky='we')

        # Create an entry for the tester's name
        ent_tester = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_tester.insert(0, self.data_holder.data_dict['user_ID'])
        ent_tester.grid(row=0, column=1, pady=15, sticky='we')
        ent_tester.config(state = "disabled")

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            frm_window, 
            text = "Serial Number: ", 
            font = font_scene
            )
        lbl_snum.grid(row=0, column=2, pady=15, sticky='we')

        # Create a entry for the serial number box
        ent_snum = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_snum.insert(0, self.data_holder.data_dict['current_full_ID'])
        ent_snum.grid(row=0, column=3, pady=15, sticky='we')
        ent_snum.config(state = "disabled")


        self.board_chipped_bent = tk.BooleanVar()
        self.wagon_connection_pin_bent = tk.BooleanVar()
        self.engine_connection_pin_bent = tk.BooleanVar()
        self.visual_scratches = tk.BooleanVar()
        


        # Beginning of the CheckButtons
        
        # Checkbutton1
        c1 = tk.Checkbutton(
            frm_window, 
            font = font_scene_14,
            text='Board Chipped/Bent',
            variable= self.board_chipped_bent, 
            onvalue=1, 
            offvalue=0 
            # command=print_selection
            )
        c1.grid(row = 1, column= 1, sticky='w', columnspan=2)
        
        # Checkbutton2
        c2 = tk.Checkbutton(
            frm_window, 
            font = font_scene_14,
            text='Wagon Connection Pin Bent',
            variable= self.wagon_connection_pin_bent, 
            onvalue=True, 
            offvalue=False 
            # command=print_selection
            )
        c2.grid(row = 2, column= 1, sticky='w', columnspan=2)

        # Checkbutton3
        c3 = tk.Checkbutton(
            frm_window, 
            font = font_scene_14,
            text='Engine Connection Pin Bent',
            variable= self.engine_connection_pin_bent, 
            onvalue=True, 
            offvalue=False 
            # command=print_selection
            )
        c3.grid(row = 3, column= 1, sticky='w', columnspan=2)

        # Checkbutton4
        c4 = tk.Checkbutton(
            frm_window, 
            font = font_scene_14,
            text='Visual Scratches',
            variable= self.visual_scratches, 
            onvalue=True, 
            offvalue=False 
            # command=print_selection
        )
        c4.grid(row = 4, column= 1, sticky='w', columnspan=2)


        

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            frm_window, 
            text = "Comments:", 
            font = font_scene
            )
        lbl_snum.grid(row=5, column=0, pady=10, sticky='w')

        # Comment Box
        self.comment_box = tk.Entry(
            frm_window,
            font = font_scene,
            state= 'normal',
            width= 75,
        )
        self.comment_box.grid(row = 6, column =0, sticky='we', columnspan=5, padx=10)



    

        # Create a button for confirming test
        btn_confirm = tk.Button(
            frm_window, 
            text = "Confirm", 
            relief = tk.RAISED, 
            command = lambda:self.btn_confirm_action(parent)
            )
        btn_confirm.grid(row = 9, column= 0, pady= 20, padx=10)


        # Create a rescan button
        btn_rescan = tk.Button(
            frm_window, 
            text = "Change Boards", 
            relief = tk.RAISED, 
            command = lambda: self.btn_rescan_action(parent))
        btn_rescan.grid(row = 9, column= 1, pady= 20, padx=10)


        # Create a logout button
        btn_logout = tk.Button(
            frm_window,
            text = "Logout", 
            relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.grid(row = 9, column= 2, pady= 20, padx=10)


        # Creating the help button
        btn_help = tk.Button(
            frm_window,
            relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.grid(row = 9, column= 3, pady= 20, padx=10)


        # # # # # # # # # 

        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        frm_window.grid_columnconfigure(0, weight=1)
        frm_window.grid_columnconfigure(1, weight=1)
        frm_window.grid_columnconfigure(2, weight=1)
        frm_window.grid_columnconfigure(3, weight=1)


        
    #################################################

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.set_frame_scan_frame()

    #################################################

    # Back button action takes the user back to the scanning device
    def btn_back_action(self, _parent):
        pass
    
    #################################################

    def update_data_holder(self):
            
        # Automatically passes the physical tests after completion
        self.data_holder.data_lists['physical_results'][self.test_idx] = True

        self.data_holder.inspection_data['board_chipped_bent'] = self.board_chipped_bent.get()
        self.data_holder.inspection_data['wagon_connection_pin_bent'] = self.wagon_connection_pin_bent.get()
        self.data_holder.inspection_data['engine_connection_pin_bent'] = self.engine_connection_pin_bent.get()
        self.data_holder.inspection_data['visual_scratches'] = self.visual_scratches.get()
        self.data_holder.inspection_data['inspection_comments'] = self.comment_box.get()
        self.data_holder.add_inspection_to_comments()
        self.data_holder.print()


    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        
        self.update_data_holder()
        
        _parent.go_to_next_test()
        
        
    
        # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #   ++ GOAL CODE ++                                 #
        # def confirm():                                    #
        #       set_frame_TIPS()                            #
        #       Runs_Test()   # Might include multithread   #
        #       Get_Results()                               #
        #       Update_Dataholder()                         #
        #       Go_To_Next_Test()                           #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # 
        pass
    def get_submit_action(self):
        return self.btn_confirm_action

    def get_parent(self):
        return self.parent

        
    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        _parent.set_frame_login_frame()

    #################################################


    def remove_widgets(self, _parent):
        for widget in self.winfo_children():
            widget.destroy()



