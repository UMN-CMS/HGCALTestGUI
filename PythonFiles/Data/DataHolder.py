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
                "id": test["name"],
                "idx": i,
                "test_data": test,
                "type": test["type"],
            }
            for i, test in enumerate(self.gui_cfg.getTests())
        }
        self.total_tests = len(self.tests)
        self.test_states = None
        self.resetTestStates()

    def resetTestStates(self):
        self.test_states = {
            tid: {
                "completed": False,
                "passed": False,
                "result": None,
                "comments": "",
            }
            for tid in self.tests
        }

    def getNumTests(self):
        return self.total_tests

    def getByIndex(self, idx):
        return next(x for x in self.tests.values() if x["idx"] == idx)

    def getTest(self, tid):
        return self.tests[tid]

    def getTestIdx(self, tid):
        return self.tests[tid]["idx"]

    def getTestState(self, tid):
        return self.test_states[tid]

    def updateTest(self, tid, passed=None, result=None, comment=None):
        logger.info(f"Updating state for test {tid}")
        for k, v in [
            ("passed", passed),
            ("result", result),
            ("comment", comment),
        ]:
            if v is not None:
                if tid not in self.test_states:
                    self.test_states[tid] = {}
                self.test_states[tid][k] = v
                logger.info(f"Updated {tid}[{}] = {v}")

    def getActiveTest(self):
        return self.tests[self.current_active_test]

    def getActiveSerial(self):
        return self.current_serial

    def getActiveUser(self):
        return self.current_user_id

    def getTests(self):
        return sorted(list(self.tests.values()), key=lambda x: x["idx"])

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
        else:
            prev_results, test_names = self.data_sender.get_previous_test_results(sn)
            mapping = dict(zip(test_names, prev_results))


    def set_user_ID(self, user_ID):
        self.current_user_id = user_ID
        logger.info(f"User ID has been set to {self.current_user_id}.")

    def set_serial_ID(self, sn):
        self.current_serial = sn
        if self.gui_cfg.getSerialCheckSafe():
            new_cfg = update_config(sn)
            self.gui_cfg = new_cfg
        self.resetTestStates()
        self.data_sender = DBSender(self.gui_cfg)
        logger.info("DataHolder: Serial Number has been set.")

    def test_new_board(self, sn):
        logger.info("DataHolder: Checking if serial is a new board")
        return self.data_sender.is_new_board(sn)

    def get_serial_ID(self):
        return self.getActiveSerial()

    def send_all_to_DB(self):
        person_ID = self.getActiveUser()
        serial_number = self.getActiveSerial()
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

    def send_to_DB(self, test_id):
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
            "serial_num": self.getActiveSerial(),
            "tester": self.getActiveUser(),
            "test_type": test_id,
            "successful": temp,
            "comments": self.test[test_id]["comments"],
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
        return users_list

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
