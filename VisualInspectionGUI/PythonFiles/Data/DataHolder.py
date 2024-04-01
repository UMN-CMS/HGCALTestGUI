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
        #self.dbclient = DBSendClient()

        self.data_dict = {
                'user_ID': "_",
                'test_stand': str(socket.gethostname()),
                'current_serial_ID': "-1BAD",
                'comments': "_",
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [str(i + 1) for i in range(self.getNumTest())],
                }
        for i in range(self.gui_cfg.getNumTest()):
            self.data_dict["test{}_completed".format(i+1)] = False
            self.data_dict["test{}_pass".format(i+1)] = False

        self.image_holder = {}

        # For the visual inspection component
        self.inspection_data = {
                'board_chipped_bent': False,
                'wagon_connection_pin_bent': False,
                'engine_connection_pin_bent': False,
                'visual_scratches': False,
                'inspection_comments': "_"
                }

        self.image_data = []

        self.photos = 'Top and Bottom'

        # All of the checkbox logic
        # Dictionaries stored by inspection index
        self.all_checkboxes = []

        for index in range(self.gui_cfg.getNumInspections()):
            self.all_checkboxes.append(self.gui_cfg.getCheckDict(index))

        # All of the comments logic
        # Dictionaries stored by inspection index
        self.all_comments = []

        for index in range(self.gui_cfg.getNumInspections()):
            self.all_comments.append(self.gui_cfg.getCommentDict(index))

        self.data_lists = {
                'test_results': [],
                'test_completion': []
                }

        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'].append(self.data_dict['test{}_pass'.format(i+1)])
            self.data_lists['test_completion'].append(self.data_dict['test{}_completed'.format(i+1)])

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
            #message = "add_new_user_ID;{'user_ID': {}, 'passwd': {}}".format(self.data_dict['user_ID'], passwd)
            #self.dbclient.send_request(message)



    def check_if_new_board(self):
        logging.info("DataHolder: Checking if serial is a new board")
        print("testing if new board")

        sn = self.get_serial_ID()
        user = self.data_dict['user_ID']
        comments = 'Checked in during Visual Inspection'
        is_new_board = self.data_sender.is_new_board(sn)
        print(is_new_board)

        if is_new_board == True:
            in_id = self.data_sender.add_new_board(sn, user, comments)
            if in_id:
                print('Board added to Database')
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'This is a new board, it has been checked in. Check In ID:' + in_id

        else:
            prev_results, test_names = self.data_sender.get_previous_test_results(sn)
            if prev_results:
                self.data_dict['test_names'] = test_names
                self.data_dict['prev_results'] = prev_results
            else:
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'No tests have been run on this board.'



