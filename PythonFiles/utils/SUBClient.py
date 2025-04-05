# Importing necessary modules
import zmq, logging
import PythonFiles
import os

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.SUBClient')

#FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
#logging.basicConfig(filename="/home/{}/GUILogs/gui.log".format(os.getlogin()), filemode = 'a', format=FORMAT, level=logging.INFO)


# Creating a class for the SUBSCRIBE socket-type Client
class SUBClient():

    def __init__(self, conn, queue, gui_cfg, q):
        with open("{}/utils/server_ip.txt".format(PythonFiles.__path__[0]), "r") as openfile:
            grabbed_ip = openfile.read()[:-1]
        logger.info("SUBClient has started") 
        print('\n')
        print('INFO:HGCALTestGUI.PythonFiles.utils.SUBClient: SUBClient has started')
        # Instantiates variables       
        self.conn = conn
        self.message = ""
        if gui_cfg["TestHandler"]["name"] == "Local" or gui_cfg['TestHandler']['name'] == 'SSH':
            self.local(conn, queue, gui_cfg, q)
        else:
            self.SUB_ZMQ(conn, queue, gui_cfg)


    def local(self, conn, queue, gui_cfg, q):
        try:
            while 1 > 0:
                # gets the signal from the Handler and splits it into topic and message
                # the topic determines what SUBClient will do with the message
                try:
                    signal = q.get()
                    self.topic, self.message = signal.split(" ; ")
                    print(f"SUBCLIENT: topic - {self.topic}; message - {self.message}")
                except Exception as e:
                    logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket") 
                    logger.error(e) 

                # Tests what topic was received and then does the appropriate code accordingly
                if self.topic == "print":

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put(self.message)

                elif self.topic == "JSON":
                    
                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("Results received successfully.\r\n")

                    # Sends the JSON to GUIWindow on the pipe.
                    self.conn.send(self.message)

                elif self.topic == "LCD":
                    logging.info("SUBClient: The topic of LCD has been selected. This method is empty")
                    pass

                else:
                    logging.error("SUBClient: Invalid topic sent. Must be 'print' or 'JSON'.")

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("SUBClient: An error has occurred. Check logs for more details.")

        except Exception as e:
            print("Outer Try: {}".format(e))
            logger.error(e)
            logger.critical("SUBClient: SUBClient has crashed. Please restart the software.")
        

    # Responsible for listening for ZMQ messages from teststand
    def SUB_ZMQ(self, conn, queue, gui_cfg):
        
        
        grabbed_ip = gui_cfg["TestHandler"]["remoteip"]
        # Creates the zmq.Context object
        cxt = zmq.Context()
        # Creates the socket as the SUBSCRIBE type
        listen_socket = cxt.socket(zmq.SUB)

        # TODO ZMQ is this always the correct port number?
        listen_socket.connect("tcp://{ip_address}:5556".format(ip_address = grabbed_ip))

        # Sets the topics that the server will listen for
        listen_socket.setsockopt(zmq.SUBSCRIBE, b'print')
        listen_socket.setsockopt(zmq.SUBSCRIBE, b'JSON')

        try:
            while 1 > 0:
                # Splits up every message that is received into topic and message
                # the space around the semi-colon is necessary otherwise the topic and messaage
                # will have extra spaces.
                try:
                    print("Waiting")
                    self.topic, self.message = listen_socket.recv_string().split(" ; ")
                    print(self.topic, self.message)
                except Exception as e:
                    logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket")
                    logger.error(e)
                                     

                poller = zmq.Poller()
                poller.register(listen_socket, zmq.POLLIN)

                # Tests what topic was received and then does the appropriate code accordingly
                if self.topic == "print":

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    print(self.message)
                    queue.put(self.message)

                elif self.topic == "JSON":
                    
                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("Results received successfully.")

                    # Sends the JSON to GUIWindow on the pipe.
                    self.conn.send(self.message)

                elif self.topic == "LCD":
                    logger.info("SUBClient: The topic of LCD has been selected. This method is empty")
                    pass

                else:
                    logger.error("SUBClient: Invalid topic sent. Must be 'print' or 'JSON'.")

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("SUBClient: An error has occurred. Check logs for more details.")

        except Exception as e:
            print("Outer Try: {}".format(e))
            logger.debug(e)
            logger.critical("SUBClient: SUBClient has crashed. Please restart the software.")
