import logging

logger = logging.getLogger('HGCAL_VI')
# Class to handle creation of different types of GUIs based on which board we want to test
# This class will hold all of the frame information and order them accordingly


# Responsible for interfacing with the configuration file
class GUIConfig():

    # Loads in a config file with board type name
    # Information about board tests and database are stored within the config
    def __init__(self, board_cfg):
        self.board_cfg = board_cfg
        self.current_idx = 1

        self.configure()


    # Create the GUI instance based off testing information
    def configure(self):

        # Possibly do something special here if need be

        logger.info("Instance of {} GUI created.".format(self.getGUIType()))


    # Get serial check safe attribute
    def getSerialCheckSafe(self):
        return self.board_cfg["SerialCheckSafe"]

    def getUseScanner(self):
        return self.board_cfg["UsingScanner"]

    def getNumInspections(self):
        return len(self.board_cfg['InspectionTest'])

    def getCheckDict(self, inspect_num):
        return self.board_cfg["InspectionTest"][inspect_num]['checkboxes']

    def getCommentDict(self, inspect_num):
         return self.board_cfg["InspectionTest"][inspect_num]['comments']


    # Get database info for getting and posting test results
    def getDBInfo(self, key=None):
        if key is None:
            return self.board_cfg["DBInfo"]
        else:
            return self.board_cfg["DBInfo"][key]
    
    # Returns true if the database should be used
    def get_if_use_DB(self):
        return self.board_cfg['DBInfo']['use_database']

    def getGUIType(self):
        return self.board_cfg["GUIType"]

    def getTestHandler(self):
        return self.board_cfg["TestHandler"]

    def getUsers(self):
        return self.board_cfg["People"]

    ################################
    
    # Necessary to be stored for the current test
    # This allows for more advanced test navigation

    def setTestIndex(self, idx):
        self.current_idx = idx

    def getTestIndex(self):
        return self.current_idx

    ################################
    
    # Returns the names for the physical tests from config
    def getPhysicalNames(self):
        try:
            return [test["name"] for test in self.board_cfg["PhysicalTest"]]
        except:
            return []

    def getTestNames(self):
        try:
            return [test["name"] for test in self.board_cfg["Test"]]
        except:
            print("Unable to return test names. Check to see if test['name'] is empty")
            logging.debug("Unable to return test names. Check to see if test['name'] is empty")
            return []