#        # Send request for query
#        self.data_dict['is_new_board'] = self.test_new_board(self.get_serial_ID())
#        print("result received:", self.data_dict['is_new_board'])
#        if self.data_dict['is_new_board'] == False:
#            prev_results = self.data_sender.get_previous_test_results(self.get_serial_ID())
#            #message = "get_previous_test_results;{'serial_number': {}}".format(self.get_serial_ID())
#            #prev_results = self.dbclient.send_request(message)
#            for result in prev_results:
#                test_id = result[0]
#                pass_fail = result[1]
#                if pass_fail == 0:
#                    pass_fail = False
#                elif pass_fail == 1:
#                    pass_fail = True
#                for index, test in enumerate(self.data_dict['tests_run']):
#                    if test_id == test:
#                        for i in range(self.gui_cfg.getNumTest()):
#                            if index == i:
#                                self.data_dict['test{}_pass'.format(i+1)] = pass_fail
#                                self.data_dict['test{}_completed'.format(i+1)] = pass_fail
#
#        else:
#            pass


    #################################################


    def set_user_ID(self, user_ID):

        print("\n\n\n\n\nuser_ID", user_ID)

        self.data_dict['user_ID'] = user_ID
        logging.debug("DataHolder: User ID has been set.")

    ##################################################

    def set_serial_ID(self, sn):
        #self.data_sender.add_new_board(sn)
        #message = "add_new_board;{'sn': {}}".format(sn)
        #self.dbclient.send_request(message)

        self.data_dict['current_serial_ID'] = sn
        new_cfg = update_config(sn)
        self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg)
        self.num_modules = int(sn[5]) + 1
        logging.info("DataHolder: Serial Number has been set.")

    def save_image(self):
        for i in self.image_holder:
            image = self.image_holder[i]
            # Saves the image to a file
            image.save(i)


    def send_image(self):
        if self.photos == 'Top and Bottom':
            for i in self.image_holder:
                idx = int(i[-5])
                if idx == 0:
                    view = 'Top'
                else:
                    view = 'Bottom'
                print(view)
                self.data_sender.add_board_image(self.data_dict["current_serial_ID"], self.image_holder[i], view)

        if self.photos == 'Connectors':
            for i in self.image_holder:
                idx = i[14]
                self.data_sender.add_board_image(self.data_dict["current_serial_ID"], self.image_holder[i], 'Connector ' + (idx+1))

    def test_new_board(self, sn):
        logging.info("DataHolder: Checking if serial is a new board")
        return self.data_sender.is_new_board(sn)
        #message = "is_new_board;{'sn': {}}".format(sn)
        #return self.dbclient.send_request(message)



    ##################################################

    def get_serial_ID(self):
        return self.data_dict['current_serial_ID']

    #################################################

    # Future method to send data to the database
    def send_all_to_DB(self):

        person_ID = self.data_dict['user_ID']
        comments = self.data_dict['comments']
        serial_number = self.get_serial_ID()


        for i in range(len(self.data_dict['tests_run'])):
            print("Iteration:", i)
            temp = 0
            if self.data_lists['test_results'][i]:
                temp = 1
            info_dict = {"serial_num":serial_number,"tester": person_ID, "test_type": self.tests_run[i], "successful": temp, "comments": comments}
            with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
                print(info_dict)
                json.dump(info_dict, outfile)
            self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]))
            #message = "add_test_json;{'json_file': {}/JSONFiles/storage.json, ''}"
        logging.info("DataHolder: All results sent to database.")
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


        info_dict = {"serial_num":self.get_serial_ID(),"tester": self.data_dict['user_ID'], "test_type": self.data_dict['tests_run'][index], "successful": temp, "comments": self.data_dict['comments']}

        with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
            print(info_dict)
            json.dump(info_dict, outfile)
        self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), file_path_list[index])
        #message = "add_test_json;{'json_file': {}, 'datafile_name': {}}".format("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), file_path_list[index])
        #self.dbclient.send_request(message)
        logging.info("DataHolder: Test results sent to database.")

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames()
        #users_list = self.dbclient.send_request("get_usernames")
        #print ("\n users_list:", users_list)
        return users_list

    #################################################

    # Prints all the variable values inside data_holder
    def print(self):
        print("data_dict: \n", self.data_dict, "\ninspection_data: \n", self.inspection_data, "\nimage_data:\n", self.image_data, "\nall_checkboxes: \n", self.all_checkboxes, "\nall_comments: \n", self.all_comments, '\n\n')



    #################################################

    def update_from_json_string(self, imported_json_string):
        json_dict = json.loads(imported_json_string)

        test_type = json_dict["name"]

        test_names = self.gui_cfg.getTestNames()

        current_test_idx = self.gui_cfg.getTestIndex()
        print("current_test_idx: {}".format(current_test_idx))

        with open("{}/JSONFiles/Current_{}_JSON.json".format(PythonFiles.__path__[0], test_names[current_test_idx].replace(" ", "").replace("/", "")), "w") as file:
            json.dump(json_dict['data'], file)
        self.data_dict['user_ID'] = json_dict["tester"]
        self.data_dict['current_serial_ID'] = json_dict["board_sn"]
        self.data_dict['test{}_completed'.format(current_test_idx+1)] = True
        self.data_dict['test{}_pass'.format(current_test_idx+1)] = json_dict["pass"]

        # Updates the lists
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'][i] = self.data_dict['test{}_pass'.format(i+1)]
            self.data_lists['test_completion'][i] = self.data_dict['test{}_completed'.format(i+1)]

        self.send_to_DB(current_test_idx)

        logging.info("DataHolder: Test results have been saved")

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

    ################################################

    # Keeps the login information stored
    def data_holder_new_test(self):

        self.data_dict = {
                'user_ID': self.data_dict['user_ID'],
                'test_stand': str(socket.gethostname()),
                'current_serial_ID': self.data_dict['current_serial_ID'],
                'comments': "_",
                'is_new_board': False,
                'prev_results': None,
                'test_names': None,
                'checkin_id': None,
                'tests_run': [str(i + 1) for i in range(self.getNumTest())],
                }
        for i in range(self.gui_cfg.getNumTest()):
            self.data_dict["test{}_completed".format(i+1)] = False
            self.data_dict["test{}_pass".format(i+1)] = False


        self.image_holder = {}

        self.inspection_data = {
                'board_chipped_bent': False,
                'wagon_connection_pin_bent': False,
                'engine_connection_pin_bent': False,
                'visual_scratches': False,
                'inspection_comments': "_"
                }

        self.data_lists = {
                'test_results': [],
                'test_completion': []
                }

        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists['test_results'].append(self.data_dict['test{}_pass'.format(i+1)])
            self.data_lists['test_completion'].append(self.data_dict['test{}_completed'.format(i+1)])

        logging.info("DataHolder: DataHolder Information has been reset for a new test.")

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

    ################################################

#################################################################################


