masterCfg = {

        "GUIType": "Wagon",

        "UsingScanner": True,

        # Order of tests matters here
        # This should be the same order that you want the tests to be run in
        # Number of test will also be decide by this list so don't miss any
        "Test": [
            {"name": "Resistance Measurement", "required": 1, "desc_short": "Measure resistance of analog lines", "desc_long": "Test must be completed before attempting to measure ID resistor"},
            {"name": "ID Resistor Measurement", "required": 1, "desc_short": "Measure resistance of ID resistor", "desc_long": "Must be completed after the general resistance measurement"},
            {"name": "I2C Read/Write", "required": 1, "desc_short": "Check I2C read/write along wagon", "desc_long": "Test must be completed before BERT for wagon wheel configuration"},
            {"name": "Bit Error Rate Test", "required": 1, "desc_short": "Determine quality of data transmission", "desc_long": "Needs to be completed after I2C check in order to set up wagon wheel"},
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





        "Photo": [
            {"name": "Top", "desc_short": "Top side of the board"},
            {"name": "Bottom", "desc_short": "Bottom side of the board"},
        ],


        # Information for sending and receiving data to/from the database
        # Needs to be different based on board type
        "DBInfo": {
            "use_database": True,
            "name": "WagonDB",
            "reader": "WagonDBReadUser",
            "inserter": "WagonDBInserter",
            "baseURL": "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/WagonDB",
            }
        }
