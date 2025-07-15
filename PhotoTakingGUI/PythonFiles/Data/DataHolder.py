###############################################################################
import json, logging, socket, PythonFiles, copy, os
import requests
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config

logger = logging.getLogger('HGCAL_Photo.PythonFiles.Data.DataHolder')

class DataHolder():

    #################################################

    # List of the variables being held by data holder
    def __init__(self, gui_cfg, main_path):

        # Object for taking care of instantiation for different test types
        self.gui_cfg = gui_cfg
        self.main_path = main_path

        # Object that sends information to the database
        self.data_sender = DBSender(gui_cfg, main_path)

        # dictionary to store data
        self.data_dict = {
                'user_ID': "_",
                'test_stand': str(socket.gethostname()),
                'current_full_ID': "-1BAD",
                'comments': "_",
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [str(i + 1) for i in range(self.getNumTest())],
                }
        self.data_dict["inspection_completed"] = False
        self.data_dict["inspection_pass"] = False

        # dictionary to hold images before sending them to the database
        self.image_holder = {}

        self.image_data = []

        self.label_info = None

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

        self.photo_list = self.gui_cfg.getPhotoList()


    #################################################

    def num_photo(self):
        return len(self.photo_list)

    def get_photo_list(self):
        return self.photo_list

    def add_new_user_name(self, user_ID, passwd):
        self.data_dict['user_ID'] = user_ID

        is_new_user_ID = True

        for item in self.get_all_users():
            if self.data_dict['user_ID'] == item:
                is_new_user_ID = False

        if is_new_user_ID:
            self.data_sender.add_new_user_ID(self.data_dict['user_ID'], passwd)


    # checks if the board is in the database already
    def check_if_new_board(self):
        logger.info("Checking if full id is a new board...")

        full = self.get_full_ID()
        is_new_board = self.data_sender.is_new_board(full)

        if is_new_board == True:
            logger.info('Board is new, sending user to visual inspection station.')

        # otherwise it looks for previous test results
        else:
            logger.info("Board has been checked in, getting previous results")
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

        self.data_dict['user_ID'] = user_ID
        logger.info("User ID set to %s" % user_ID)

    ##################################################

    # sets the full id and updates the config
    def set_full_ID(self, full):
        self.data_dict['current_full_ID'] = full
        new_cfg = update_config(full)
        self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg, self.main_path)
        
        logger.info("Full ID set to %s" % full)

    def save_image(self):
        for i in self.image_holder:
            image = self.image_holder[i]
            # Saves the image to a file
            image.save(i)

    # sends the image to the database
    def send_image(self):
        for i in self.image_holder:
            idx = int(i[-5])
            if idx == 0:
                view = 'Top'
            else:
                view = 'Bottom'
            logger.info('Uploading %s image...' % view)
            self.data_sender.add_board_image(self.data_dict["current_full_ID"], self.image_holder[i], view)


    def upload_local_boards(self, board_list):
        for path, sn, view in board_list:
            self.data_sender.upload_local_board(path, sn, view)
        logger.info('Locally saved images uploaded sucessfully')

    ##################################################

    def get_full_ID(self):
        return self.data_dict['current_full_ID']

    #################################################

    # current method to send to the database
    def send_to_DB(self):
        test_names = "Visual Inspection"
        test_type_id = 0

        info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": test_type_id, "successful": self.data_dict["inspection_pass"], "comments": self.data_dict['comments']}

        with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
            json.dump(info_dict, outfile)

        with open("{}/JSONFiles/data.json".format(PythonFiles.__path__[0]), "w") as outfile:
            json.dump(self.inspection_data, outfile)

        self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "{}/JSONFiles/data.json".format(PythonFiles.__path__[0]))
        logger.info("Test results sent to database.")

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames()
        return users_list

    #################################################

    # sends the visual inspection json comments to the database
    def update_from_json_string(self):

        test_type = "Visual Inspection"
        test_type_id = 0

        passed = not any([x for x in self.inspection_data.values()][:-1])

        self.data_dict['inspection_completed'] = True
        self.data_dict['inspection_pass'] = int(passed)
        self.data_dict['data'] = self.inspection_data

        self.send_to_DB()

        logger.info("Test results have been saved")

    ################################################

    def add_inspection_to_comments(self):
        if self.inspection_data['board_bent']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board is chipped or bent."
        if self.inspection_data['board_broken']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Wagon connnection pin is bent."
        if self.inspection_data['component_missing']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Engine connection pin is bent."
        if self.inspection_data['component_broken']:
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

    ################################################

    # Keeps the login information stored
    # resets all other data
    def data_holder_new_test(self):

        self.data_dict = {
                'user_ID': self.data_dict['user_ID'],
                'test_stand': str(socket.gethostname()),
                'current_full_ID': self.data_dict['current_full_ID'],
                'comments': "_",
                'is_new_board': False,
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [str(i + 1) for i in range(self.getNumTest())],
                }
        self.data_dict["inspection_completed"] = False
        self.data_dict["inspection_pass"] = False


        self.image_holder = {}

        logger.info("DataHolder Information has been reset for a new test.")

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

    ################################################

#################################################################################


