import multiprocessing as mp
import logging, time, sys, os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from PIL import ImageTk as iTK
from PIL import Image
import PythonFiles
from pathlib import Path
import yaml
import requests
import json

logger = logging.getLogger('HGCAL_VI.PythonFiles.Scenes.EconScanScene')


class EconScanScene(ttk.Frame):

    def __init__(self, parent, master_frame, data_holder, gui_cfg, board_id=None):
        self.data_holder = data_holder
        self.db_url = gui_cfg.getDBInfo("baseURL")
        # Load boards config
        with open(Path(__file__).parent.parent / "Data/hd_wagon_econ_configs.yaml", "r") as f:
            self.boards_config = yaml.safe_load(f)['boards']

        self.board_id = board_id
        self.board_image_path = None
        self.component_config = []
        self.current_index = 0
        self.scanned_components = {}
        self.comments = []
        self.results = {}
        self.passed_test = True
        self.EXIT_CODE = 0



        self.master_frame = master_frame
        self.parent = parent

        self.create_style(parent)
        super().__init__(self.master_frame, width=1300-213, height=800)

        self.initialize_GUI(parent, master_frame)

    #################################################

    def create_style(self, _parent):
        self.s = ttk.Style()
        self.s.tk.call('lappend', 'auto_path', f'{_parent.main_path}/../awthemes-10.4.0')
        self.s.tk.call('lappend', 'auto_path', f'{_parent.main_path}/awthemes-10.4.0')
        self.s.tk.call('package', 'require', 'awdark')
        self.s.theme_use('awdark')

    #################################################

    def initialize_GUI(self, parent, master_frame):
        """Set up the scanning GUI with left panel (progress + scanned Entry + buttons)
        and right panel (board + component images)."""
    
        self.grid(column=0, row=0, sticky="nsew")
        master_frame.grid_rowconfigure(0, weight=1)
        master_frame.grid_columnconfigure(0, weight=1)
    
        # === Grid layout ===
        self.grid_columnconfigure(0, weight=1)  # left panel
        self.grid_columnconfigure(1, weight=3)  # right panel
        self.grid_rowconfigure(0, weight=1)
    
        # --- Left panel ---
        self.left_panel = ttk.Frame(self)
        self.left_panel.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(3, weight=1)  # expandable filler
    
        # Progress label
        self.lbl_progress = ttk.Label(
            self.left_panel, font=("Arial", 24), anchor="center"
        )
        self.lbl_progress.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    
        # Editable scanned Entry
        self.scanned_label_var = tk.StringVar(value="")
        self.scanned_entry = ttk.Entry(
            self.left_panel,
            textvariable=self.scanned_label_var,
            font=("Arial", 20),
            justify="center",
            state="normal"
        )
        self.scanned_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))
    
        # Bind Enter key to submit typed value
        self.scanned_entry.bind("<Return>", lambda event: self.manual_next_component())
    
        # Trace changes to update dictionary in real time
        def _on_scanned_entry_change(*args):
            if self.current_index < len(self.component_config):
                component_name = self.component_config[self.current_index]["name"]
                self.scanned_components[component_name] = self.scanned_label_var.get()
        self.scanned_label_var.trace_add("write", _on_scanned_entry_change)
    
        # Next button (manual input)
        self.btn_next = ttk.Button(
            self.left_panel, text="Next", command=self.manual_next_component
        )
        self.btn_next.grid(row=2, column=0, sticky="ew", pady=(0, 20))
    
        # --- Bottom buttons frame ---
        self.left_buttons_frame = ttk.Frame(self.left_panel)
        self.left_buttons_frame.grid(row=4, column=0, sticky="ew", pady=10)
        for i in range(4):
            self.left_buttons_frame.grid_columnconfigure(i, weight=1)
    
        # Cancel button
        self.btn_cancel = ttk.Button(
            self.left_buttons_frame, text="Cancel",
            command=lambda: self.btn_submit_action(parent)
        )
        self.btn_cancel.grid(row=0, column=0, sticky="ew", padx=5)
    
        # Submit button
        self.btn_submit = ttk.Button(
            self.left_buttons_frame, text="Submit", command=lambda: self.btn_submit_action(parent), state="disabled"
        )
        self.btn_submit.grid(row=0, column=1, sticky="ew", padx=5)
    
        # Logout button
        self.btn_logout = ttk.Button(
            self.left_buttons_frame, text="Logout",
            command=lambda: self.btn_logout_action(parent)
        )
        self.btn_logout.grid(row=0, column=2, sticky="ew", padx=5)
    
        # Help button
        self.btn_help = ttk.Button(
            self.left_buttons_frame, text="Help",
            command=lambda: self.help_action(parent)
        )
        self.btn_help.grid(row=0, column=3, sticky="ew", padx=5)
    
        # --- Right panel ---
        self.right_panel = ttk.Frame(self)
        self.right_panel.grid(column=1, row=0, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(0, weight=3)  # board image
        self.right_panel.grid_rowconfigure(1, weight=1)  # component image
        self.right_panel.grid_columnconfigure(0, weight=1)
    
        # Board image (top)
        self.board_frame = ttk.Frame(self.right_panel)
        self.board_frame.grid(row=0, column=0, sticky="nsew")
        self.board_frame.grid_rowconfigure(0, weight=1)
        self.board_frame.grid_columnconfigure(0, weight=1)
        self.lbl_board = ttk.Label(self.board_frame)
        self.lbl_board.grid(row=0, column=0, sticky="nsew")
    
        # Component image (bottom)
        self.location_img_label = ttk.Label(self.right_panel)
        self.location_img_label.grid(row=1, column=0, sticky="nsew", pady=10)
    
        # Prevent grid from shrinking widgets
        self.grid_propagate(False)

    ################################################

    def update_component_prompt(self):
        if not self.component_config:
            # No board loaded yet
            self.lbl_progress["text"] = "No board selected"
            self.location_img_label.configure(image=None)
            self.scanned_label_var.set("Not scanned")
            return
    
        component = self.component_config[self.current_index]
    
        self.lbl_progress["text"] = (
            f"Scan component {self.current_index + 1} of {len(self.component_config)}\n"
            f"{component['name']}"
        )

        self.scanned_label_var.set("")

        MAX_LOC_WIDTH = 200
        MAX_LOC_HEIGHT = 200
        comp_img_path = Path(__file__).parent.parent / f'Data/{component["image"]}'
        img = Image.open(comp_img_path)
        img.thumbnail((MAX_LOC_WIDTH, MAX_LOC_HEIGHT), Image.Resampling.LANCZOS)
        photo = iTK.PhotoImage(img)
        self.location_img_label.configure(image=photo)
        self.location_img_label.image = photo

    ################################################

    def scan_QR_code(self, master_window):

        if not hasattr(self, 'master_window'):
            self.master_window = master_window

        sys.path.insert(1, '/home/hgcal/WagonTest/Scanner/python')
        from ..Scanner.python.get_barcodes import scan, listen, parse_xml

        manager = mp.Manager()
        self.full_id = manager.list()

        self.scanner = scan(self.parent.main_path)
        self.listener = mp.Process(target=listen, args=(self.full_id, self.scanner))
        self.listener.start()

        # Start non-blocking polling
        self.after(10, self._poll_scanner)

    #################################################

    def _poll_scanner(self):
        from ..Scanner.python.get_barcodes import parse_xml

        if len(self.full_id) > 0:
            label = parse_xml(self.full_id[0])

            # Stop scanner processes
            try:
                self.listener.terminate()
                self.scanner.terminate()
            except:
                pass

            # Store scanned component
            component_name = self.component_config[self.current_index]["name"]
            self.scanned_components[component_name] = label
            self.scanned_label_var.set(label)
            # Move to next component
            self.current_index += 1
            if self.current_index < len(self.component_config):
                self.update_component_prompt()
                # Start scanning next component
                self.scan_QR_code(self.master_window)
            else:
                self.on_all_components_scanned()
        elif self.EXIT_CODE:
            try:
                self.listener.terminate()
                self.scanner.terminate()
            except:
                pass
        else:
            # Poll again in 10 ms
            self.after(10, self._poll_scanner)

    #################################################

    def on_all_components_scanned(self):
        self.check_grade() 
        #print(self.passed_test)
        #print(self.comments)
        #print(self.results)
        output_str = "All components scanned.\n"
        
        for name, label in self.scanned_components.items():
            #self.data_holder.add_component(name, label)
            output_str += f'{name}: {label}\n'
        output_str += self.comments
        
        self.info_dict = {
            "full_id": self.full_board_id,
            "tester": self.data_holder.data_dict['user_ID'], 
            "test_type": "ECON Scan",
            "successful": int(self.passed_test), 
            "comments": self.comments}

        #self.data = {
        #        "test_data": self.data,
        #        "test_criteria": self.test_criteria or False,
        #}

        #self.results = {
        #        "name": self.name,
        #        "board_sn": self.board_sn,
        #        "tester": self.tester,
        #        "pass": self.passed,
        #        "data": self.data,
        #        "comments": str(self.comments),
        #}

        #self.scanned_entry.grid_remove()
        #self.btn_next.grid_remove()

        self.lbl_progress["text"] = output_str
        self.btn_submit["state"] = "active"

    #################################################

    def btn_submit_action(self, _parent):
        self.EXIT_CODE = 1
        r = requests.post('{}/add_test_json.py'.format(self.db_url), data = self.info_dict, files = {'attach1': json.dumps(self.results)})

        if self.data_holder.data_dict['prev_results'] != '':
            self.data_holder.check_if_new_board()
            _parent.set_frame_postscan()
        else:
            self.data_holder.check_if_new_board()
            parent.set_frame_inspection_frame()
        self.EXIT_CODE = 0

    #################################################

    def btn_logout_action(self, _parent):
        self.EXIT_CODE = 1
        try:
            self.listener.terminate()
            self.scanner.terminate()
        except:
            pass
        _parent.set_frame_login_frame()

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)

    #################################################

    def load_board(self):
        self.full_board_id = str(self.data_holder.data_dict['current_full_ID'])
        self.board_id = self.full_board_id[3:9]
        if self.board_id not in self.boards_config:
            raise ValueError(f"Board ID {board_id} not found in config")
        board_data = self.boards_config[self.board_id]
        self.board_image_path = board_data['board_image']
        self.board_image_path = Path(__file__).parent.parent / f'Data/{self.board_image_path}'
        self.component_config = board_data['components']
    
        self.current_index = 0
        self.scanned_components = {}
    
        # Load board image
        if hasattr(self, 'lbl_board'):
            self.load_and_scale_board_image(self.board_image_path) 
        self.update_component_prompt()

    def load_and_scale_board_image(self, image_path):
        self.board_frame.update_idletasks() 
        frame_width = self.board_frame.winfo_width()
        frame_height = self.board_frame.winfo_height()
    
        # If not ready yet, try again shortly
        if frame_width <= 1 or frame_height <= 1:
            self.after(50, lambda: self.load_and_scale_board_image(image_path))
            return
    
        img = Image.open(image_path)
    
        # Calculate scale factor to fit inside frame while keeping aspect ratio
        img_ratio = img.width / img.height
        frame_ratio = frame_width / frame_height
    
        if img_ratio > frame_ratio:
            new_width = frame_width
            new_height = int(frame_width / img_ratio)
        else:
            new_height = frame_height
            new_width = int(frame_height * img_ratio)
        
        new_width = max(100, new_width)
        new_height = max(100, new_height)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = iTK.PhotoImage(img)
    
        # Update label
        self.lbl_board.configure(image=photo)
        self.lbl_board.image = photo

    def manual_next_component(self):
        if self.current_index >= len(self.component_config):
            return
    
        # Get value from Entry
        value = self.scanned_label_var.get().strip()
        if not value:
            # Optionally, warn the user they must type something
            self.scanned_label_var.set("Please enter a value")
            time.sleep(2)
            self.scanned_label_var.set("")
            return
    
        # Store value
        component_name = self.component_config[self.current_index]["name"]
        self.scanned_components[component_name] = value
    
        # Move to next component
        self.current_index += 1
        if self.current_index < len(self.component_config):
            self.update_component_prompt()  # reset component image & Entry
        else:
            self.on_all_components_scanned()

    def check_grade(self):
        econ_grade_map = {
            2: {"BA": "BA", "DD": "DD", "FF": "FF"},
            3: {"AA": "AAA", "BA": "BAA", "AB": "BAB", "BB": "BBB", "DB": "DBB", "42": "DDB", "DD": "DDD", "FD": "FDD", "FF": "FFF"},
            4: {"AA": "AAAA", "BA": "BAAA", "DB": "DDBB", "DD": "DDDD", "64": "FDDD", "FD": "FFDD"},
        }
        num_modules = int(self.full_board_id[5])+int(self.full_board_id[6])
        correct_grades = self.full_board_id[9:11] 
        self.passed_test = True
        for key, value in self.scanned_components.items():
            self.results[key] = dict()
            self.results[key]["full_id"] = value  
            module_num = int(key[-1]) - 1
            scanned_grade = value[8]
            correct_grade = econ_grade_map[num_modules][correct_grades][module_num]
            self.results[key]["Correct Grade"] = correct_grade 
            self.results[key]["Scanned Grade"] = scanned_grade
            if scanned_grade != correct_grade:
                self.results[key]["Passed"] = False
                self.comments.append(f"\n{key} should be grade {correct_grade},\nbut scanned as grade {scanned_grade}.")
            else:
                self.results[key]["Passed"] = True 
        for key in self.results.keys():
            self.passed_test = self.passed_test and self.results[key]["Passed"] 
        if self.passed_test:
            self.comments = "All grades correct."
        else:
            self.comments.append("\nPlease finish checking in and then\nplace in failed bin.")
            self.comments = "\n".join(self.comments)

