################################################################################
import json, logging, socket, PythonFiles, copy, os
import requests
from PythonFiles.Data.DBSender import DBSender
from PythonFiles.update_config import update_config

logger = logging.getLogger(__name__)


class DataHolder:
    def __init__(self, gui_cfg):
        self.gui_cfg = gui_cfg
        self.data_sender = DBSender(gui_cfg)

        self.current_active_test = gui_cfg.getTests()[0]["name"]
        self.current_serial = ""
        self.current_user_id = ""

        self.tests = {
            test["name"]: {
                "test_data": test,
                "id": test["name"],
                "type": test["type"],
                "idx": i,
                "completed": False,
                "passed": False,
                "result": None,
                "comments": "",
            }
            for i, test in enumerate(self.gui_cfg.getTests())
        }

        self.total_tests = len(self.tests)

    def getNumTests(self, idx):
        return self.total_tests

    def getByIndex(self, idx):
        return next(x for x in self.tests.values() if x["idx"] == idx)

    def getActiveTest(self):
        return self.tests[self.current_active_test]

    def getTests(self):
        return sorted(list(self.tests.values()), key=lambda x: x["idx"])

    def get_total_test_num(self):
        return self.total_test_num

    def get_use_scanner(self):
        return self.gui_cfg.getUseScanner()

    def add_new_user_name(self, user_ID, passwd):
        self.current_user_id = user_ID
        is_new_user_ID = True

        for item in self.get_all_users():
            if self.current_user_id == item:
                is_new_user_ID = False
        if is_new_user_ID:
            self.data_sender.add_new_user_ID(self.current_user_id, passwd)

    def check_if_new_board(self):
        logger.info("Checking if serial is a new board")
        sn = self.get_serial_ID()
        user = self.current_user_id
        comments = "Checked in during general testing"
        is_new_board = self.data_sender.is_new_board(sn)

        if is_new_board == True:
            in_id = self.data_sender.add_new_board(sn, user, comments)
            if in_id:
                self.data_dict["test_names"] = None
                self.data_dict["prev_results"] = (
                    "This is a new board, it has been checked in. Check In ID:" + in_id
                )

        else:
            prev_results, test_names = self.data_sender.get_previous_test_results(sn)
            if prev_results:
                self.data_dict["test_names"] = test_names
                self.data_dict["prev_results"] = prev_results
            else:
                self.data_dict["test_names"] = None
                self.data_dict["prev_results"] = "No tests have been run on this board."

    def set_user_ID(self, user_ID):
        self.current_user_id = user_ID
        logger.debug(f"User ID has been set to {self.current_user_id}.")


    def set_serial_ID(self, sn):
        self.data_dict["current_serial_ID"] = sn
        if self.gui_cfg.getSerialCheckSafe():
            new_cfg = update_config(sn)
            self.gui_cfg = new_cfg
        self.data_holder_new_test()
        self.data_sender = DBSender(self.gui_cfg)
        logger.info("DataHolder: Serial Number has been set.")

    def test_new_board(self, sn):
        logger.info("DataHolder: Checking if serial is a new board")
        return self.data_sender.is_new_board(sn)
        # message = "is_new_board;{'sn': {}}".format(sn)
        # return self.dbclient.send_request(message)

    ##################################################

    def get_serial_ID(self):
        return self.data_dict["current_serial_ID"]

    #################################################

    # Future method to send data to the database
    def send_all_to_DB(self):
        person_ID = self.data_dict["user_ID"]
        comments = self.data_dict["comments"]
        serial_number = self.get_serial_ID()

        for i in range(len(self.data_dict["tests_run"])):
            print("Iteration:", i)
            temp = 0
            if self.data_lists["test_results"][i]:
                temp = 1
            info_dict = {
                "serial_num": serial_number,
                "tester": person_ID,
                "test_type": self.tests_run[i],
                "successful": temp,
                "comments": comments,
            }
            with open(
                "{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w"
            ) as outfile:
                print(info_dict)
                json.dump(info_dict, outfile)
            self.data_sender.add_test_json(
                "{}/JSONFiles/storage.json".format(PythonFiles.__path__[0])
            )
            # message = "add_test_json;{'json_file': {}/JSONFiles/storage.json, ''}"
        logger.info("DataHolder: All results sent to database.")

    #################################################

    def send_to_DB(self, test_run):
        index = test_run

        test_names = list(self.tests)

        file_path_list = []

        for name in test_names:
            file_path_list.append(
                "{}/JSONFiles/Current_{}_JSON.json".format(
                    PythonFiles.__path__[0], name.replace(" ", "").replace("/", "")
                )
            )

        # Converts self.test_results[index] into 1/0 instead of bool
        temp = 0
        if self.data_lists["test_results"][index]:
            temp = 1

        info_dict = {
            "serial_num": self.get_serial_ID(),
            "tester": self.data_dict["user_ID"],
            "test_type": self.data_dict["tests_run"][index],
            "successful": temp,
            "comments": self.data_dict["comments"],
        }

        with open(
            "{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), "w"
        ) as outfile:
            print(info_dict)
            json.dump(info_dict, outfile)
        self.data_sender.add_test_json(
            "{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]),
            file_path_list[index],
        )
        # message = "add_test_json;{'json_file': {}, 'datafile_name': {}}".format("{}/JSONFiles/storage.json".format(PythonFiles.__path__[0]), file_path_list[index])
        # self.dbclient.send_request(message)
        logger.info("DataHolder: Test results sent to database.")

    #################################################

    def get_all_users(self):
        users_list = self.data_sender.get_usernames()
        # users_list = self.dbclient.send_request("get_usernames")
        # print ("\n users_list:", users_list)
        return users_list

    #################################################

    # Prints all the variable values inside data_holder
    def print(self):
        print(
            "data_dict: \n",
            self.data_dict,
            "\nall_checkboxes: \n",
            self.all_checkboxes,
            "\nall_comments: \n",
            self.all_comments,
            "\n\n",
        )

    #################################################

    def update_from_json_string(self, imported_json_string):
        json_dict = json.loads(imported_json_string)

        test_type = json_dict["name"]

        test_names = list(self.tests)

        current_test_idx = self.gui_cfg.getTestIndex() - 1
        print("current_test_idx: {}".format(current_test_idx))

        with open(
            "{}/JSONFiles/Current_{}_JSON.json".format(
                PythonFiles.__path__[0],
                test_names[current_test_idx].replace(" ", "").replace("/", ""),
            ),
            "w",
        ) as file:
            json.dump(json_dict["data"], file)
        self.data_dict["user_ID"] = json_dict["tester"]
        self.data_dict["current_serial_ID"] = json_dict["board_sn"]
        self.data_dict["test{}_completed".format(current_test_idx + 1)] = True
        self.data_dict["test{}_pass".format(current_test_idx + 1)] = json_dict["pass"]

        # Updates the lists
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists["test_results"][i] = self.data_dict[
                "test{}_pass".format(i + 1)
            ]
            self.data_lists["test_completion"][i] = self.data_dict[
                "test{}_completed".format(i + 1)
            ]

        if self.gui_cfg.get_if_use_DB():
            self.send_to_DB(current_test_idx)

        logger.info("DataHolder: Test results have been saved")

    def getGUIcfg(self):
        return self.gui_cfg

    ################################################

    # Keeps the login information stored
    def data_holder_new_test(self):
        self.data_dict = {
            "user_ID": self.data_dict["user_ID"],
            "test_stand": str(socket.gethostname()),
            "current_serial_ID": self.data_dict["current_serial_ID"],
            "queue": self.data_dict["queue"],
            "comments": "_",
            "prev_results": None,
            "test_names": None,
            "checkin_id": None,
            "tests_run": [str(i + 1) for i in range(self.getNumTest())],
        }

        self.inspection_data = {
            "board_chipped_bent": False,
            "wagon_connection_pin_bent": False,
            "engine_connection_pin_bent": False,
            "visual_scratches": False,
            "inspection_comments": "_",
        }

        self.data_lists = {
            "test_results": [],
            "test_completion": [],
            "physical_results": [],
            "physical_completion": [],
        }

        self.total_test_num = 0

        for i in range(self.gui_cfg.getNumTest()):
            self.data_dict["test{}_completed".format(i + 1)] = False
            self.data_dict["test{}_pass".format(i + 1)] = False

        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_dict["physical{}_completed".format(i + 1)] = False
            self.data_dict["physical{}_pass".format(i + 1)] = False

        self.ptest_criteria = {}
        self.ptest_names = self.gui_cfg.getPhysicalNames()

        for i in range(self.gui_cfg.getNumPhysicalTest()):
            self.data_lists["physical_results"].append(
                self.data_dict["physical{}_pass".format(i + 1)]
            )
            self.data_lists["physical_completion"].append(
                self.data_dict["physical{}_completed".format(i + 1)]
            )

            temp_dict = {
                "{}".format(i + 1): self.gui_cfg.getPhysicalTestRequirements(i),
            }

            self.ptest_criteria.update(temp_dict)

            self.total_test_num = self.total_test_num + 1

        # print(self.data_dict)
        for i in range(self.gui_cfg.getNumTest()):
            self.data_lists["test_results"].append(
                self.data_dict["test{}_pass".format(i + 1)]
            )
            self.data_lists["test_completion"].append(
                self.data_dict["test{}_completed".format(i + 1)]
            )

            self.total_test_num = self.total_test_num + 1

        logger.info("DataHolder: DataHolder Information has been reset for a new test.")

        self.gui_cfg.setTestIndex(1)

        self.current_test_idx = self.gui_cfg.getTestIndex()

    ################################################
