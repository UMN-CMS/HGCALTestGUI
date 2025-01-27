#################################################################################

# Importing Necessary Modules
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font


#################################################################################


# Creating class for the window
class Inspection1(ttk.Frame):

    #################################################

    def __init__(self, parent, master_frame, data_holder):
        super().__init__(master_frame, width = 1105, height = 850)
        
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)

        self.test_name = "SOMETHING STRING"
        self.data_holder = data_holder
        self.create_style(parent)
        self.update_frame(parent)
        self.parent = parent

    #################################################

    def create_style(self, _parent):

        self.s = ttk.Style()

        self.s.tk.call('lappend', 'auto_path', '{}/../awthemes-10.4.0'.format(_parent.main_path))
        self.s.tk.call('package', 'require', 'awdark')

        self.s.theme_use('awdark') 

    def update_frame(self, parent):

        # Creates a font to be more easily referenced later in the code
        font_scene = ('Arial', 12)
        font_scene_14 = ('Arial', 14)

        # Create a centralized window for information
        frm_window = ttk.Frame(self, width = 1105, height = 850)
        frm_window.grid(column=0, row=0, sticky = 'n')
        
        frm_window.grid_rowconfigure(0, weight=1)
        frm_window.grid_columnconfigure(0, weight=1)

        # Create a label for the tester's name
        lbl_tester = ttk.Label(
            frm_window, 
            text = "Tester: ", 
            font = ('Arial', '26')
            )
        lbl_tester.grid(row=0, column=1,sticky = 'nw', pady=15 , padx = 20)

        # Create an entry for the tester's name
        ent_tester = tk.Entry(
            frm_window, 
            #font = font_scene
            )
        ent_tester.insert(0, self.data_holder.data_dict['user_ID'])
        ent_tester.grid(row=0, column=2, sticky = 'nw', pady=25 )
        ent_tester.config(state = "disabled")

        # Create a label for the full id box
        lbl_full = ttk.Label(
            frm_window, 
            text = "Full ID: ", 
            font = ('Arial', '26')
            )
        lbl_full.grid(row=0, column=3, pady=10, padx = 20, sticky = 'nw')

        # Create a entry for the full id box
        ent_full = tk.Entry(
            frm_window, 
            #font = font_scene
            )
        ent_full.insert(0, self.data_holder.data_dict['current_full_ID'])
        ent_full.grid(pady=25, row = 0, column = 4, sticky = 'nw')
        ent_full.config(state = "disabled")

         # Create a centralized window for information
        frm_Q = ttk.Frame(self)
        frm_Q.grid(column=0, row=0, sticky = 'n', pady = (200,0))
        frm_Q.grid_rowconfigure(0, weight=1)
        frm_Q.grid_columnconfigure(0, weight=1)


        # TODO Index can change for different InspectionScenes
        inspection_index = 0
        check_dictionary = self.data_holder.get_check_dict(inspection_index)

        self.tk_bools = []
        self.s.configure('TCheckbutton', font = ('Arial','36'))
        
        if len(check_dictionary) > 0:
            for idx, item in enumerate(self.data_holder.get_check_dict(0)):
        
                new_bool = tk.BooleanVar()
                self.tk_bools.append(new_bool)

                # Checkbutton1
                c1 = ttk.Checkbutton(
                    frm_Q, 
                    text=item['text'],
                    variable= new_bool, 
                    onvalue= True, 
                    offvalue= False,
                    style = 'TCheckbutton'
                    # command=print_selection
                    )
                c1.grid( row = 1 + idx, column= 2, sticky = 'nw', columnspan=2)

        lbl_comm = ttk.Label(
            frm_window, 
            text = "Comments:", 
            #font = font_scene
            )
        lbl_comm.grid(row=0, column=1, pady= (75,0) )
        lbl_comm.config(font = ('Arial', '24'))

        # Comment Box
        self.comment_box = tk.Entry(
            frm_window,
            #font = font_scene,
            state= 'normal',
            width= 75,
        )
        self.comment_box.grid(row = 1, column =1,  columnspan=5)



    

        # Create a button for confirming test
        btn_confirm = ttk.Button(
            frm_window, 
            text = "Confirm", 
            #relief = tk.RAISED, 
            command = lambda:self.btn_confirm_action(parent)
            )
        btn_confirm.grid(row = 5, column= 2, pady= 35, sticky = 's')
        #btn_confirm['font'] = font.Font(family = 'Arial', size = 13)



        # Create frame for logout button
        nav_frame = ttk.Frame(self)
        nav_frame.grid(column = 1, row = 0, sticky = 'se', padx =5)


        # Create a rescan button
        btn_rescan = ttk.Button(
            nav_frame, 
            text = "Change Boards", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_rescan_action(parent))
        btn_rescan.pack(anchor = 'se', pady=15)

        # Create a logout button
        btn_logout = ttk.Button(
            nav_frame, 
            text = "Logout", 
            #relief = tk.RAISED, 
            command = lambda: self.btn_logout_action(parent))
        btn_logout.pack(anchor = 'se')

        # Creating the help button
        btn_help = ttk.Button(
            nav_frame,
            #relief = tk.RAISED,
            text = "Help",
            command = lambda: self.help_action(parent)
        )
        btn_help.pack(anchor = 'se', pady = 10)



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

    def btn_confirm_action(self, _parent):
        
        self.update_data_holder()
        _parent.set_frame_summary()

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



