import logging, time
import WagonTestGUI
from PythonFiles.utils.REQClient import REQClient

# Format for the logging configuration
FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'

# Configures the logging. Set level to 'logging.INFO' to see relevant information. Set level to 'logging.DEBUG' if you wish to see every received message (only run this for a couple minutes on DEBUG, the file size is immmense.
logging.basicConfig(
    filename="/shared/{}/GUILogs/gui.log".format(os.getlogin()), 
    filemode = 'w', 
    format=FORMAT, 
    level=logging.INFO
    )

class StressTest():
    def __init__(self, conn, queue):
        
        #### Test Settings #### 

        # Reduce the desired time to have no remainders
        # Example:
        #           Bad ->      max_hr = 36
        #           Good ->     max_day = 1
        #                       max_hr = 12

        max_day = 0     # Set equal to to the number of desired days for the test to run       
        max_hr = 12      # Set equal to the number of desired hours for the test to run
        max_min = 0     # Set equal to the number of desired minutes for the test to run
        max_sec = 0     # Set equal to the number of desired seconds for the test to run


        #######################
        
        # Creates initial variables
        test_active = False         # Used to make sure test requests are not sent during an active test
        run_num = 0                 # Establishes the Number of Runs for information reporting
        start_time = time.time()    # Establishes a start time to report length of tests


        try:
            # Constantly attempts to start a run so long as there is not a currently active run
            # or as long as the test end requirements haven't been met
            while 1 > 0:
                # Creates a run so long as there is not currently a run happening
                if test_active == False:
                    run_start_time = time.time()                                # Logs the run start time
                    req_client = REQClient("STRESS", "000000", "STRESS")        # Starts the run by sending the test request
                    run_num += 1                                                # Increases the Run Number so that it can be tracked
                    test_active = True                                          # Makes it so that another run cannot be initialized 
                    # Is necessary for the run, is constantly trying to print the queue objects
                    # for more info, view update_console in TestInProgressScene.py
                    while 1 > 0:
                        try:
                            if not queue.empty():    
                                logging.debug("StressTest: Waiting for queue objects...")
                                text = queue.get()
                                logging.debug("Message: %s" % text)
                                if text == "Results received successfully.":
                                    # On the end of the run, logs the run information and sets the conditions for starting a new run
                                    run_time = self.determine_time(run_start_time, "string")
                                    print("StressTest: Run %s completed with a run time of %s. Beginning next run..." % (str(run_num), run_time))
                                    logging.info("StressTest: Run %s completed with a run time of %s. Beginning next run..." % (str(run_num), run_time))
                                    test_active = False
                                    break                
                            else:
                                time.sleep(.01)
                        except Exception as e:
                            # Records the error and run information
                            run_time = self.determine_time(run_start_time, "string")
                            logging.error(e)
                            logging.error("StressTest: An error has occurred during Run %s inside the nested while loop. Run time was %s" % (str(run_num), run_time))
                    # Grabs the test running time for the conditional
                    run_day, run_hr, run_min, run_sec = self.determine_time(start_time, "integer")
                    # Here is where you set the conditional to determine how many runs you want it to run for.
                    if run_day >= max_day and run_hr >= max_hr and run_min >= max_min and run_sec >= max_sec:
                        break                                             
                else:
                    pass
            # Assuming everyting went well, this will send a test completion message with information
            test_time = self.determine_time(start_time, "string")
            logging.info("StressTest: Test completed. The test time was %s and contained %s runs." % (test_time, str(run_num)))
        except Exception as e:
            # Records the error and run information
            test_time = self.determine_time(start_time, "string")
            logging.error(e)
            logging.error("StressTest: An error has occurred in the outer while loop during Run %s. The error occurred after %s" % (str(run_num), test_time))

    # Takes the a start time and the type of data you would like returned 
    # Calculates the amount of time since that start time
    # Returns that time in reduced day, hour, minute, second format.
    def determine_time(self, start_time, return_type):
        run_day = 0
        run_hr = 0
        run_min = 0
        run_sec = 0
        run_time = time.time() - start_time
        working_run_time = run_time
        if working_run_time > 60:
            run_min = int(working_run_time / 60)
            run_sec = working_run_time % 60
            working_run_time = run_min
            if working_run_time > 60:
                run_hr = int(working_run_time / 60) 
                run_min = working_run_time % 60
                working_run_time = run_hr
                if working_run_time > 24:
                    run_day = (working_run_time / 24)
                    run_hr = working_run_time % 24
        results = "%s days, %s, hours, %s minutes, and %s seconds" % (run_day, run_hr, run_min, run_sec)
        if return_type == "string":
            return results
        elif return_type == "integer":
            return run_day, run_hr, run_min, run_sec
