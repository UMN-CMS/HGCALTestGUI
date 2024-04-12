base_path = "/home/HGCAL_dev/test_scripts"

masterCfg = {

    "GUIType": "Engine",

    "UsingScanner": True,


    # Order of tests matters here
    # This should be the same order that you want the tests to be run in
    # Number of test will also be decide by this list so don't miss any
    "Test": [
        {
            "name": "Power-Ground Resistance",
            "required": 1,
            "desc_short": "Measure resistance between power and ground",
            "desc_long": "Check that the power and grounds are not shorted at the terminal, or between the inputs.",
        },
        {
            "name": "1.5V Input Check",
            "required": 1,
            "desc_short": "Check that the 1.5V input is not shorted.",
            "desc_long": "Check that resistance between across C906 or C908 is non-zero.",
        },
        {
            "name": "10V Input Check",
            "required": 1,
            "desc_short": "Check that the 10V input is not shorted.",
            "desc_long": "Check that resistance between across C907 or C909 is non-zero.",
        },
        {
            "name": "1.2V Output Check",
            "required": 1,
            "desc_short": "Check that the 1.2V output is not shorted.",
            "desc_long": "Check that resistance between across C904 or C904 or TP901 is non-zero.",
        },
        {
            "name": "RX 2.5V Output Check",
            "required": 1,
            "desc_short": "Check that the RX 2.5V output is not shorted.",
            "desc_long": "Check that resistance across C902 is non-zero."
        },
        {
            "name": "TX 2.5V Output Check",
            "required": 1,
            "desc_short": "Check that the TX 2.5V output is not shorted.",
            "desc_long": "Check that resistance across either C903 or TP902 is non-zero."
        },
        # Power on Tests
        {
            "name": "LDO Output",
            "required": 1,
            "desc_short": "Check that the LDO output voltage is around 1.2V",
            "desc_long": "Measure the votlage across either R911 or TP901 and verify that it is appropriate."
        },
        {
            "name": "LinPol RX Check",
            "required": 1,
            "desc_short": "Check that the RX voltage from the linppol is operating correctly",
            "desc_long": "Check that voltages across either R905 or R902 is 2.5V."
        },
        {
            "name": "LinPol TX Check",
            "required": 1,
            "desc_short": "Check that the TX voltage from the linppol is operating correctly",
            "desc_long": "Measure the voltage across either TP902 or R906 or C903 is 2.5V."
        },

        #Operations Tests
        {
            "name": "X_PWR",
            "required": 1,
            "desc_short": "Check the the X_PWR voltage is correct.",
            "desc_long": "Measure using the tester, and should find approximately 1.2V.",
            "TestClass" : "TestXPWR",
        },
        {
            "name": "lpGBT setup",
            "required": 1,
            "desc_short": "Ensure setup can be performed",
            "desc_long": "Perform nominal setup from BE. Do setup, link trick, setup. Check PUSMStatus (0x1d9) reports READY (0x13) for all 3 lpGBTs. Check lpGBTs locked to BE All 3 RX equal within 200 Hz. Check All 3 RX-DV equal within 200 Hz",
        },
        {
            "name": "EClock Rates",
            "required": 1,
            "desc_short": "Ensure EClock rates are correct",
            "desc_long": "Check that all EClocks are running at 320MHz.",
        },
        {
            "name": "lpGBT IC/EC communication",
            "required": 1,
            "desc_short": "Check operability of lpGBT IC/EC communication",
            "desc_long": "Read and write to lpBGT registers via ICEC. Check DAQ lpGBT read of registers via IC. Check Trigger lpGBTs: successful read registers via EC. Ensure write and readback to user ID registers (0x004 - 0x007)",
        },
        {
            "name": "I2C",
            "required": 1,
            "desc_short": "Engine can use I2C master",
            "desc_long": "Check that engine can communicate as an I2C master",
            "TestScript": "engine_test_suite.py",

        },
        {
            "name": "GPIO functionality",
            "required": 1,
            "desc_short": "Check the quality of the GPIOs",
            "desc_long": "Read and write to all GPIO channels and verify levels. Write nominal configuration and then toggle each line one-by-one and verify change in both lpGBT status and voltage level",
            "TestClass" : "TestGpio"
        },
        {
            "name": "ADC functionality",
            "required": 1,
            "desc_short": "Check quality of the ADCs",
            "desc_long": "Measure known voltages/resistances. Check measured values for all 4 gains within tolerances, (only need to do all 4 gains for one measurement).",
            "TestClass" : "TestAdc"
        },
        {
            "name": "Uplink quality",
            "required": 1,
            "desc_short": "Check the quality of the uplinks",
            "desc_long": "PRBS validation from lpGBTs. Check bit error rate below threshold.",
            "TestClass" : "TestUplink"
        },
        {
            "name": "Downlink quality",
            "required": 1,
            "desc_short": "Check the quality of the downlinks",
            "desc_long": "Eye opening test. Check eye opening width and height below threshold.",
        },
        {
            "name": "Fast Command quality",
            "required": 1,
            "desc_short": "Check the quality of the Fast Command path",
            "desc_long": "PRBS validation from and back to ZCU. Check bit error rate below threshold.",
            "TestClass" : "TestFC"
        },
        {
            "name": "Elink quality",
            "required": 1,
            "desc_short": "Check the quality of the elinks",
            "desc_long": "PRBS validation from and back to ZCU. Check bit error rate below threshold.",
            "TestClass" : "TestElinkUp"
        },
        {
            "name": "Crossover link quality",
            "required": 1,
            "desc_short": "Check the quality of the crossover links",
            "desc_long": "PRBS validation from and back to ZCU. Check bit error rate below threshold.",
        },
    ],


    "PhysicalTest": [
        #{
        #    "name": "SAMPLE test", 
        #    "required": 1, 
        #    "desc_short": "Some short description", 
        #    "desc_long": "Really long description for later purposes.",
        #    "criteria": {
        #        "first testing criteria",
        #        "second testing criteria",
        #        "third testing criteria",                
        #    },

        #}, 

    ],

    "InspectionTest": [
        
        {
            "name": "Inspection1",
            "required": 1,
            "checkboxes": [
                {
                    "text": "Is the board bent?",
                    "value": False,
                    "requirement": False,
                },
                {
                    "text": "Is the board visibly broken?",
                    "value": False,
                    "requirement": False,
                },
                {
                    "text": "Are any components missing?",
                    "value": False,
                    "requirement": False,
                },
                {
                    "text": "Are any components visibly broken?",
                    "value": False,
                    "requirement": False,
                },
                

            ],
            "user_entry": [
                {
                    "text": "Enter a voltage between 0.5 and 1.2",
                    "value": 0,
                    "requirement": 1.0,
                }

            ],

            "comments": "No Comment",


        },


    ],

    # Example of information needed for tests (from Wagon config)
    # Use template dictionary above
    # FOLLOW THE FORMAT EXPICITLY PLEASE :)
    # "Test": [
    #    {"name": "Resistance Measurement", "required": 1, "desc_short": "Measure resistance of analog lines", "desc_long": "Test must be completed before attempting to measure ID resistor"},
    #    {"name": "ID Resistor Measurement", "required": 1, "desc_short": "Measure resistance of ID resistor", "desc_long": "Must be completed after the general resistance measurement"},
    #    {"name": "I2C Read/Write", "required": 1, "desc_short": "Check I2C read/write along wagon", "desc_long": "Test must be completed before BERT for wagon wheel configuration"},
    #    {"name": "Bit Error Rate Test", "required": 1, "desc_short": "Determine quality of data transmission", "desc_long": "Needs to be completed after I2C check in order to set up wagon wheel"},
    # ],
    # List of board types (e.g. major/minor type serial number differences)
    # Mostly important for wagons but allows for support of different engine
    # production versions if necessary
    # requiredTests field should match the indices of the list above
    # (e.g. if Test2 is required for Engine V3 Right, this list should include 1
    "Board_type": [
        {
            "name": "Engine V3 Right",
            "type_sn": "100300",
            "requiredTests": [0, 1, 2, 3, 4],
        },
        {
            "name": "Engine V3 Left",
            "type_sn": "100310",
            "requiredTests": [0, 1, 2, 3, 4],
        },
    ],
    # People who you would like to add as testers by default
    # HGCAL_dev can be used for debug testing in the beginning
    # The GUI will require everyone to have their own "account"
    "People": [
        "Nadja",
        "Charlie",
        "Bryan",
        "Devin",
        "HGCAL_dev",
    ],


    "Photo": [
        {"name": "Top", "desc_short": "Top side of the board"},
        {"name": "Bottom", "desc_short": "Bottom side of the board"},
    ],


    # Information for sending and receiving data to/from the database
    # Needs to be different based on board type
    "DBInfo": {
        "use_database": True,
        "name": "EngineDB",
        "reader": "EngineDBReadUser",
        "inserter": "EngineDBInserter",
        "admin": "EngineDBInserter",
        "baseURL": "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/EngineDB",
    },
}

masterCfg["Test"] = [dict(**x, TestPath=base_path, TestScript= "engine_test_suite.py") for x in masterCfg["Test"] if "TestClass" in x]
