import multiprocessing as mp
import zmq, sys, os, signal, logging, json

sys.path.append("{}".format(os.getcwd()))

# Class needed for bridging the gap between request, running test
# and sending results back

# This takes the place of the REPserver and PUBServer which are
# used when tests are run via ZMQ

# Note that this process needs to start on instantiation of the GUI
# to avoid any overlapping event monitors. So, conn_trigger
# is used to trigger a new test via REQClient

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.LocalHandler')

class LocalHandler:

    def __init__(self, gui_cfg, conn_trigger, q):

        conn_test, conn_pub = mp.Pipe()

        # Listen for test request
        while True:
            logger.info("LocalHandler: New PUB proc")
            msg = conn_trigger.recv()
            if msg == "EXIT":
                break
            else:
                request = json.loads(msg)
            process_PUB = mp.Process(target = self.task_local, args=(conn_pub,q))
            process_PUB.start()

            if request is not None:

                desired_test = request["desired_test"]
                test_info = {"full_id": request["full_id"], "tester": request["tester"]}

                logger.info("LocalHandler: New test proc")
                self.process_test = mp.Process(target = self.task_test, args=(conn_test, gui_cfg, desired_test, test_info))
                self.process_test.start()

                # Hold until test finish
                logger.info("LocalHandler: Joining test proc")
                self.process_test.join()

                logger.info("LocalHandler: Terminate PUB proc")
                process_PUB.terminate()


        try:
            conn_pub.close()
            conn_test.close()

        except Exception as e:
            logger.error("LocalHandler: PUB and test pipe could not be closed: {}".format(e))

        #try:
        #    process_PUB.terminate()
        #except Exception as e:
        #    logger.error("LocalHandler: PUB and test process could not be terminated: {}".format(e))

    def task_local(self, conn, q):
        # listens for incoming data and attaches the correct topic before sending it on to SUBClient
        #try:
        while 1 > 0:
            prints = conn.recv()
            if "Done." in prints:
                prints = 'print ; ' + str(prints)
                q.put(prints)

                json = conn.recv()
                json = 'JSON ; ' + str(json)
                q.put(str(json))
                break
            else:
                prints = 'print ; ' + str(prints)
                q.put(prints)
            
        logger.info("LocalHandler: Loop has been broken.")
        #except:
        #    logging.critical("Local server has crashed.")



    def task_test(self, conn_test, gui_cfg, desired_test, test_info):   

        # Dynamically import test class 
        test_meta = gui_cfg["Test"][desired_test]
        # Need to strip .py from test script for import
        # TestClass is the name of the class defined in the test script
        sys.path.append(test_meta["TestPath"])
        mod = __import__(test_meta["TestScript"][:-3], fromlist=[test_meta["TestClass"]])
        test_class = getattr(mod, test_meta["TestClass"])

        test_class(conn_test, board_sn=test_info["full_id"], tester=test_info["tester"])

