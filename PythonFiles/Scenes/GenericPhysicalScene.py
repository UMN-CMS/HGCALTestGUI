import tkinter as tk
import tkinter.font as font


class GenericPhysicalScene(tk.Frame):
    def __init__(self, parent, master_frame, data_holder, test_id, test_config):
        super().__init__(master_frame, width=870, height=500)

        self.data_holder = data_holder

        self.test_id = test_id
        self.test_config = test_config
        self.fields = self.test_config["data_fields"]

        self.offset = 1
        self.values = {}
        self.update_frame(parent)

    def create_btn_from_cfg(self, data_field):
        font_scene = ("Arial", 12)
        font_scene_14 = ("Arial", 14)

        current_row = len(self.values.keys()) + self.offset

        if data_field["type"] == "float":
            lbl_tester = tk.Label(
                self.frm_window, text="{}: ".format(data_field["name"]), font=font_scene
            )
            lbl_tester.grid(row=current_row, column=1, pady=15)

            self.values[data_field["name"]] = tk.StringVar()

            ent_tester = tk.Entry(
                self.frm_window,
                font=font_scene,
                textvariable=self.values[data_field["name"]],
            )
            ent_tester.grid(row=current_row, column=2, pady=15)

        elif data_field["type"] == "bool":
            self.values[data_field["name"]] = tk.BooleanVar()

            c1 = tk.Checkbutton(
                self.frm_window,
                font=font_scene_14,
                text="{}:".format(data_field["name"]),
                variable=self.values[data_field["name"]],
                onvalue=1,
                offvalue=0
                # command=print_selection
            )
            c1.grid(row=current_row, column=1, pady=15)

    def update_frame(self, parent):
        # Creates a font to be more easily referenced later in the code
        font_scene = ("Arial", 12)
        font_scene_14 = ("Arial", 14)

        # Create a centralized window for information
        self.frm_window = tk.Frame(self, width=1105, height=650)
        self.frm_window.grid(column=0, row=0)

        # Create a label for the tester's name
        lbl_tester = tk.Label(
            self.frm_window,
            text=f"Tester: ",
            font=font_scene,
        )
        lbl_tester.grid(row=0, column=0, pady=15)

        # Create an entry for the tester's name
        ent_tester = tk.Entry(self.frm_window, font=font_scene)
        ent_tester.insert(0, self.data_holder.getActiveUser())
        ent_tester.grid(row=0, column=1, pady=15)
        ent_tester.config(state="disabled")

        # Create a label for the serial number box
        lbl_snum = tk.Label(
            self.frm_window,
            text=f"Serial Number: ",
            font=font_scene,
        )
        lbl_snum.grid(row=0, column=2, pady=15)

        # Create a entry for the serial number box
        ent_snum = tk.Entry(self.frm_window, font=font_scene)
        print(self.data_holder.getActiveSerial())
        ent_snum.insert(0, self.data_holder.getActiveSerial())
        ent_snum.grid(row=0, column=3, pady=15)
        ent_snum.config(state="disabled")

        for data_field in self.fields:
            self.create_btn_from_cfg(data_field)

        btn_confirm = tk.Button(
            self.frm_window,
            text="Confirm",
            relief=tk.RAISED,
            command=lambda: self.btn_confirm_action(parent),
        )
        btn_confirm.grid(row=9, column=1, pady=50)
        btn_confirm["font"] = font.Font(family="Arial", size=13)

        # Create frame for logout button
        nav_frame = tk.Frame(self)
        nav_frame.grid(column=1, row=0, sticky="ne", padx=5)

        # Create a rescan button
        btn_rescan = tk.Button(
            nav_frame,
            text="Change Boards",
            relief=tk.RAISED,
            command=lambda: self.btn_rescan_action(parent),
        )
        btn_rescan.pack(anchor="ne", pady=15)

        # Create a logout button
        btn_logout = tk.Button(
            nav_frame,
            text="Logout",
            relief=tk.RAISED,
            command=lambda: self.btn_logout_action(parent),
        )
        btn_logout.pack(anchor="se")

        # Creating the help button
        btn_help = tk.Button(
            nav_frame,
            relief=tk.RAISED,
            text="Help",
            command=lambda: self.help_action(parent),
        )
        btn_help.pack(anchor="s", padx=10, pady=10)

        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frm_window.grid_propagate(0)
        self.grid_propagate(0)

    # Rescan button takes the user back to scanning in a new board
    def btn_rescan_action(self, _parent):
        _parent.set_frame_scan_frame()

    # Back button action takes the user back to the scanning device
    def btn_back_action(self, _parent):
        pass

    def update_data_holder(self):
        values = {}
        passed = True
        for data_field in [x for x in self.fields if x["critical"]]:
            if data_field["type"] == "float":
                v = self.values[data_field["name"]].get()
                r = data_field["required_range"]
                passed &= float(r["max"]) >= float(v) and float(r["min"]) <= float(v)
                values[data_field["name"]] = v
            elif data_field["type"] == "bool":
                v = self.values[data_field["name"]].get()
                passed &= v
                values[data_field["name"]] = v
            if not passed:
                break
        test = self.data_holder.getTest(self.test_id)
        self.data_holder.updateTest(self.test_id, passed=passed, result=v)
        return passed

    #################################################

    # Confirm button action takes the user to the test in progress scene
    def btn_confirm_action(self, _parent):
        if self.update_data_holder():
            _parent.gotoNext()
        else:
            _parent.critical_failure_popup()

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

    #################################################

    # functionality for the logout button
    def btn_logout_action(self, _parent):
        _parent.gotoScene("login")

    #################################################

    def remove_widgets(self, _parent):
        for widget in self.winfo_children():
            widget.destroy()
