################################################################################
import json, logging, socket, PythonFiles, copy, os
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config
from collections import OrderedDict

logger = logging.getLogger('HGCAL_VI.PythonFiles.Data.DataHolder')

class DataHolder():

    #################################################

    # List of the variables being held by data holder
    def __init__(self, gui_cfg):
        
        # Object for taking care of instantiation for different test types
        self.gui_cfg = gui_cfg

        # Object that sends information to the database
        self.data_sender = DBSender(gui_cfg)
        
        self.data_dict = {
                'user_ID': "_",
                'test_stand': str(socket.gethostname()),
                'current_full_ID': "-1BAD",
                'comments': "_",
                'in_id': None,
                'is_new_board': False,
                'test_names': '',
                'prev_results': '',
                'manufacturer': 'None',
                }

        # for the visual inspection component
        self.inspection_data = OrderedDict({
                'board_bent': False,
                'board_broken': False,
                'component_missing': False,
                'component_broken': False,
                'inspection_comments': '_'
                })

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

    #################################################

    def get_check_dict(self, idx):
        return self.all_checkboxes[idx]

    def set_check_dict(self, idx, value):
        self.all_checkboxes[0][idx]['value'] = value
        self.inspection_data[list(self.inspection_data.keys())[idx]] = value

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

        if is_new_user_ID:
            self.data_sender.add_new_user_ID(self.data_dict['user_ID'], passwd)        

    def get_manufacturers(self):
        return self.data_sender.get_manufacturers()

    def set_manufacturer_id(self, manufacturer):
        self.data_dict['manufacturer']  = manufacturer

    def add_component(self, barcode):
        self.data_sender.add_component(barcode, self.get_full_ID())


    # when a board gets entered, this function checks if it's new
    def check_if_new_board(self):
        logger.info("Checking if full id is a new board...")

        full = self.get_full_ID()
        #returns true if the board is new, false if not
        is_new_board, in_id = self.data_sender.is_new_board(full)

        comments = self.data_dict['comments']
        self.data_dict['is_new_board'] = is_new_board
        
        if is_new_board == True:
            logger.info('Board is new, checking it in.')
            user = self.data_dict['user_ID']
            # data sender's add new board function returns the check in id
            self.data_dict['in_id'] = self.data_sender.add_new_board(full, user, comments, self.data_dict['manufacturer'])

        else:
            # if the board is not new, this returns the previous testing information on the board
            logger.info('Board has already been checked in, getting previous results.')
            prev_results, test_names = self.data_sender.get_previous_test_results(full)
            if prev_results:
                self.data_dict['test_names'] = test_names
                self.data_dict['prev_results'] = prev_results
            else:
                self.data_dict['test_names'] = None
                self.data_dict['prev_results'] = 'No tests have been run on this board.'
            self.data_dict['in_id'] = in_id

        return self.data_dict['in_id']

    def decode_label(self, full_id):
        self.label_info = self.data_sender.decode_label(full_id)

    def check_for_ldo(self):
        got_code = self.data_sender.check_for_ldo(self.get_full_ID())
        return got_code

    #################################################


    def set_user_ID(self, user_ID):
 
        self.data_dict['user_ID'] = user_ID 
        logger.info("User ID set to %s" % user_ID)

    ##################################################

    def set_comments(self, comments):
 
        self.data_dict['comments'] = comments
        logger.info("Comments have been entered.")

    def set_inspection_comments(self, comments):

        self.inspection_data['inspection_comments'] = comments
        logger.info('Comments entered for VI test')

    ##################################################

    def set_full_ID(self, full):
        if full[3] != self.data_dict['current_full_ID'][3]:
            new_cfg = update_config(full)
            self.gui_cfg = new_cfg

            self.data_sender = DBSender(self.gui_cfg)

        self.data_dict['current_full_ID'] = full
        self.data_holder_new_test()
        logging.info("Full ID set to %s" % full)

    def send_image(self, img_idx=0):
        self.data_sender.add_board_image(self.data_dict["current_full_ID"], open(self.image_data[img_idx], "rb"))

    #################################################

    # current method to send to the database
    def send_to_DB(self):
        test_name = "Visual Inspection"
        test_type_id = 0

        logger.info('Uploading visual inspection results...')
        info_dict = {"full_id":self.get_full_ID(),"tester": self.data_dict['user_ID'], "test_type": test_name, "successful": self.data_dict["inspection_pass"], "comments": self.data_dict['comments']}
        logger.debug(info_dict)

        with open("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w") as outfile:
            json.dump(info_dict, outfile)

        with open("{}/JSONFiles/data.json".format(PythonFiles.__path__[0]), "w") as outfile:
            json.dump(self.inspection_data, outfile)

        test_id = self.data_sender.add_test_json("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "{}/JSONFiles/data.json".format(PythonFiles.__path__[0]), self.get_full_ID())

        logging.info("Test results sent to database.")

        return test_id

    #################################################

    # sends the visual inspection json comments to the database
    def update_from_json_string(self):

        test_type = "Visual Inspection"
        test_type_id = 0

        passed = not any([x for x in self.inspection_data.values()][:-1])

        self.data_dict['inspection_completed'] = True
        self.data_dict['inspection_pass'] = int(passed)
        fid = self.get_full_ID()
        if "320EL" in fid or "320EH" in fid:
            got_code = self.check_for_ldo()
            if got_code is None or got_code == "None":
                self.data_dict['inspection_pass'] = 0

        #self.add_inspection_to_comments()
        self.data_dict['data'] = self.inspection_data

    ################################################

    def add_inspection_to_comments(self):
        if self.inspection_data['board_bent']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board is chipped or bent."
        if self.inspection_data['board_broken']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board is visibly broken"
        if self.inspection_data['component_missing']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board is missing components."
        if self.inspection_data['component_broken']:
            if self.data_dict['comments'] == "_":
                self.data_dict['comments'] = ""
            self.data_dict['comments'] = self.data_dict['comments'] + " Board component is broken."
        #if self.inspection_data['inspection_comments'] != "_":
        #    if self.data_dict['comments'] == "_":
        #        self.data_dict['comments'] = ""
        #    self.data_dict['comments'] = self.data_dict['comments'] + " User comments: " + self.inspection_data['inspection_comments']
        #    self.data_dict['inspection_comments'] = self.inspection_data['inspection_comments']


    ##################################################

    def get_full_ID(self):
        return self.data_dict['current_full_ID']

    #################################################
   
    def get_all_users(self):
        users_list = self.data_sender.get_usernames() 
        return users_list

    #################################################

    # Tracking the test index in another place and propagating to the config
    def setTestIdx(self, test_idx):
        
        self.current_test_idx = test_idx
        self.gui_cfg.setTestIndex(self.current_test_idx)

    def getTestNames(self):
        return self.gui_cfg.getTestNames()

    ################################################

    # Keeps the login information stored
    def data_holder_new_test(self): 

        self.data_dict = {
                'user_ID': self.data_dict['user_ID'],
                'test_stand': str(socket.gethostname()),
                'current_full_ID': self.get_full_ID(),
                'comments': "_",
                'is_new_board': False,
                'test_names': '',
                'prev_results': '',
                'in_id': None,
                'manufacturer': self.data_dict['manufacturer'],
                }

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

        self.data_dict["inspection_completed"] = False
        self.data_dict["inspection_pass"] = False

        self.inspection_data = {
                'board_bent': False,
                'board_broken': False,
                'component_missing': False,
                'component_broken': False,
                'inspection_comments': "_"
                }

        logger.info("DataHolder Information has been reset for a new test.")        

    ################################################

#################################################################################


