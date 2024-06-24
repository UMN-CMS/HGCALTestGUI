#!/usr/bin/python3

'''
Utility class for running HGCAL tests via GUI

This class assumes that your results dictionary stores only certain fields.
Make sure that you are syncronizing your return from the test function with that of the test class.
This should return a three object tuple: pass/fail (bool), result (string, human readable test outcome), data (dictionary)
'''

import json
import os
import yaml

from datetime import datetime

class Test():
    
    def __init__(self, test_func, info_dict, conn, config_path):

        self.conn = conn
        self.test_func = test_func

        self.load_config(config_path)

        self.send("Initializing a test")

        # All information that should be provided from the GUI to every test
        try:
            self.name = info_dict['name']
            self.board_sn = info_dict['board_sn']
            self.tester = info_dict['tester']
        except:
            self.send("Please provide the name of the test, board serial number, and tester name")


    def run(self):
        # Info that will be provided from running the test
        self.passed, self.result, self.data = self.run_test(self.test_func, self.test_cfg)

        # Package up results into a dictionary for parsing into a JSON
        self.results = {'name': self.name, 'board_sn': self.board_sn, 'tester': self.tester, 'pass': self.passed, 'data': self.data, 'result': self.result, 'time': str(datetime.now())}

        self.send(self.dump_results())
        
        self.save_results()

        self.send_results(self.result)

    # Dump results in JSON format for uploading to the database
    def dump_results(self):
        return json.dumps(self.results)

    # Save JSON file under <serial_number>_<test_name>.json
    def save_results(self):
        save_dir = "./jsons"
        self.send("\nSaving results to {}\n".format("./jsons/{0}/{0}_{1}.json".format(self.name.replace(" ",""), self.board_sn)))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        if not os.path.exists("{}/{}".format(save_dir, self.name.replace(" ",""))):
            os.makedirs("{}/{}".format(save_dir, self.name.replace(" ","")))
        with open("./jsons/{0}/{0}_{1}.json".format(self.name.replace(" ",""), self.board_sn), "w") as f:
            f.write(self.dump_results())

        f.close()

    # Handler for sending test printouts in whatever fashion is necessary
    def send(self, message):
        if self.conn is None:
            print(message)
        else:
            self.conn.send("print ; " + message)

        # Other types of connections to be implemented: MP pipes, os pipes

    # Need separate send function for results
    def send_results(self):

        if self.conn is None:
            print(self.results)
        else:
            self.conn.send("JSON ; " + json.dumps(self.results))
    

    # Get results as a python dictionary
    def get_results(self):
        self.send(self.results)
        return self.results

    # Send results via the PUB Server
    #def send_results(self):
    #    self.send("Test Outcome: " + self.results["result"])

    # Loading configuration needed by test function, needs to be a yaml file
    # Returns dictionary object that should be taken as an argument in test function
    def load_config(self, config_path):
        self.test_cfg = yaml.safe_load(open(config_path, "r"))

    # Function for running your test, kwargs must agree with defined kwargs for your test
    # This function assumes that the output of the test will be the pass/fail condition (bool)
    # and a dictionary (of any depth) containing the extra data to store for the test
    def run_test(self, test_func, test_config):
        self.send("Running the test:")
        return test_func(test_config)


if __name__ ==  "__main__":

    import argparse

    parser = argparse.ArgumentParser(prog="Test Demo", description="Run your own tests by giving --config and --test command line options", epilog="Both config and test flags must be set to run your test")

    parser.add_argument("-c", "--config",   dest="config_path", action="store", type=str, help="path to your test configuration file")

    args = parser.parse_args()

    test_cfg = yaml.safe_load(open(args.config_path, "r"))
    test_path = test_cfg["test_path"].split(".py")[0].replace("/", ".")
    test_class_name = test_cfg["test_class"]

    test_mod = __import__(test_path, fromlist=[test_class_name])
    test_class = getattr(test_mod, test_class_name)

    conn = None
    board_sn = 123
    tester = "Demo Tester"

    test_class(conn, board_sn, tester, args.config_path)
    

