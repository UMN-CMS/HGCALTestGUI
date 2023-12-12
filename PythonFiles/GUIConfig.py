# Class to handle creation of different types of GUIs based on which board we want to test
# This class will hold all of the frame information and order them accordingly
# Responsible for interfacing with the configuration file


class GUIConfig:
    # Loads in a config file with board type name
    # Information about board tests and database are stored within the config
    def __init__(self, board_cfg):
        self.board_cfg = board_cfg
        self.configure()

    def configure(self):
        # Possibly do something special here if need be
        print("Instance of {} GUI created.".format(self.getGUIType()))

    # Get serial check safe attribute
    def getSerialCheckSafe(self):
        return self.board_cfg["SerialCheckSafe"]

    # Get number of tests to define order of scenes and sidebar
    def getNumTest(self):
        return len(self.board_cfg["Tests"])

    def getUseScanner(self):
        return self.board_cfg["UsingScanner"]

    def getTests(self):
        return self.board_cfg["Tests"]

    # Get database info for getting and posting test results
    def getDBInfo(self, key=None):
        if key is None:
            return self.board_cfg["DBInfo"]
        else:
            return self.board_cfg["DBInfo"][key]

    # Returns true if the database should be used
    def get_if_use_DB(self):
        return self.board_cfg["DBInfo"]["use_database"]

    def getGUIType(self):
        print(self.board_cfg)
        return self.board_cfg["GUIType"]

    def getTestHandler(self):
        return self.board_cfg["TestHandler"]

    def getTestNames(self):
        try:
            return [test["name"] for test in self.board_cfg["Tests"]]
        except:
            print("Unable to return test names. Check to see if test['name'] is empty")
            logging.debug(
                "Unable to return test names. Check to see if test['name'] is empty"
            )
            return []

