################################################################################
import json, logging, socket, PythonFiles, copy, os
import requests
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="/home/{}/GUILogs/visual_gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.DEBUG)

class DataHolder():

    #################################################

    # List of the variables being held by data holder
    def __init__(self, gui_cfg):

        # Object for taking care of instantiation for different test types
        self.gui_cfg = gui_cfg

        # Object that sends information to the database
        self.data_sender = DBSender(gui_cfg)

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

        # For the visual inspection component
        self.inspection_data = {
                'board_bent': False,
                'board_broken': False,
                'component_missing': False,
                'component_broken': False,
                'inspection_comments': "_"
                }

        self.image_data = []

        # All of the checkbox logic
        # Dictionaries stored by inspection index
        self.all_checkboxes = []

        self.label_info = None

        for index in range(self.gui_cfg.getNumInspections()):
            self.all_checkboxes.append(self.gui_cfg.getCheckDict(index))

        # All of the comments logic
        # Dictionaries stored by inspection index
        self.all_comments = []

        for index in range(self.gui_cfg.getNumInspections()):
            self.all_comments.append(self.gui_cfg.getCommentDict(index))

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

        self.photo_list = self.gui_cfg.getPhotoList()


    #################################################

    def num_photo(self):
        return len(self.photo_list)

    def get_photo_list(self):
        return self.photo_list

    def get_check_dict(self, idx):
        return self.all_checkboxes[idx]

    def get_comment_dict(self, idx):
        return self.all_comments[idx]

    def set_comment_dict(self, idx, val):
        self.all_comments[idx] = val

    def add_new_user_name(self, user_ID, passwd):
        self.data_dict['user_ID'] = user_ID

        is_new_user_ID = True

        for item in self.get_all_users():
            if self.data_dict['user_ID'] == item:
                is_new_user_ID = False
        print("\n\n\n\n\n\nIs the user new?:{}\n\n\n\n\n\n".format(is_new_user_ID))

        if is_new_user_ID:
            self.data_sender.add_new_user_ID(self.data_dict['user_ID'], passwd)


    # checks if the board is in the database already
    def check_if_new_board(self):
        logging.info("DataHolder: Checking if board is a new board")
        print("testing if new board")

        full = self.get_full_ID()
        user = self.data_dict['user_ID']
        comments = 'Checked in during Visual Inspection'
        is_new_board = self.data_sender.is_new_board(full)
        print(is_new_board)

        # if it's new, checks it in
        if is_new_board == True:
            in_id = self.data_sender.add_new_board(full, user, comments)
            if in_id:
                print('Board added to Database')
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'This is a new board, it has been checked in. Check In ID:' + in_id

        # otherwise it looks for previous test results
        else:
            prev_results, test_names = self.data_sender.get_previous_test_results(full)
            if prev_results:
                self.data_dict['test_names'] = test_names
                self.data_dict['prev_results'] = prev_results
            else:
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'No tests have been run on this board.'

    def decode_label(self):
        full_id = self.get_full_ID()

        self.label_info = self.data_sender.decode_label(full_id)


    #################################################


    def set_user_ID(self, user_ID):

        print("\n\n\n\n\nuser_ID", user_ID)

        self.data_dict['user_ID'] = user_ID
        logging.debug("DataHolder: User ID has been set.")

    ##################################################

    # sets the full id and updates the config
    def set_full_ID(self, full):
        self.data_dict['current_full_ID'] = full
        new_cfg = update_config(full)
        self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg)
        self.num_modules = int(full[5]) + 1
        logging.info("DataHolder: Full ID has been set.")

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
            print(view)
            self.data_sender.add_board_image(self.data_dict["current_full_ID"], self.image_holder[i], view)


    # sets the boards location in the database to the current test stand
    def update_location(self, full):
        text = self.data_sender.update_location(full, 'Visual Inspection')
        print(text)


    ##################################################

    def get_full_ID(self):
        return self.data_dict['current_full_ID']

    #################################################

    # Future method to send data to the database
    def send_all_to_DB(self):

        person_ID = self.data_dict['user_ID']
        comments = self.data_dict['comments']
        full_id = self.get_full_ID()


        for i in range(len(self.data_dict['tests_run'])):
            print("Iteration:", i)
            temp = 0
            if self.data_lists['test_results'][i]:
                temp = 1
            info_dict = {"full_id":full_id,"tester": person_ID, "test_type": self.tests_run[i], "successful": temp, "comments": comments}
            with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
                print(info_dict)
                json.dump(info_dict, outfile)
            self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]))
            #message = "add_test_json;{'json_file': {}/JSONFiles/storage.json, ''}"
        logging.info("DataHolder: All results sent to database.")
    #################################################

    # current method to send to the database
    def send_to_DB(self):
        test_names = "Visual Inspection"
        test_type_id = 0

        info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": test_type_id, "successful": self.data_dict["inspection_pass"], "comments": self.data_dict['comments']}

        with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
            print(info_dict)
            json.dump(info_dict, outfile)

        with open("{}/JSONFiles/data.json".format(PythonFiles.__path__[0]), "w") as outfile:
            json.dump(self.inspection_data, outfile)

        self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "{}/JSONFiles/data.json".format(PythonFiles.__path__[0]))

        #self.dbclient.send_request(message)
        logging.info("DataHolder: Test results sent to database.")

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames()
        return users_list

    #################################################

    # Prints all the variable values inside data_holder
    def print(self):
        print("data_dict: \n", self.data_dict, "\ninspection_data: \n", self.inspection_data, "\nimage_data:\n", self.image_data, "\nall_checkboxes: \n", self.all_checkboxes, "\nall_comments: \n", self.all_comments, '\n\n')



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

        logging.info("DataHolder: Test results have been saved")

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

        self.inspection_data = {
                'board_bent': False,
                'board_broken': False,
                'component_missing': False,
                'component_broken': False,
                'inspection_comments': "_"
                }

        logging.info("DataHolder: DataHolder Information has been reset for a new test.")

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

    ################################################

#################################################################################


