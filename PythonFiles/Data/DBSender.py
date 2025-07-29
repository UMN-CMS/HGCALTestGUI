import requests
import json
import socket
import logging
from pathlib import Path
import logging
# from read_barcode import read_barcode

logger = logging.getLogger('HGCALTestGUI.PythonFiles.Data.DBSender')

# python scripts run from here are on the machine that contains the server and database
class DBSender():

    def __init__(self, gui_cfg):
        self.gui_cfg = gui_cfg

        # Predefined URL for the database
        self.db_url = self.gui_cfg.getDBInfo("baseURL")

        # If True, use database
        # If False, run in "offline" mode
        self.use_database = self.gui_cfg.get_if_use_DB()

    def attempt_admin_access(self, password):
        r = requests.post('{}/connect_admin.py'.format(self.db_url), data={'password': password})
        lines = r.text.split('\n')

        try:
            begin = lines.index("Begin") + 1
            end = lines.index("End")
        except:
            logger.error('There was an issue with the web API script `connect_admin.py`. The website may be down.')
            logger.debug(r.text)

        for i in range(begin, end):
            if lines[i] == 'Success':
                return True
            else:
                return False

    def decode_label(self, full_id):
        
        if len(full_id) != 15:
            logger.warning('Invalid label scanned')
            label_info = None
        else:
            r = requests.post('{}/decode_label.py'.format(self.db_url), data={'label': full_id})
            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error('There was an issue with the web API script `decode_label.py`. Check that the label library has been updated for the web API.')
                logger.debug(r.text)

            temp = []

            for i in range(begin, end):
                temp.append(lines[i])
            
            label_info = {'Major Type': temp[0], 'Subtype': temp[1], 'SN': temp[2]}

        return label_info


    def add_new_user_ID(self, user_ID, passwd):
        
        if (self.use_database):

            try:
                r = requests.post('{}/add_tester2.py'.format(self.db_url), data= {'person_name':user_ID, 'password': passwd})
            except Exception as e:
                logger.error("Unable to add the user to the database. Username: {}. Check to see if your password is correct.".format(user_ID))
                logger.debug(r.text)


        # If not using the database, use this...
        else:
            pass    
     

    # Returns an acceptable list of usernames from the database
    def get_usernames(self):
        if (self.use_database):
            r = requests.get('{}/get_usernames.py'.format(self.db_url))
            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error('There was an issue with the web API script `get_usernames.py`. There is likely a syntax error in an associated web API script.')
                logger.debug(r.text)

            usernames = []

            for i in range(begin, end):
                temp = lines[i]
                usernames.append(temp)

            return usernames

        # If not using database...        
        else:

            return self.gui_cfg.getUsers()


    # Returns a list of booleans
    # Whether or not DB has passing results 
    def get_previous_test_results(self, full_id):
   
        r = requests.post('{}/get_previous_test_results.py'.format(self.db_url), data={"full_id": str(full_id)})
        
        lines = r.text.split('\n')

        try:
            begin1 = lines.index("Begin1") + 1
            end1 = lines.index("End1")
            begin2 = lines.index("Begin2") + 1
            end2 = lines.index("End2")
            begin3 = lines.index("Begin3") + 1
            end3 = lines.index("End3")
        except:
            logger.error('There was an issue with the web API script `get_previous_test_results.py`. There is likely a syntax error in an associated web API script.')
            logger.debug(r.text)

        tests_run = []
        outcomes = []
        poss_tests = []

        for i in range(begin1, end1):
            tests_run.append(lines[i])
        for i in range(begin2, end2):
            outcomes.append(lines[i])
        for i in range(begin3, end3):
            poss_tests.append(lines[i])

        tests_passed = []
        for i in range(len(tests_run)):
            tests_passed.append([tests_run[i], outcomes[i]])

        return tests_passed, poss_tests
    
    
    # Posts a new board with passed in full id
    def add_new_board(self, full, user_id, comments):
        r = requests.post('{}/add_module2.py'.format(self.db_url), data={"full_id": str(full)})
        r = requests.post('{}/board_checkin2.py'.format(self.db_url), data={"full_id": str(full), 'person_id': str(user_id), 'comments': str(comments)})
            

        try:
            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error('There was an issue with the web API scripts `add_module2.py` or `board_checkin2.py`. There is likely a syntax error in an associated web API script.')
                logger.debug(r.text)

            in_id = None

            for i in range(begin, end):
                in_id = lines[i]
        except:
            logger.warning("Tried checking in a board that was already checked in")
            in_id = None

        return in_id

    def is_new_board(self, full):
        r = requests.post('{}/is_new_board.py'.format(self.db_url), data={"full_id": str(full)})
        
        lines = r.text.split('\n')
   
        try:
            begin = lines.index("Begin") + 1
            end = lines.index("End")
        except:
            logger.error('There was an issue with the web API script `is_new_board.py`. There is likely a syntax error in an associated web API script.')
            logger.debug(r.text)


        for i in range(begin, end): 
            
            if lines[i] == "True":
                return True
            elif lines[i] == "False":
                return False

    def set_component_info(self, info_dict):
        r = requests.post('{}/set_component_info.py'.format(self.db_url), data = info_dict)

    def add_test_stand_info(self, info_dict):
        r = requests.post('{}/add_test_station_info.py'.format(self.db_url), data = info_dict)

        lines = r.text.split('\n')

        begin = lines.index("Begin") + 1
        end = lines.index("End")

        for i in range(begin, end): 
            return lines[i]

    def get_tester_config(self, teststand):
        r = requests.post('{}/get_tester_config_id.py'.format(self.db_url), data={'test_stand':teststand})

        lines = r.text.split('\n')

        try:
            begin = lines.index("Begin") + 1
            end = lines.index("End")

            for i in range(begin, end): 
                return lines[i]

        except:
            logger.warning('Tried to fetch tester configuration from DB... none was found.')
            return None
        

    def add_test_json(self, json_file, config):
        
        with open(json_file) as load_file:
            results = json.load(load_file)        

        test_attach = results.pop('data', None)
        datafile_name = "{}/JSONFiles/sending.json".format(str(Path.home().absolute()))

        results['test_type'] = results['name']
        results['full_id'] = results['board_sn']
        results['successful'] = int(results['pass'])
        results['config_id'] = config

        with open(datafile_name, 'w') as datafile:
            json.dump(test_attach, datafile)

        datafile = open(datafile_name, "rb")        

        attach_data = {'attach1': datafile}

        if (self.use_database):
            r = requests.post('{}/add_test_json.py'.format(self.db_url), data = results, files = attach_data)
        else:
            pass


 # Returns a list of all different types of tests
    def get_test_list(self):
        if (self.use_database):
            r = requests.get('{}/get_test_types.py'.format(self.db_url))

            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error('There was an issue with the web API script `get_test_types.py`. There is likely a syntax error in an associated web API script.')
                logger.debug(r.text)

            tests = []

            for i in range(begin, end):
                temp = lines[i][1:-1].split(",")
                temp[0] = str(temp[0][1:-1])
                temp[1] = int(temp[1])
                tests.append(temp)

            return tests

        else:
            
            blank_tests = []
            for i in enumerate(self.gui_cfg.getNumTest()):
                blank_tests.append("Test{}".format(i))

            return blank_tests

