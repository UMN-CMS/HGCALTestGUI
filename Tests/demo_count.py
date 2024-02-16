import time, sys, os, random

sys.path.append("{}/Tests/".format(os.getcwd()))

from Test import Test

# Simple test counting from 1 to 10 for demo purposes
# This is an example of how a test can be written to run locally
# Note the inheritance of the test demo class for full functionality
class counting(Test):

    def __init__(self, conn, board_sn=-1, tester="Jane Doe", config_path = "./Tests/test_configs/counting.yaml"):

        # Test metadata for storage
        self.info_dict = {'name': "Count to 10", 'board_sn': board_sn, 'tester': tester}

        # One end of a multiprocessing pipe to send output to GUI console
        self.conn = conn

        # Initialization of the parent test object handles result saving,
        # message passing between tests and GUI
        # Note that tests are run on initialization of the Test object
        Test.__init__(self, self.run_count, self.info_dict, conn, config_path)
        
        self.run()

    def initialization(self):

        # Do some initialization of test setup
        time.sleep(3)

    def run_count(self, test_cfg):

        self.initialization()

        self.send("Beginning count test:")

        max_range = test_cfg["max_range"]+1

        try: 
            for i in range(1, max_range):
                self.send("{}".format(i))
                time.sleep(1)

                # Simulating a failure case to show how that is handled by the Test API 
                if random.random() < 0.03:
                    raise Exception("This is a simulated random failure case")
        except:
            self.send("Something went wrong while counting to {}... Don't worry, this is a simulated test failure to illustrate failure handling :)".format(max_range-1))
            test_passed = False
            result = "Test failed, maximum value counted to is {}".format(i)
            data = {"StartVal": 1, "EndVal": i}
            return test_passed, result, data

        test_passed = True
        data = {"StartVal": 1, "EndVal": i}
        result = "Test passed!"
        self.send("Done.")

        return test_passed, result, data

