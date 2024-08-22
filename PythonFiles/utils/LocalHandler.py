import multiprocessing as mp
import zmq, sys, os, signal, logging, json

sys.path.append("{}".format(os.getcwd()))
sys.path.append("{}/Tests".format(os.getcwd()))

# Class needed for bridging the gap between request, running test
# and sending results back

# This takes the place of the REPserver and PUBServer which are
# used when tests are run via ZMQ

# Note that this process needs to start on instantiation of the GUI
# to avoid any overlapping event monitors. So, conn_trigger
# is used to trigger a new test via REQClient

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.LocalHandler')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.INFO)

class LocalHandler:

    def __init__(self, gui_cfg, conn_trigger, q):

        conn_test, conn_pub = mp.Pipe()

        # Listen for test request
        while True:
            print("New PUB proc")
            print("waiting for trigger request")
            logger.info("New PUB proc")
            request = json.loads(conn_trigger.recv())
            process_PUB = mp.Process(target = self.task_local, args=(conn_pub,q))
            process_PUB.start()

            if request is not None:

                desired_test = request["desired_test"]
                test_info = {"full_id": request["full_id"], "tester": request["tester"]}

                print("New test proc")
                logger.info("New test proc")
                self.process_test = mp.Process(target = self.task_test, args=(conn_test, gui_cfg, desired_test, test_info))
                self.process_test.start()

                # Hold until test finish
                print("Joining test proc")
                logger.info("Joining test proc")
                self.process_test.join()

                print("Terminate PUB proc")
                logger.info("Terminate PUB proc")
                process_PUB.terminate()


        try:
            conn_pub.close()
            conn_test.close()

        except Exception as e:
            logging.error("PUB and test pipe could not be closed: {}".format(e))

        try:
            process_PUB.terminate()
        except Exception as e:
            logging.error("PUB and test process could not be terminated: {}".format(e))

    def task_local(self, conn, q):
        # listens for incoming data and attaches the correct topic before sending it on to SUBClient
        #try:
        while 1 > 0:
            prints = conn.recv()
            if prints == "Done.":
                prints = 'print ; ' + str(prints)
                q.put(prints)

                json = queue.get()
                json = 'JSON ; ' + str(json)
                q.put(str(json))
            else:
                prints = 'print ; ' + str(prints)
                q.put(prints)
            
        logging.info("Loop has been broken.")
        #except:
        #    logging.critical("Local server has crashed.")



    def task_test(self, conn_test, gui_cfg, desired_test, test_info):   

        # Dynamically import test class 
        test_meta = gui_cfg["Test"][desired_test]
        # Need to strip .py from test script for import
        mod = __import__(test_meta["TestScript"][:-3], fromlist=[test_meta["TestClass"]])
        test_class = getattr(mod, test_meta["TestClass"])

        test_class(conn_test, board_sn=test_info["full_id"], tester=test_info["tester"])


    # removed in favor of task_local, which functions without a ZMQ server
##########################################################################
    def task_PUB(self, conn_pub):
        # Used to allow CTRL+C keyboard interrupt
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # Creates zmq.Context object
        cxt = zmq.Context()
        # Sets socket type to PUBLISH
        pub_socket = cxt.socket(zmq.PUB)
        # Server side .bind
        pub_socket.bind("tcp://*:5556")

        # Creates a while loop that is searching for the "print" messages on the pipe
        # Sends them immediately and once it receieves "Done." It prepares to receive and send
        # the json files of results.
        try:
            while 1 > 0:
                print("Ready for next request")
                prints = conn_pub.recv()
                logger.info("Print statement received.")
                logger.info("Testing if print statement is 'Done.'")
                if prints == "Done.":
                    logger.info("String variable prints = 'Done.'")
                    prints = "print ; " + str(prints)
                    logger.info("'print' topic added to the prints variable.")
                    pub_socket.send_string(prints)
                    logger.info("Sent final print statement.")
                    logger.info("Waiting for JSON on Pipe")
                    json = conn_pub.recv()
                    logger.info("JSON receieved.")
                    json = "JSON ; " + str(json)
                    logger.info("JSON topic added to json string")
                    pub_socket.send_string(str(json))
                    logger.info("JSON sent.")
                    # Breaks the loop once it sends the JSON so the server will shut down
                    #break
                else:
                    prints = "print ; " + prints
                    logger.info(prints)
                    logger.info("'print' topic added to prints variable.")
                    pub_socket.send_string(prints)
                    logger.info("Sent print statement.")
            
            logger.info("Loop has been broken.")
        except:
            logger.critical("PUBServer has crashed.")

        # Closes the server once the loop is broken so that there is no hang-up in the code
        #print("PUBServer Closing")    
        #pub_socket.close()
##########################################################################

