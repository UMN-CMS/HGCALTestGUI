#####################################################################
#                                                                   #
#  This is the code for a client to send a request to a server to   #
#  run specific test scripts. You can additionally specify running  #
#  tests locally or via ssh.                                        #
#                                                                   #
#####################################################################

#################################################################################

# Importing necessary modules
import zmq, logging
import PythonFiles
import multiprocessing as mp
import os
import json
import time

from PythonFiles.utils.LocalHandler import LocalHandler

#################################################################################

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.REQClient')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(
#    filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), 
#    filemode = 'a', 
#    format=FORMAT, 
#    level=logging.INFO
#    )

# Making the Client Server a class
class REQClient():

    ################################################

    # Ensures nothing happens on instantiantion
    def __init__(self, gui_cfg, desired_test, serial, tester, conn_trigger):
        with open("{}/utils/server_ip.txt".format(PythonFiles.__path__[0]),"r") as openfile:
            grabbed_ip = openfile.read()[:-1]
        self.message = ""

        test_handler_name = gui_cfg.getTestHandler()["name"]
        print("#"*20)
        print("#"*20)
        print(test_handler_name)
        print("#"*20)
        print("#"*20)

        # Run the ZMQ server on test stand and make requests via ZMQ client
        if test_handler_name == "ZMQ":

            self.ZMQClient(gui_cfg, desired_test, serial, tester)
        
        # Run tests only on the current computer
        elif test_handler_name == "Local":

            self.LocalClient(conn_trigger, desired_test, serial, tester)

        # Run tests on another machine via SHH (key required)
        elif test_handler_name == "SSH":

            self.SSHClient(conn_trigger, desired_test, serial, tester)


    # Handling tests run on the local machine
    def LocalClient(self, conn_trigger, desired_test, serial, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "serial": serial, "tester": tester}
        trigger_message = json.dumps(trigger_dict)

        conn_trigger.send(trigger_message)

    # Handling tests run via SSH
    def SSHClient(self, conn_trigger, desired_test, serial, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "serial": serial, "tester": tester}
        trigger_message = json.dumps(trigger_dict)

        conn_trigger.send(trigger_message)

    def ZMQClient(self, gui_cfg, desired_test, serial, tester):
        sending_msg = desired_test + ";" + serial + ";" + tester
        # Establishing variable for use
        self.desired_test = desired_test
        # Necessary for zmqClient    
        context = zmq.Context()

        try: 
            remote_ip = gui_cfg.getTestHandler()["remoteip"]

            # Creates a socket to talk to the server
            # print("Connecting to the testing server...")
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://{ip_address}:5555".format(ip_address = remote_ip))
        except:
            print("No remote_ip specified, please modify config")

        debug_msg = "REQClient: Sending request to REPServer for: " + self.desired_test
        logger.debug(debug_msg)
        
        # Tell the server what test to run
        socket.send_string(sending_msg)
        
        # Timeout feature for the socket
        # The poller is responsible for stopping the socket send after a certain time
        # Poller is in milliseconds
        #poller = zmq.Poller()
        #poller.register(socket, zmq.POLLIN)
        #if not poller.poll(6*1000):   
        #    raise IOError("Timeout processing the REQClient request from socket")
            

        logger.debug("REQClient: Request sent. Waiting for confirmation receipt...")
        # Get the reply
    
        # Recording the number of tries to open the socket and receive a string
        tries = 0


        REQUEST_TIMEOUT = 2500
        REQUEST_RETRIES = 3
        # socket.connect("tcp://{ip_address}:5555".format(ip_address = grabbed_ip))

        retries_left = REQUEST_RETRIES
        while (len(self.message)< 1) and tries < 1000:
            
            try:
                #print("\nTrying to receive a message from the socket")
                #logger.debug("REQClient: Trying to receive a message from the socket receive")
                #self.message = socket.recv_string()
                #print("\n\n\nSelf.message: {}\n\n\n".format(self.message))

                if(socket.poll(REQUEST_TIMEOUT) &  zmq.POLLIN) != 0:
                    self.message = socket.recv_string()
                    retries_left = REQUEST_RETRIES
                    print("REQClient: Request received.")
                    logger.info("REQClient: Request received.")
                    break

                retries_left -= 1
                logger.warning("REQClient: No response from server")
                print("\n\nREQCLIENT WARNING: NO RESPONSE FROM THE SERVER\n\n")
                socket.setsockopt(zmq.LINGER, 0)
                socket.close()
                
                # Out of retries
                if retries_left == 0:
                    logger.error("REQClient: Server seems to be offline, abandoning...")
                    print("REQClient: Server seems to be offline, abandoning...")
                    break
                
                logger.info("REQClient: Attempts remaining...Reconnecting to the server...")

                socket = context.socket(zmq.REQ)
                
                socket.connect("tcp://{ip_address}:5555".format(ip_address = grabbed_ip))
        
                logger.info("REQClient: Resending...")

                socket.send_string(sending_msg)
                

            except:
                print("REQClient: couldn't get info - {}".format(tries))
                logger.debug("REQClient: No Message received from the request.")
                tries = tries + 1 
            #messagebox.showerror("No Message Received", "REQClient: No message received from the request.")


        # Closes the client so the code in the GUI can continue once the request is sent.
        try:
            logger.debug("REQClient: Trying to close the socket")
            socket.close()
        except:
            logger.debug("REQClient: Unable to close the socket")

    #################################################

    def get_message(self):
        return self.message

    #################################################

    def set_message(self, string):
        self.message = string

    #################################################
    
            
#################################################################################
