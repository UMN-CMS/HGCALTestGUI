#####################################################################
#                                                                   #
#  Adaptation from REQClient specifically for Thermal Tester        #
#  Additional parameter support for specifying args for test        #
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

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.ThermalREQClient')
#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(
#    filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), 
#    filemode = 'a', 
#    format=FORMAT, 
#    level=logging.INFO
#    )

# Making the Client Server a class
class ThermalREQClient():

    ################################################

    # Ensures nothing happens on instantiantion
    def __init__(self, gui_cfg, desired_test, thermal_dict, full_id, tester, conn_trigger):
        
        print("ThermalREQClient: Initializing...")
        
        with open("{}/utils/server_ip.txt".format(PythonFiles.__path__[0]),"r") as openfile:
            grabbed_ip = openfile.read()[:-1]
        self.message = ""

        test_handler_name = gui_cfg.getTestHandler()["name"]

        # Run the ZMQ server on test stand and make requests via ZMQ client
        if test_handler_name == "ThermalZMQ":

            self.ThermalZMQClient(gui_cfg, desired_test, thermal_dict, full_id, tester)
        
        # Run tests only on the current computer
        elif test_handler_name == "Local":

            self.ThermalLocalClient(conn_trigger, desired_test, thermal_dict, full_id, tester)

        # Run tests on another machine via SHH (key required)
        elif test_handler_name == "SSH":

            self.ThermalSSHClient(conn_trigger, desired_test, thermal_dict, full_id, tester)


    # Handling tests run on the local machine
    def ThermalLocalClient(self, conn_trigger, desired_test, thermal_dict, full_id, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "full_id": full_id, "tester": tester}
        trigger_message = json.dumps(trigger_dict)

        conn_trigger.send(trigger_message)

    # Handling tests run via SSH
    def ThermalSSHClient(self, conn_trigger, desired_test, thermal_dict, full_id, tester):

        desired_test = int(desired_test[4:])

        trigger_dict = {"desired_test": desired_test, "full_id": full_id, "tester": tester}
        trigger_message = json.dumps(trigger_dict)

        conn_trigger.send(trigger_message)

    def ThermalZMQClient(self, gui_cfg, desired_test, thermal_dict, serial, tester):
        sending_msg = f"{desired_test};{thermal_dict};{tester}"

        print("\nsending_msg:", sending_msg, "\n")
        # Establishing variable for use
        self.desired_test = desired_test
        # Necessary for zmqClient    
        context = zmq.Context()

        try: 
            remote_ip = gui_cfg.getTestHandler()["remoteip"]

            # Creates a socket to talk to the server
            print("ThermalREQClient: Connecting to the thermal testing server...")
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://{ip_address}:8898".format(ip_address = remote_ip))
        except:
            print("No remote_ip specified, please modify config")

        debug_msg = "ThermalREQClient: Sending request to REPServer for: " + self.desired_test
        print(debug_msg)
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
            

        logger.debug("ThermalREQClient: Request sent. Waiting for confirmation receipt...")
        # Get the reply
    
        # Recording the number of tries to open the socket and receive a string
        tries = 0


        REQUEST_TIMEOUT = 2000
        REQUEST_RETRIES = 3
        # socket.connect("tcp://{ip_address}:5555".format(ip_address = grabbed_ip))

        retries_left = REQUEST_RETRIES
        while (len(self.message)< 1) and tries < 1000:
            
            try:
                #print("\nTrying to receive a message from the socket")
                #logger.debug("ThermalREQClient: Trying to receive a message from the socket receive")
                #self.message = socket.recv_string()
                #print("\n\n\nSelf.message: {}\n\n\n".format(self.message))

                if(socket.poll(REQUEST_TIMEOUT) &  zmq.POLLIN) != 0:
                    self.message = socket.recv_string()
                    retries_left = REQUEST_RETRIES
                    print("ThermalREQClient: Request received.")
                    logger.info("ThermalREQClient: Request received.")
                    break

                retries_left -= 1
                logger.warning("ThermalREQClient: No response from server")
                print("\n\nTHERMALREQCLIENT WARNING: NO RESPONSE FROM THE SERVER\n\n")
                socket.setsockopt(zmq.LINGER, 0)
                socket.close()
                
                # Out of retries
                if retries_left == 0:
                    logger.error("ThermalREQClient: Server seems to be offline, abandoning...")
                    print("ThermalREQClient: Server seems to be offline, abandoning...")
                    break
                
                logger.info("ThermalREQClient: Attempts remaining...Reconnecting to the server...")

                socket = context.socket(zmq.REQ)
                
                # TODO ZMQ What is "grabbed_ip" supposed to be?
                socket.connect("tcp://{ip_address}:5555".format(ip_address = grabbed_ip))
        
                logger.info("ThermalREQClient: Resending...")

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
