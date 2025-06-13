import requests
import json
import socket
import base64
import os
from PIL import Image
import logging

from io import BytesIO
# from read_barcode import read_barcode

logger = logging.getLogger('HGCAL_Photo.PythonFiles.Data.DBSender')


class DBSender():

    def __init__(self, gui_cfg, main_path):
        self.gui_cfg = gui_cfg
        self.main_path = main_path

        # Predefined URL for the database
        self.db_url = self.gui_cfg.getDBInfo("baseURL")

        # If True, use database
        # If False, run in "offline" mode
        self.use_database = self.gui_cfg.get_if_use_DB()



    # Since we will have the tester in a separate room, we need to do modify the http requests
    # This proxy will be used to make http requests directly to cmslab3 via an ssh tunnel
    def getProxies(self):
        if (self.use_database):
            if "umncmslab" in socket.gethostname():
                return None

            return {"http": "http://127.0.0.1:8080"}

        # If not using the database, then...
        else:
            pass

    def add_new_user_ID(self, user_ID, passwd):

        if (self.use_database):

            try:
                r = requests.post('{}/add_tester2.py'.format(self.db_url), data= {'person_name':user_ID, 'password': passwd})
            except Exception as e:
                logger.error("Unable to add the user to the database. Username: {}. Check to see if your password is correct.".format(user_ID))


        # If not using the database, use this...
        else:
            pass

    def decode_label(self, full_id):
        
        if len(full_id) != 15:
            logger.warning("Invalid label scanned")
            label_info = None
        else:
            r = requests.post('{}/../LabelDB/decode_label.py'.format(self.db_url), data={'label': full_id})
            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error("There was an issue with the web API script `decode_label.py`. Check that the label library has been updated for the web API.")

            temp = []

            for i in range(begin, end):
                temp.append(lines[i])
            
            label_info = {'Major Type': temp[0], 'Subtype': temp[1], 'SN': temp[2]}

        return label_info

    # Returns an acceptable list of usernames from the database
    def get_usernames(self):
        if (self.use_database):
            r = requests.get('{}/get_usernames.py'.format(self.db_url))
            lines = r.text.split('\n')

            try:
                begin = lines.index("Begin") + 1
                end = lines.index("End")
            except:
                logger.error("There was an issue with the web API script `get_usernames.py`. There is likely a syntax error in an associated web API script.")

            usernames = []

            for i in range(begin, end):
                temp = lines[i]
                usernames.append(temp)

            return usernames

        # If not using database...
        else:

            return ['User1', 'User2', 'User3']

    # writes image to server disk and saves the name in the database
    def add_board_image(self, full_id, image, view):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        encodedImage = base64.b64encode(buffered.getvalue())
        r = requests.post('{}/add_board_image~.py'.format(self.db_url), data={"full_id": full_id, "image": encodedImage, "view": view})

        lines = r.text.split('\n')

        saved_image = False
        for l in lines:
            if 'File received successfully!' in l:
                saved_image = True
                logger.info('Image uploaded successfully!')

        if saved_image == False:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk("{}/PythonFiles/Images".format(self.main_path)):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            logger.error("Failed to save image, opting for local file storage...")
            logger.info("Image directory size is %s megabytes" % (total_size/1000000))
            if total_size < 5000000000:
                image.save("{}/PythonFiles/Images/{}_{}.png".format(self.main_path, full_id, view))
                logger.info("Image saved to local disk successfully.")
            else:
                raise "Image Directory is too full, please upload and delete images."
            

    def upload_local_board(self, path, full_id, view):
        image = Image.open(path)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        encodedImage = base64.b64encode(buffered.getvalue())
        r = requests.post('{}/add_board_image~.py'.format(self.db_url), data={"full_id": full_id, "image": encodedImage, "view": view})

        lines = r.text.split('\n')

        for l in lines:
            if 'File received successfully!' in l:
                logger.info('Image uploaded successfully, deleting local file...')
                os.remove(path)
                logger.info('File removed.')



    # Returns a dictionary of booleans
    # Whether or not DB has passing results
    def get_previous_test_results(self, full_id):

        r = requests.post('{}/get_previous_test_results.py'.format(self.db_url), data={"full_id": str(full_id)})

        lines = r.text.split('\n')

        try:
            begin1 = lines.index("Begin1") + 1
            end1 = lines.index("End1")
            begin2 = lines.index("Begin2") + 1
            end2 = lines.index("End2")
            begin3 = lines.index("Begin3") + 1
            end3 = lines.index("End3")
        except:
            logger.error("There was an issue with the web API script `get_previous_test_results.py`. There is likely a syntax error in an associated web API script.")

        tests_run = []
        outcomes = []
        poss_tests = []

        for i in range(begin1, end1):
            tests_run.append(lines[i])
        for i in range(begin2, end2):
            outcomes.append(lines[i])
        for i in range(begin3, end3):
            poss_tests.append(lines[i])

        tests_passed = []
        for i in range(len(tests_run)):
            tests_passed.append([tests_run[i], outcomes[i]])

        return tests_passed, poss_tests


    # Posts a new board with passed in full id
    # this is only called if the full id isn't recognized by is_new_board
    def add_new_board(self, full, user_id, comments):
        r = requests.post('{}/add_module2.py'.format(self.db_url), data={"full_id": str(full), 'manufacturer': "None"})
        r = requests.post('{}/board_checkin2.py'.format(self.db_url), data={"full_id": str(full), 'person_id': str(user_id), 'comments': str(comments)})


        try:
            lines = r.text.split('\n')

            begin = lines.index("Begin") + 1
            end = lines.index("End")

            in_id = None

            for i in range(begin, end):
                in_id = lines[i]
        except:
            in_id = None

        return in_id

    # checks if the board is in the database
    def is_new_board(self, full):
        r = requests.post('{}/is_new_board.py'.format(self.db_url), data={"full_id": str(full)})

        lines = r.text.split('\n')

        try:
            begin = lines.index("Begin") + 1
            end = lines.index("End")
        except:
            logger.error("There was an issue with the web API script `is_new_board.py`. There is likely a syntax error in an associated web API script.")


        for i in range(begin, end):

            if "True" in lines[i]:
                return True
            elif "False" in lines[i]:
                return False


    def add_test_json(self, json_file, datafile_name):
        load_file = open(json_file)
        results = json.load(load_file)
        load_file.close()

        datafile = open(datafile_name, "rb")

        attach_data = {'attach1': datafile}

        if (self.use_database):
            r = requests.post('{}/add_test_json.py'.format(self.db_url), data = results, files = attach_data)

        else:
            pass

