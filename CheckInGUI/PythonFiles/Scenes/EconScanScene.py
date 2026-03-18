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
        self.all_scanned = False 
        self.warned = False
        self.last_warnings = []
        self.is_rescanning = False

        self.econ_grade_map = {
            2: {"BA": "BA", "DD": "DD", "FF": "FF"},
            3: {"AA": "AAA", "BA": "BAA", "AB": "BAB", "BB": "BBB", "DB": "DBB", "42": "DDB", "DD": "DDD", "FD": "FDD", "FF": "FFF"},
            4: {"AA": "AAAA", "BA": "BAAA", "DB": "DDBB", "DD": "DDDD", "64": "FDDD", "FD": "FFDD"},
        }

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
        self.grid_columnconfigure(1, weight=2)  # right panel
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
            command=lambda: self.btn_cancel_action(parent)
        )
        self.btn_cancel.grid(row=0, column=0, sticky="ew", padx=5)
    
        # Submit button
        self.btn_submit = ttk.Button(
            self.left_buttons_frame, text="Submit", command=lambda: self.btn_submit_action(parent), state="disabled"
        )
        self.btn_submit.grid(row=0, column=1, sticky="ew", padx=5)
   
        #Rescan dropbox/button
        self.rescan_frame = ttk.Frame(self.left_panel)
        self.rescan_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.rescan_frame.grid_columnconfigure(0, weight=1)
        self.rescan_frame.grid_remove()
        
        self.btn_rescan = ttk.Button(
            self.rescan_frame, text="Rescan Selected", command=self.rescan_component
        )
        self.btn_rescan.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.rescan_var = tk.StringVar()
        self.rescan_dropdown = ttk.Combobox(
            self.rescan_frame, textvariable=self.rescan_var, state="readonly", font=("Arial", 14)
        )
        self.rescan_dropdown.grid(row=1, column=0, sticky="ew")
    
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
       

        # Right panel
        self.right_panel = ttk.Frame(self)
        self.right_panel.grid(column=1, row=0, sticky="nsew", padx=10, pady=10)
        
        self.board_frame = ttk.Frame(self.right_panel)
        self.board_frame.pack(expand=True, fill="both")
        
        self.lbl_board = ttk.Label(self.board_frame)
        self.lbl_board.pack(expand=True)

    def update_component_prompt(self):
        if not self.component_config:
            # No board loaded yet
            self.lbl_progress["text"] = "No board selected"
            self.scanned_label_var.set("Not scanned")
            return
            
        component = self.component_config[self.current_index]
        
        self.lbl_progress["text"] = (
            f"Scan component {self.current_index + 1} of {len(self.component_config)}\n"
            f"{component['name']}"
        )

        self.scanned_label_var.set("")
        self.get_component_image()

    ################################################

    def scan_QR_code(self):

        sys.path.insert(1, '/home/hgcal/WagonTest/Scanner/python')
        from ..Scanner.python.get_barcodes import scan, listen, parse_xml

        manager = mp.Manager()
        self.full_id = manager.list()

        self.scanned_entry["state"] = 'active'
        self.btn_next["state"] = 'active'

        try:
            self.listener.terminate()
            self.scanner.terminate()
        except:
            pass
        
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
            del self.full_id[:] 
            try:
                self.listener.terminate()
                self.scanner.terminate()
            except:
                pass
            self.scanned_label_var.set(label)
            self.advance_component(label)

        elif self.EXIT_CODE:
            try:
                self.listener.terminate()
                self.scanner.terminate()
            except:
                pass
        else:
            self.after(10, self._poll_scanner)

    #################################################

    def on_all_components_scanned(self):
        self.check_grade() 
        output_str = "All components scanned.\n"
        self.scanned_label_var.set("")

        for name, label in self.scanned_components.items():
            #self.data_holder.add_component(name, label)
            output_str += f'{name}: {label}\n'
        output_str += self.comments
        if not self.passed_test:
            output_str += "\nPlease finish checking in board.\nThen, place in failed bin and notify an expert."
        
        self.info_dict = {
            "full_id": self.full_board_id,
            "tester": self.data_holder.data_dict['user_ID'], 
            "test_type": "ECON Scan",
            "successful": int(self.passed_test), 
            "comments": self.comments}

        self.scanned_entry.grid_remove() 
        self.btn_next.grid_remove()
        
        component_names = [c["name"] for c in self.component_config]
        self.rescan_dropdown["values"] = component_names
        self.rescan_var.set(component_names[0])
        self.rescan_frame.grid()

        self.lbl_progress["text"] = output_str
        self.btn_submit["state"] = "active"
        self.all_scanned = True

    def rescan_component(self):
        selected = self.rescan_var.get()
        if not selected:
            return
    
        component_names = [c["name"] for c in self.component_config]
        self.current_index = component_names.index(selected)
        self.is_rescanning = True
    
        self.rescan_frame.grid_remove()
        self.btn_submit["state"] = "disabled"
        self.all_scanned = False
        self.scanned_entry.grid()
        self.btn_next.grid()
    
        self.update_component_prompt()
        self.scan_QR_code()

    #################################################

    def btn_submit_action(self, _parent):
        if not self.all_scanned:
            self.manual_next_component()
            return
        self.EXIT_CODE = 1
        print(self.info_dict)
        print(self.results)
        r = requests.post('{}/add_test_json.py'.format(self.db_url), data = self.info_dict, files = {'attach1': json.dumps(self.results)})
         
        self.btn_submit["state"] = "disabled"

        self.component_config = []
        self.current_index = 0
        self.scanned_components = {}
        self.comments = []
        self.results = {}
        self.passed_test = True
        self.all_scanned = False 
        self.warned = False
        self.last_warnings = []
        self.is_rescanning = False

        if self.data_holder.data_dict['prev_results'] != '':
            self.data_holder.check_if_new_board()
            _parent.set_frame_postscan()
        else:
            self.data_holder.check_if_new_board()
            _parent.set_frame_inspection_frame()

        self.scanned_entry.grid() 
        self.btn_next.grid()
        self.rescan_frame.grid_remove()

        self.EXIT_CODE = 0

    #################################################

    def btn_logout_action(self, _parent):
        self.EXIT_CODE = 1
        self.scanned_entry["state"] = "active"
        self.btn_next["state"] = "active"

        self.btn_submit["state"] = "disabled"

        self.component_config = []
        self.current_index = 0
        self.scanned_components = {}
        self.comments = []
        self.results = {}
        self.passed_test = True
        self.all_scanned = False
        self.warned = False
        self.last_warnings = []
        self.is_rescanning = False

        self.scanned_entry.grid() 
        self.btn_next.grid()
        self.rescan_frame.grid_remove()

        _parent.set_frame_login_frame()
        self.EXIT_CODE = 0

    
    def btn_cancel_action(self, _parent):

        self.EXIT_CODE = 1
        self.scanned_entry["state"] = "active"
        self.btn_next["state"] = "active"
        self.btn_submit["state"] = "disabled"

        self.component_config = []
        self.current_index = 0
        self.scanned_components = {}
        self.comments = []
        self.results = {}
        self.passed_test = True
        self.all_scanned = False
        self.warned = False
        self.last_warnings = []
        self.is_rescanning = False

        self.scanned_entry.grid() 
        self.btn_next.grid()
        self.rescan_frame.grid_remove()

        _parent.set_frame_scan_frame()
        self.EXIT_CODE = 0

    #################################################

    def help_action(self, _parent):
        _parent.help_popup(self)

    #################################################

    def load_board(self):
        self.full_board_id = str(self.data_holder.data_dict['current_full_ID'])
        self.board_id = self.full_board_id[3:9]
        if self.board_id not in self.boards_config:
            raise ValueError(f"Board ID {board_id} not found in config")
        self.component_config = self.boards_config[self.board_id]['components']
        self.current_index = 0
        self.scanned_components = {}
        self.update_component_prompt()
    
    def get_component_image(self):
        self.board_image_path = self.boards_config[self.board_id]['components'][self.current_index]['image']
        try:
            self.board_image_path = Path(__file__).parent.parent / f'Data/{self.board_image_path}'
            if hasattr(self, 'lbl_board'):
                self.load_and_scale_board_image(self.board_image_path) 
        except:
            print(f"No image {self.board_image_path}. Using default.")
            self.board_image_path = Path(__file__).parent.parent / f'Data/boards/missing.jpg'
            if hasattr(self, 'lbl_board'):
                self.load_and_scale_board_image(self.board_image_path) 

    def load_and_scale_board_image(self, image_path):
        img = Image.open(image_path)
        
        target_width, target_height = 650, 879
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = iTK.PhotoImage(img)

        self.lbl_board.config(image=photo)
        self.lbl_board.image = photo
        self.board_frame.update()

    def manual_next_component(self):
        value = self.scanned_label_var.get().strip()
        if not value:
            self.scanned_label_var.set("Please enter a value")
            self.scanned_entry.update()
            time.sleep(2)
            self.scanned_label_var.set("")
            return

        self.advance_component(value, scanned=False)

    def advance_component(self, value, scanned = True):
        self.EXIT_CODE = 0
        component_name = self.component_config[self.current_index]["name"]

        if self.is_rescanning:
            self.scanned_components[component_name] = None 
        current_values = list(self.scanned_components.values())

        if scanned:
            self.scanned_entry["state"] = "disabled"
            self.btn_next["state"] = "disabled"

        if value in current_values:
            self.lbl_progress["text"] = (f"ID already scanned\n" 
                f"Please double-check and rescan.")

            self.scanned_entry["state"] = "normal"
            self.btn_next["state"] = "normal"
            self.scan_QR_code()
            return

        pass_id_check, warnings = self.check_id(value, component_name)  
        if (not pass_id_check) and (warnings != self.last_warnings):
            self.last_warnings = warnings 
            self.lbl_progress["text"] = (f"{warnings}\n" 
                f"Please double-check and rescan.\n"
                f"If you are sure you have scanned\nthe correct ECON, hit next."
            )

            self.scanned_entry["state"] = "normal"
            self.btn_next["state"] = "normal"
            self.scan_QR_code()
            return
        
        if scanned:
            self.lbl_progress["text"] = "Good scan"
            self.lbl_progress.update()
            time.sleep(1)

        self.scanned_components[component_name] = value
        self.current_index += 1
        if self.is_rescanning:
            self.is_rescanning = False
            self.on_all_components_scanned()
        elif self.current_index < len(self.component_config):
            self.update_component_prompt()
            self.scan_QR_code()
        elif self.current_index >= len(self.component_config):
            self.on_all_components_scanned()

    def check_grade(self):
        num_modules = int(self.full_board_id[5])+int(self.full_board_id[6])
        correct_grades = self.full_board_id[9:11] 
        self.passed_test = True
        self.comments = []

        for key, value in self.scanned_components.items():
            self.results[key] = {"full_id": value, "Passed": True}
            pass_id_check, warnings = self.check_id(value, key)
            if not pass_id_check:
                self.results[key]["Passed"] = False
            
            if len(value) > 7:
                d_or_t = value[7]
            else:
                d_or_t = None

            if (d_or_t is not None) and (d_or_t == 'D'):
                module_num = int(key[-1]) - 1
                scanned_grade = value[8]
                correct_grade = self.econ_grade_map[num_modules][correct_grades][module_num]
                self.results[key]["Correct Grade"] = correct_grade
                self.results[key]["Scanned Grade"] = scanned_grade

                if scanned_grade != correct_grade:
                    self.results[key]["Passed"] = False
            self.results[key]["Comments"] = warnings
            if warnings is not None:
                self.comments.append(warnings)

        self.passed_test = all(r["Passed"] for r in self.results.values())
        self.comments = "All grades correct." if self.passed_test else "\n".join(self.comments)

    def get_submit_action(self):
        return self.btn_submit_action

    def get_parent(self):
        return self.parent

    def check_id(self, value, site_name):
        warnings = []

        if len(value) < 9:
            return False, f"'{value}' is not a valid ECON ID (too short)."

        if value[:3] != "320":
            warnings.append(f"Unexpected prefix '{value[:3]}' (expected '320').")

        d_or_t = value[7]
        expected = site_name[4]

        if d_or_t not in ('D', 'T'):
            return False, f"Non-existent ECON type '{d_or_t}' scanned for site {site_name}."

        if d_or_t != expected:
            warnings.append(f"ECON{d_or_t} scanned for site {site_name}.")
        elif d_or_t == 'D': 
            grade_check_passed, grade_check_warning = self.check_individual_grade(value, site_name)
            if not grade_check_passed:
                warnings.append(grade_check_warning)

        if warnings:
            return False, "\n".join(warnings)
        return True, None

    def check_individual_grade(self, value, site_name):
        num_modules = int(self.full_board_id[5])+int(self.full_board_id[6])
        correct_grades = self.full_board_id[9:11] 
        d_or_t = value[7]
        module_num = int(site_name[-1])-1
        if d_or_t == 'D':
            scanned_grade = value[8]
            correct_grade = self.econ_grade_map[num_modules][correct_grades][module_num]

            if scanned_grade != correct_grade:
                return False, f"{site_name} should be grade {correct_grade}, but grade {scanned_grade} was scanned."

        return True, None
