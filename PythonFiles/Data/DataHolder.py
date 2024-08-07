################################################################################
import json, logging, socket, PythonFiles, copy, os
import requests
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config
import yaml

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Data.DataHolder')

#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/visual_gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

class DataHolder():

    #################################################

    # List of the variables being held by data holder
    def __init__(self, gui_cfg):
        
        # Object for taking care of instantiation for different test types
        self.gui_cfg = gui_cfg

        self.curpath = os.path.dirname(os.path.abspath(__file__))

        # Object that sends information to the database
        self.data_sender = DBSender(gui_cfg)
        #self.dbclient = DBSendClient()
        use_db = self.gui_cfg.get_if_use_DB()

        if use_db:
            self.test_list = self.data_sender.get_test_list()
            gui_tests = self.gui_cfg.getTests()
            db_test_names = dict(self.test_list)
            self.index_gui_to_db = {}
            for i,x in enumerate(gui_tests):
                if x['name'] in db_test_names.keys():
                    self.index_gui_to_db[i] = x['name']
            #self.index_gui_to_db = {i : db_test_names[x["name"]] for i,x in enumerate(gui_tests)}

        else:
            gui_tests = self.gui_cfg.getTests()
            self.index_gui_to_db = {}
            for i,x in enumerate(gui_tests):
                self.index_gui_to_db[i] = x['name']
            #self.index_gui_to_db = [i for i,x in enumerate(self.gui_cfg.getTests())]

        #dictionary of info to be held
        self.data_dict = {
                'user_ID': "_",
                'test_stand': str(socket.gethostname()),
                'current_full_ID': "-1BAD",
                'queue': None,
                'comments': "_",
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [i  for i in range(self.getNumTest())],
                }
        # adds tests to dictionary to be marked as complete
        for i in range(self.gui_cfg.getNumTest()):
            self.data_dict["test{}_completed".format(i)] = False
            self.data_dict["test{}_pass".format(i)] = False

        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_dict['physical{}_completed'.format(i)] = False
            self.data_dict['physical{}_pass'.format(i)] = False

        self.data_lists = {
                'test_results': [],
                'test_completion': [],
                'physical_results': [],
                'physical_completion': [],
                }

        self.total_test_num = 0

        self.ptest_criteria = {}
        self.ptest_names = self.gui_cfg.getPhysicalNames()

        self.label_info = None

        self.config_id = None

        self.admin = False
        self.password = None

        self.tester_type = None
        self.wagon_tester_info = {
                'Kria': None,
                'Tester': None,
                'Interposer': None,
                'Wagon Wheel 1': None,
                'Wagon Wheel 2': None,
                'Wagon Wheel 3': None,
                'Wagon Wheel 4': None,
                'num_wagon_wheels': 0,
                'interposer_type': None,
                }

        self.engine_tester_info = {
                'ZCU': None,
                'East Interposer': None,
                'West Interposer': None,
                'Test Bridge 1': None,
                'Test Bridge 2': None,
                }

       
        # adds each test to data list for results and completion status to be added
        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_lists['physical_results'].append(self.data_dict['physical{}_pass'.format(i)])
            self.data_lists['physical_completion'].append(self.data_dict['physical{}_completed'.format(i)])

            temp_dict = {
                '{}'.format(i) : self.gui_cfg.getPhysicalTestRequirements(i),
            }

            self.ptest_criteria.update(temp_dict)

            self.total_test_num = self.total_test_num + 1

        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'].append(self.data_dict['test{}_pass'.format(i)])
            self.data_lists['test_completion'].append(self.data_dict['test{}_completed'.format(i)])

            self.total_test_num = self.total_test_num + 1
    
        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()


    #################################################

    def get_total_test_num(self):
        return self.total_test_num

    def get_use_scanner(self):
        return self.gui_cfg.getUseScanner()

    def get_check_dict(self, idx):
        return self.all_checkboxes[idx]

    def get_comment_dict(self, idx):
        return self.all_comments[idx]

    def set_comment_dict(self, idx, val):
        self.all_comments[idx] = val 

    def add_new_user_name(self, user_ID):
        self.data_dict['user_ID'] = user_ID
        
        is_new_user_ID = True

        for item in self.get_all_users():
            if self.data_dict['user_ID'] == item:
                is_new_user_ID = False

        if is_new_user_ID:
            self.data_sender.add_new_user_ID(self.data_dict['user_ID'], self.password)        

    def get_physical_criteria(self, num):
        return self.ptest_criteria[num]


    # when a board gets entered, this function checks if it's new
    def check_if_new_board(self):
        logger.info("DataHolder: Checking if full id is a new board")

        full = self.get_full_ID()
        #returns true if the board is new, false if not
        is_new_board = self.data_sender.is_new_board(full)
        
        if is_new_board == True:
            pass

        else:
            # if the board is not new, this returns the previous testing information on the board
            prev_results, test_names = self.data_sender.get_previous_test_results(full)
            if prev_results:
                self.data_dict['test_names'] = test_names
                self.data_dict['prev_results'] = prev_results
            else:
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'No tests have been run on this board.'

    def decode_label(self, full_id):
        self.label_info = self.data_sender.decode_label(full_id)


    #################################################


    def set_user_ID(self, user_ID):

        print("\nuser_ID", user_ID)
 
        self.data_dict['user_ID'] = user_ID 
        logger.debug("DataHolder: User ID has been set.")

    ##################################################

    def set_full_ID(self, full):
        self.data_dict['current_full_ID'] = full
        if self.gui_cfg.getSerialCheckSafe():
            new_cfg = update_config(full)
            self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg)
        logger.info("DataHolder: Full ID has been set.")


    def update_location(self, full):
        text = self.data_sender.update_location(full, self.data_dict['test_stand'])
        print(text)


    ##################################################

    def get_full_ID(self):
        return self.data_dict['current_full_ID']

    #################################################

    def attempt_admin_access(self, password):
        admin_connected = self.data_sender.attempt_admin_access(password)
        if admin_connected == True:
            self.admin = True
            self.password = password

    def upload_test_stand_info(self):
        if self.tester_type == 'Wagon':
            info_dict = {'kria': self.wagon_tester_info['Kria'],
                    'tester': self.wagon_tester_info['Tester'],
                    'interposer': self.wagon_tester_info['Interposer'],
                    'interposer_type': self.wagon_tester_info['interposer_type'],
                    'wheel_1': self.wagon_tester_info['Wagon Wheel 1'],
                    'wheel_2': self.wagon_tester_info['Wagon Wheel 2'],
                    'wheel_3': self.wagon_tester_info['Wagon Wheel 3'],
                    'wheel_4': self.wagon_tester_info['Wagon Wheel 4'],
                    'test_stand': self.data_dict['test_stand'],
                    }
            wagon_cfg = yaml.safe_load(open('{}/../../Configs/Wagon_cfg.yaml'.format(self.curpath),"r"))
            db_url = wagon_cfg['DBInfo']['baseURL']
        if self.tester_type == 'Engine':
            info_dict = {'ZCU': self.engine_tester_info['ZCU'],
                    'east_interposer': self.engine_tester_info['East Interposer'],
                    'west_interposer': self.engine_tester_info['West Interposer'],
                    'bridge_1': self.engine_tester_info['Test Bridge 1'],
                    'bridge_2': self.engine_tester_info['Test Bridge 2'],
                'test_stand': self.data_dict['test_stand'],
                }
            engine_cfg = yaml.safe_load(open('{}/../../Configs/Engine_cfg.yaml'.format(self.curpath),"r"))
            db_url = engine_cfg['DBInfo']['baseURL']
        self.config_id = self.data_sender.add_test_stand_info(info_dict, db_url)

    def set_component_info(self, label, working, comments):
        info_dict = {'label': label, 'working': working, 'comments': comments}

        if self.tester_type == 'Wagon':
            wagon_cfg = yaml.safe_load(open('{}/../../Configs/Wagon_cfg.yaml'.format(self.curpath),"r"))
            db_url = wagon_cfg['DBInfo']['baseURL']

        if self.tester_type == 'Engine':
            engine_cfg = yaml.safe_load(open('{}/../../Configs/Engine_cfg.yaml'.format(self.curpath),"r"))
            db_url = engine_cfg['DBInfo']['baseURL']

        self.data_sender.set_component_info(info_dict, db_url)

    #################################################

    # Future method to send data to the database
    def send_all_to_DB(self):
          
        person_ID = self.data_dict['user_ID']
        comments = self.data_dict['comments']
        full_id = self.get_full_ID()
        
         
        for i in range(len(self.data_dict['tests_run'])):
            temp = 0
            if self.data_lists['test_results'][i]:
                temp = 1
            info_dict = {"full_id":full_id,"tester": person_ID, "test_type": self.index_gui_to_db[self.tests_run[i]], "successful": temp, "comments": comments} 
            with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
                print(info_dict)
                json.dump(info_dict, outfile)
            self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]))
            #message = "add_test_json;{'json_file': {}/JSONFiles/storage.json, ''}"
        logger.info("DataHolder: All results sent to database.")
    #################################################

    def send_to_DB(self, test_run):
        index = test_run
        
        test_names = self.gui_cfg.getTestNames()

        file_path_list = []

        for name in test_names:
            file_path_list.append("{}/JSONFiles/Current_{}_JSON.json".format(PythonFiles.__path__[0], name.replace(" ", "").replace("/", "")))
            
        # Converts self.test_results[index] into 1/0 instead of bool       
        temp = 0
        if self.data_lists['test_results'][index]:
            temp = 1 


        if self.config_id:
            info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": self.index_gui_to_db[self.data_dict['tests_run'][index]], "successful": temp, "comments": self.data_dict['comments'], 'config':self.config_id}
        else:
            info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": self.index_gui_to_db[self.data_dict['tests_run'][index]], "successful": temp, "comments": self.data_dict['comments']}
        
        with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
            print(str(info_dict) + '\r\n')
            json.dump(info_dict, outfile)

        self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), file_path_list[index])
        logger.info("DataHolder: Test results sent to database.")

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames() 
        return users_list

    #################################################

    # Prints all the variable values inside data_holder
    def print(self):    
        print("data_dict: \n", self.data_dict, "\ninspection_data: \n", self.inspection_data,  "\nall_checkboxes: \n", self.all_checkboxes, "\nall_comments: \n", self.all_comments, '\n\n')
           

    #################################################

    def update_from_json_string(self, imported_json_string):
        json_string = imported_json_string.replace("'", '"')
        json_string = json_string.replace('True', 'true')
        json_string = json_string.replace('False', 'false')
        json_dict = json.loads(json_string)

        test_names = self.gui_cfg.getTestNames()

        current_test_idx = self.gui_cfg.getTestIndex()
        print("current_test_idx: {}\r\n".format(current_test_idx))

        test_type = test_names[current_test_idx]

        with open("{}/JSONFiles/Current_{}_JSON.json".format(PythonFiles.__path__[0], test_names[current_test_idx].replace(" ", "").replace("/", "")), "w") as file:
            json.dump(json_dict['data'], file)
        self.data_dict['test{}_completed'.format(current_test_idx)] = True
        self.data_dict['test{}_pass'.format(current_test_idx)] = json_dict["pass"]

        # Updates the lists
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'][i] = self.data_dict['test{}_pass'.format(i)]
            self.data_lists['test_completion'][i] = self.data_dict['test{}_completed'.format(i)]
        
        if self.gui_cfg.get_if_use_DB():
            self.send_to_DB(current_test_idx)

        logger.info("DataHolder: Test results have been saved")

    ################################################

    def add_inspection_to_comments(self):
        if self.inspection_data['board_chipped_bent']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board is chipped or bent."
        if self.inspection_data['wagon_connection_pin_bent']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Wagon connnection pin is bent."
        if self.inspection_data['engine_connection_pin_bent']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Engine connection pin is bent."
        if self.inspection_data['visual_scratches']: 
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " There are visual scratches on the board."
        if self.inspection_data['inspection_comments'] != "_": 
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " User comments: " + self.inspection_data['inspection_comments']

    ################################################

    # Tracking the test index in another place and propagating to the config
    def setTestIdx(self, test_idx):
        
        self.current_test_idx = test_idx
        self.gui_cfg.setTestIndex(self.current_test_idx)

    def getNumTest(self):
        return self.gui_cfg.getNumTest()

    def getTestNames(self):
        return self.gui_cfg.getTestNames()

    def getNumPhysicalTest(self):
        return self.gui_cfg.getNumPhysicalTest()

    def getPhysicalNames(self):
        return self.gui_cfg.getPhysicalNames()

    ################################################

    def getGUIcfg(self):
        return self.gui_cfg

    ################################################

    # resets the data holder when a new board is scanned
    # Keeps the login information stored, full id has already been changed
    def data_holder_new_test(self): 

        self.data_dict = {
                'user_ID': self.data_dict['user_ID'],
                'test_stand': str(socket.gethostname()),
                'current_full_ID': self.data_dict['current_full_ID'],
                'queue': self.data_dict['queue'],
                'comments': "_",
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [i for i in range(self.getNumTest())],
                }

        self.data_lists = {
                'test_results': [],
                'test_completion': [],
                'physical_results': [],
                'physical_completion': [],
                }

        self.total_test_num = 0

        self.label_info = None

        self.config_id = None

        for i in range(self.gui_cfg.getNumTest()):
            self.data_dict['test{}_completed'.format(i)] = False
            self.data_dict['test{}_pass'.format(i)] = False

        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_dict['physical{}_completed'.format(i)] = False
            self.data_dict['physical{}_pass'.format(i)] = False


        self.ptest_criteria = {}
        self.ptest_names = self.gui_cfg.getPhysicalNames()

        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_lists['physical_results'].append(self.data_dict['physical{}_pass'.format(i)])
            self.data_lists['physical_completion'].append(self.data_dict['physical{}_completed'.format(i)])

            temp_dict = {
                '{}'.format(i) : self.gui_cfg.getPhysicalTestRequirements(i),
            }

            self.ptest_criteria.update(temp_dict)

            self.total_test_num = self.total_test_num + 1
        
        #print(self.data_dict)
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'].append(self.data_dict['test{}_pass'.format(i)])
            self.data_lists['test_completion'].append(self.data_dict['test{}_completed'.format(i)])

            self.total_test_num = self.total_test_num + 1

        logger.info("DataHolder: DataHolder Information has been reset for a new test.")        

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

    ################################################

    #################################################################################


