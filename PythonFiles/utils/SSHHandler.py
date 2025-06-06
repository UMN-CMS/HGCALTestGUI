import multiprocessing as mp
import subprocess as sp
import zmq, sys, os, signal, logging, json

sys.path.append("{}".format(os.getcwd()))
sys.path.append("{}/Tests".format(os.getcwd()))

# Class needed for briding the gap between request, running test
# and sending results back

# This takes the place of the REPserver and PUBServer which are
# used when tests are run via ZMQ

# Note that this process needs to start on instantiation of the GUI
# to avoid any overlapping event monitors. So, conn_trigger
# is used to trigger a new test via REQClient

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.SUBClient')

class SSHHandler:

    def __init__(self, gui_cfg, gui_cfg_host, conn_trigger, q):

        queue = mp.Queue()

        # Listen for test request
        while True:
            logger.info("New PUB proc")
            request = json.loads(conn_trigger.recv())
            process_PUB = mp.Process(target = self.task_local, args=(queue,q))
            process_PUB.start()

            if request is not None:

                desired_test = request["desired_test"]
                test_info = {"full_id": request["full_id"], "tester": request["tester"]}

                logger.info("New test proc")
                self.process_test = mp.Process(target = self.task_test, args=(queue, gui_cfg, gui_cfg_host, desired_test, test_info))
                self.process_test.start()

                # Hold until test finish
                logger.info("Joining test proc")
                self.process_test.join()

                logger.info("Terminate PUB proc")
                process_PUB.terminate()


        try:
            queue.close()

        except Exception as e:
            logger.error("PUB and test queue could not be closed: {}".format(e))

        try:
            process_PUB.terminate()
        except Exception as e:
            logger.error("PUB and test process could not be terminated: {}".format(e))

    def task_local(self, queue, q):
        # listens for incoming data and attaches the correct topic before sending it on to SUBClient
        try:
            while 1 > 0:
                prints = queue.get()
                if "Done." in prints:
                    prints = 'print ; ' + str(prints)
                    q.put(prints)

                    json = queue.get()
                    json = 'JSON ; ' + str(json)
                    q.put(str(json))
                    break
                else:
                    prints = 'print ; ' + str(prints)
                    q.put(prints)
                
            logging.info("Loop has been broken.")
        except:
            logging.critical("Local server has crashed.")


    def task_test(self, conn_test, gui_cfg, gui_cfg_host, desired_test, test_info):   

        logger.info("SSHHandler: task_test has started.")

        # Dynamically import test class and testing info
        full_id = test_info["full_id"]
        tester = test_info["tester"]

        test_path = gui_cfg["Test"][desired_test]['TestPath']
        test_command = gui_cfg["Test"][desired_test]['TestScript']
    
        username = gui_cfg_host['TestHandler']['username']
        hostname = gui_cfg_host['TestHandler']['hostname']

        #command to run test on ssh
        #username, hostname, test_command, and test_config are specified in GUI Config
        #full id, tester, and test_config are extra arguments passed to the python command being run
        cmd = ['ssh', '-t', username + '@' + hostname, test_path + '/' + test_command, full_id, tester]

        #runs ssh command using python subprocess 
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True)
        logger.info("SSHHandler: test has been started")

        #iterates over lines as they are received, sends them to task_local 
        for line in iter(proc.stdout.readline, ''):
            conn_test.put(line.replace('\n', '\r\n'))





