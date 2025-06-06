import logging
# Class to handle creation of different types of GUIs based on which board we want to test
# This class will hold all of the frame information and order them accordingly

logger = logging.getLogger('HGCALTestGUI')


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


    # Get number of tests to define order of scenes and sidebar
    def getNumTest(self):
        return len(self.board_cfg["Test"])

    # Get the number of tests that require physical input
    def getNumPhysicalTest(self):
        return len(self.board_cfg["PhysicalTest"])

    # Returns the information necessary for physical test
    # Formatted as a dictionary
    def getPhysicalTestRequirements(self, num):
        index = 0
        for ptest in self.board_cfg["PhysicalTest"]:
            if index == num:
                return ptest

        return None

    def getUseScanner(self):
        return self.board_cfg["UsingScanner"]

    def getTests(self):
        return self.board_cfg["Test"]

    def getPhysicalTests(self):
        return self.board_cfg["PhysicalTest"]

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
            logger.error("Unable to return test names from config. Check to see if test['name'] is empty")
            return []
