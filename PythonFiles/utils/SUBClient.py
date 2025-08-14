# Importing necessary modules
import zmq, logging
import PythonFiles
import os
import multiprocessing as mp

logger = logging.getLogger('HGCALTestGUI.PythonFiles.utils.SUBClient')


# Creating a class for the SUBSCRIBE socket-type Client
class SUBClient():

    def __init__(self, conn, queue, gui_cfg, q):
        with open("{}/utils/server_ip.txt".format(PythonFiles.__path__[0]), "r") as openfile:
            grabbed_ip = openfile.read()[:-1]
        logger.info("SUBClient has started") 
        # Instantiates variables       
        self.conn = conn
        self.message = ""
        # TODO will need to use multiprocessing to start both local and SUB_ZMQ if we want to run tests both ways
        if gui_cfg["TestHandler"]["name"] == "Local" or gui_cfg['TestHandler']['name'] == 'SSH':
            self.local(conn, queue, gui_cfg, q)
        elif gui_cfg["TestHandler"]["name"] == "ZMQ":
            self.SUB_ZMQ(conn, queue, gui_cfg)
        elif gui_cfg["TestHandler"]["name"] == "Local and ZMQ":
            self.process_local = mp.Process(target = _local, args=(conn, queue, gui_cfg, q))
            self.process_ZMQ = mp.Process(target = _SUB_ZMQ, args=(conn, queue, gui_cfg))
            self.process_local.start()
            self.process_ZMQ.start()

    def local(conn, queue, gui_cfg, q):
        try:
            while 1 > 0:
                # gets the signal from the Handler and splits it into topic and message
                # the topic determines what SUBClient will do with the message
                try:
                    signal = q.get()
                    self.topic, self.message = signal.split(" ; ")
                except Exception as e:
                    logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket") 
                    logger.exception(e) 

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
                else:
                    logger.error("SUBClient: Invalid topic sent. Must be 'print' or 'JSON'.")

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("SUBClient: An error has occurred. Check logs for more details.")

        except Exception as e:
            logger.exception(e)
            logger.critical("SUBClient has crashed. Please restart the software.")
        

    # Responsible for listening for ZMQ messages from teststand
    def SUB_ZMQ(conn, queue, gui_cfg):
        grabbed_ip = gui_cfg["TestHandler"]["remoteip"]
        # Creates the zmq.Context object
        cxt = zmq.Context()
        # Creates the socket as the SUBSCRIBE type
        listen_socket = cxt.socket(zmq.SUB)
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
                    self.topic, self.message = listen_socket.recv_string().split(" ; ")
                except Exception as e:
                    logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket")
                    logger.exception(e)
                                        

                poller = zmq.Poller()
                poller.register(listen_socket, zmq.POLLIN)

                # Tests what topic was received and then does the appropriate code accordingly
                if self.topic == "print":

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put(self.message)

                elif self.topic == "JSON":
                    
                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("Results received successfully.")

                    # Sends the JSON to GUIWindow on the pipe.
                    self.conn.send(self.message)

                else:
                    logger.error("Invalid topic sent. Must be 'print' or 'JSON'.")

                    # Places the message in the queue. the queue.get() is in 
                    # TestInProgressScene's begin_update() method
                    queue.put("SUBClient: An error has occurred. Check logs for more details.")

        except Exception as e:
            logger.exception(e)
            logger.critical("SUBClient: SUBClient has crashed. Please restart the software.")


def _local(conn, queue, gui_cfg, q):
    try:
        while 1 > 0:
            # gets the signal from the Handler and splits it into topic and message
            # the topic determines what SUBClient will do with the message
            try:
                signal = q.get()
                topic, message = signal.split(" ; ")
            except Exception as e:
                logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket") 
                logger.exception(e) 

            # Tests what topic was received and then does the appropriate code accordingly
            if topic == "print":

                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put(message)

            elif topic == "JSON":
                
                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put("Results received successfully.\r\n")

                # Sends the JSON to GUIWindow on the pipe.
                conn.send(message)
            else:
                logger.error("SUBClient: Invalid topic sent. Must be 'print' or 'JSON'.")

                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put("SUBClient: An error has occurred. Check logs for more details.")

    except Exception as e:
        logger.exception(e)
        logger.critical("SUBClient has crashed. Please restart the software.")
        

# Responsible for listening for ZMQ messages from teststand
def _SUB_ZMQ(conn, queue, gui_cfg):
    grabbed_ip = gui_cfg["TestHandler"]["remoteip"]
    # Creates the zmq.Context object
    cxt = zmq.Context()
    # Creates the socket as the SUBSCRIBE type
    listen_socket = cxt.socket(zmq.SUB)
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
                topic, message = listen_socket.recv_string().split(" ; ")
            except Exception as e:
                logger.error("SUBClient: There was an error trying to get the topic and/or message from the socket")
                logger.exception(e)
                                    

            poller = zmq.Poller()
            poller.register(listen_socket, zmq.POLLIN)

            # Tests what topic was received and then does the appropriate code accordingly
            if topic == "print":

                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put(message)

            elif topic == "JSON":
                
                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put("Results received successfully.")

                # Sends the JSON to GUIWindow on the pipe.
                conn.send(message)

            else:
                logger.error("Invalid topic sent. Must be 'print' or 'JSON'.")

                # Places the message in the queue. the queue.get() is in 
                # TestInProgressScene's begin_update() method
                queue.put("SUBClient: An error has occurred. Check logs for more details.")

    except Exception as e:
        logger.exception(e)
        logger.critical("SUBClient: SUBClient has crashed. Please restart the software.")
