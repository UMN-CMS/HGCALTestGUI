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

# Making the Client Server a class
class REQClient():

    ################################################

    # Ensures nothing happens on instantiantion
    def __init__(self, gui_cfg, desired_test, full_id, tester, conn_trigger):
        with open("{}/utils/server_ip.txt".format(PythonFiles.__path__[0]),"r") as openfile:
            grabbed_ip = openfile.read()[:-1]
        self.message = ""

        test_handler_name = gui_cfg.getTestHandler()["name"]

        # Run the ZMQ server on test stand and make requests via ZMQ client
        if test_handler_name == "ZMQ":

            self.ZMQClient(gui_cfg, desired_test, full_id, tester)
        
        # Run tests only on the current computer
        elif test_handler_name == "Local":

            self.LocalClient(conn_trigger, desired_test, full_id, tester)

        # Run tests on another machine via SHH (key required)
        elif test_handler_name == "SSH":

            self.SSHClient(conn_trigger, desired_test, full_id, tester)


    # Handling tests run on the local machine
    def LocalClient(self, conn_trigger, desired_test, full_id, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "full_id": full_id, "tester": tester}
        trigger_message = json.dumps(trigger_dict)

        conn_trigger.send(trigger_message)

    # Handling tests run via SSH
    def SSHClient(self, conn_trigger, desired_test, full_id, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "full_id": full_id, "tester": tester}
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
            logger.error("No remote_ip specified, please modify config")

        debug_msg = "Sending request to REPServer for: " + self.desired_test
        logger.info(debug_msg)
        
        # Tell the server what test to run
        socket.send_string(sending_msg)
        
        # Timeout feature for the socket
        # The poller is responsible for stopping the socket send after a certain time
        # Poller is in milliseconds
        #poller = zmq.Poller()
        #poller.register(socket, zmq.POLLIN)
        #if not poller.poll(6*1000):   
        #    raise IOError("Timeout processing the REQClient request from socket")
            

        logger.info("Request sent. Waiting for confirmation receipt...")
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
                    logger.info("Request received.")
                    break

                retries_left -= 1
                logger.warning("No response from server")
                socket.setsockopt(zmq.LINGER, 0)
                socket.close()
                
                # Out of retries
                if retries_left == 0:
                    logger.error("Server seems to be offline, abandoning...")
                    break
                
                logger.info("Attempts remaining... Reconnecting to the server...")

                socket = context.socket(zmq.REQ)
                
                socket.connect("tcp://{ip_address}:5555".format(ip_address = grabbed_ip))
        
                logger.info("Resending...")

                socket.send_string(sending_msg)
                

            except:
                logger.info("couldn't get info - {}".format(tries))
                tries = tries + 1 
            #messagebox.showerror("No Message Received", "REQClient: No message received from the request.")


        # Closes the client so the code in the GUI can continue once the request is sent.
        try:
            logger.info("Trying to close the socket")
            socket.close()
        except:
            logger.info("Unable to close the socket")

    #################################################

    def get_message(self):
        return self.message

    #################################################

    def set_message(self, string):
        self.message = string

    #################################################
    
            
#################################################################################
