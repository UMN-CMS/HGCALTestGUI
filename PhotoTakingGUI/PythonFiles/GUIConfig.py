
# Class to handle creation of different types of GUIs based on which board we want to test
# This class will hold all of the frame information and order them accordingly

class GUIConfig():

    # Loads in a config file with board type name
    # Information about board tests and database are stored within the config
    def __init__(self, board_cfg):
        self.board_cfg = board_cfg
        self.current_idx = 1

        self.configure()

    # Return true if GUI should use the database
    def get_if_use_DB(self):
        return self.board_cfg['DBInfo']['use_database']


    # Create the GUI instance based off testing information
    def configure(self):

        # Possibly do something special here if need be

        print("Instance of {} GUI created.".format(self.getGUIType()))

    # Get number of tests to define order of scenes and sidebar
    def getNumTest(self):
        return len(self.board_cfg["Test"])

    # Get number of tests to define order of scenes and sidebar
    def getTests(self):
        return self.board_cfg["Test"]

    # Get database info for getting and posting test results
    def getDBInfo(self, key=None):
        if key is None:
            return self.board_cfg["DBInfo"]
        else:
            return self.board_cfg["DBInfo"][key]

    def getGUIType(self):
        print(self.board_cfg)
        return self.board_cfg["GUIType"]

    def setTestIndex(self, idx):
        self.current_idx = idx

    def getTestIndex(self):
        return self.current_idx


    def getTestNames(self):
        return [test["name"] for test in self.board_cfg["Test"]]

    # Returns a dictionary of each photo required
    def getPhotoList(self):
        return self.board_cfg['Photo']
        
