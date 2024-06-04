#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.font as font


#################################################################################


# Creating class for the window
class Inspection1(tk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
        super().__init__(master_frame, width = 1105, height = 850)

        self.test_name = "SOMETHING STRING"
        self.data_holder = data_holder
        
        self.update_frame(parent)

    #################################################

    def update_frame(self, parent):

        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 12)
        font_scene_14 = ('Arial', 14)

        # Create a centralized window for information
        frm_window = tk.Frame(self, width = 1105, height = 850)
        frm_window.grid(column=0, row=0)

        # Create a label for the tester's name
        lbl_tester = tk.Label(
            frm_window, 
            text = "Tester: ", 
            font = font_scene
            )
        lbl_tester.grid(row=0, column=0, pady=15 )

        # Create an entry for the tester's name
        ent_tester = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_tester.insert(0, self.data_holder.data_dict['user_ID'])
        ent_tester.grid(row=0, column=1, pady=15 )
        ent_tester.config(state = "disabled")

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            frm_window, 
            text = "Serial Number: ", 
            font = font_scene
            )
        lbl_snum.grid(row=0, column=2, pady=15 )

        # Create a entry for the serial number box
        ent_snum = tk.Entry(
            frm_window, 
            font = font_scene
            )
        ent_snum.insert(0, self.data_holder.data_dict['current_serial_ID'])
        ent_snum.grid(row=0, column=3, pady=15)
        ent_snum.config(state = "disabled")

        # TODO Index can change for different InspectionScenes
        inspection_index = 0
        check_dictionary = self.data_holder.get_check_dict(inspection_index)

        self.tk_bools = []

        if len(check_dictionary) > 0:
            for idx, item in enumerate(self.data_holder.get_check_dict(0)):
        
                new_bool = tk.BooleanVar()
                self.tk_bools.append(new_bool)
        
                # Checkbutton1
                c1 = tk.Checkbutton(
                    frm_window, 
                    font = font_scene_14,
                    text=item['text'],
                    variable= new_bool, 
                    onvalue= True, 
                    offvalue= False 
                    # command=print_selection
                    )
                c1.grid(row = 1 + idx, column= 1, sticky='w', columnspan=2)


        

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            frm_window, 
            text = "Comments:", 
            font = font_scene
            )
        lbl_snum.grid(row=5, column=1, pady=(25, 0) )

        # Comment Box
        self.comment_box = tk.Entry(
            frm_window,
            font = font_scene,
            state= 'normal',
            width= 75,
        )
        self.comment_box.grid(row = 6, column =1, sticky='w', columnspan=5)



    

        # Create a button for confirming test
        btn_confirm = tk.Button(
            frm_window, 
            text = "Confirm", 
            relief = tk.RAISED, 
            command = lambda:self.btn_confirm_action(parent)
            )
        btn_confirm.grid(row = 9, column= 1, pady= 50)
        btn_confirm['font'] = font.Font(family = 'Arial', size = 13)



        # Create frame for logout button
        nav_frame = tk.Frame(self)
        nav_frame.grid(column = 1, row = 0, sticky = 'ne', padx =5)


        # Create a rescan button
        btn_rescan = tk.Button(
            nav_frame, 
            text = "Change Boards", 
            relief = tk.RAISED, 
            command = lambda: self.btn_rescan_action(parent))
        btn_rescan.pack(anchor = 'ne', pady=15)

        # Create a logout button
        btn_logout = tk.Button(
            nav_frame, 
            text = "Logout", 
            relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'se')

        # Creating the help button
        btn_help = tk.Button(
            nav_frame,
            relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.pack(anchor = 's', padx = 10, pady = 10)



        
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        frm_window.grid_propagate(0)
        self.grid_propagate(0)
        
    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)


    ################################################# 

    #################################################

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.set_frame_scan_frame()

    #################################################

    # Back button action takes the user back to the scanning device
    def btn_back_action(self, _parent):
        pass
    
    #################################################

    # adds the visual inspection info to the data holder
    def update_data_holder(self):
        for i, items in enumerate(self.tk_bools):
            self.data_holder.get_check_dict(0)[i]['value'] = items.get()           
 
        self.data_holder.set_comment_dict(0, self.comment_box.get())  
        self.data_holder.add_inspection_to_comments()
        self.data_holder.update_from_json_string()
        self.data_holder.print()


    #################################################

    # Confirm button action takes the user to the camera scene scene
    def btn_confirm_action(self, _parent):
        
        self.update_data_holder()
        _parent.first_frame_camera_frame()


    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        _parent.set_frame_login_frame()

    #################################################


    def remove_widgets(self, _parent):
        for widget in self.winfo_children():
            widget.destroy()



