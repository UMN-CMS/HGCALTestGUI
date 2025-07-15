################################################################################
import json, logging, socket, PythonFiles, copy, os
import requests
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config
from pathlib import Path
import yaml

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Data.DataHolder')

class DataHolder():

    #################################################

    # List of the variables being held by data holder
    def __init__(self, gui_cfg):

        (Path.home() / "JSONFiles").mkdir(exist_ok=True, parents=True)
        
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

        self.admin = False
        self.password = None
       
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
        logger.info("Checking if full id is a new board...")

        full = self.get_full_ID()
        #returns true if the board is new, false if not
        is_new_board = self.data_sender.is_new_board(full)
        
        if is_new_board == True:
            logger.info("Board is new")

        else:
            logger.info("Board has been checked in, getting previous results")
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

    def get_test_results(self):
        prev_results, test_names = self.data_sender.get_previous_test_results(self.get_full_ID())
        res_dict = {}
        for n in test_names:
            res_dict[n] = []
        for idx,el in enumerate(prev_results):
            res_dict[el[0]] = el[1]
        return res_dict


    #################################################


    def set_user_ID(self, user_ID):
 
        self.data_dict['user_ID'] = user_ID 
        logger.info("User ID set to %s"  % user_ID)

    ##################################################

    def set_full_ID(self, full):
        self.data_dict['current_full_ID'] = full
        if self.gui_cfg.getSerialCheckSafe():
            new_cfg = update_config(full)
            self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg)
        logger.info("Full ID set to {}".format(full))


    ##################################################

    def get_full_ID(self):
        return self.data_dict['current_full_ID']

    #################################################

    def send_to_DB(self, test_run):
        logger.info("Uploading results...")

        index = test_run
        
        test_names = self.gui_cfg.getTestNames()

        file_path_list = []

        for name in test_names:
            file_path_list.append("{}/JSONFiles/Current_{}_JSON.json".format(str(Path.home().absolute()), name.replace(" ", "").replace("/", "")))
            
        # Converts self.test_results[index] into 1/0 instead of bool       
        temp = 0
        if self.data_lists['test_results'][index]:
            temp = 1 


        if self.config_id:
            info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": self.index_gui_to_db[self.data_dict['tests_run'][index]], "successful": temp, "comments": self.data_dict['comments'], 'config':self.config_id}
        else:
            info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": self.index_gui_to_db[self.data_dict['tests_run'][index]], "successful": temp, "comments": self.data_dict['comments']}
        
        with open("{}/JSONFiles/storage.json".format(str(Path.home().absolute())), "w") as outfile:
            logger.debug(str(info_dict))
            json.dump(info_dict, outfile)

        self.data_sender.add_test_json(file_path_list[index], self.config_id)
        logger.info("Test results sent to database successfully.")

        self.data_dict['comments'] = '_'

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames() 
        return users_list

    #################################################

    def update_from_json_string(self, imported_json_string):
        json_string = imported_json_string.replace("'", '"')
        json_string = json_string.replace('True', 'true')
        json_string = json_string.replace('False', 'false')
        json_dict = json.loads(json_string)

        test_names = self.gui_cfg.getTestNames()
        test_type = test_names[self.current_test_idx]

        with open("{}/JSONFiles/Current_{}_JSON.json".format(str(Path.home().absolute()), test_names[self.current_test_idx].replace(" ", "").replace("/", "")), "w") as file:
            json.dump(json_dict, file)
        self.data_dict['test{}_completed'.format(self.current_test_idx)] = True
        self.data_dict['test{}_pass'.format(self.current_test_idx)] = json_dict["pass"]
        comments = json_dict.get('comments', '_')
        self.data_dict['comments'] = comments
        
        # Updates the lists
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'][i] = self.data_dict['test{}_pass'.format(i)]
            self.data_lists['test_completion'][i] = self.data_dict['test{}_completed'.format(i)]
        
        if self.gui_cfg.get_if_use_DB():
            self.send_to_DB(self.current_test_idx)

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
        
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'].append(self.data_dict['test{}_pass'.format(i)])
            self.data_lists['test_completion'].append(self.data_dict['test{}_completed'.format(i)])

            self.total_test_num = self.total_test_num + 1

        logger.info("DataHolder Information has been reset for a new board.")


    ################################################

    #################################################################################


