from dumpToYaml import dump_to_yaml

masterCfg = { 

        "GUIType": "Wagon",

        "UsingScanner": True,

        # Order of tests matters here
        # This should be the same order that you want the tests to be run in
        # Number of test will also be decide by this list so don't miss any 
        # TestClass, TestScript, and TestPath fields will be used to write the REPserver script
        # TestPath should be in reference to the testing home directory
        "Test": [
                {
                "name": "Resistance Measurement", 
                "required": 1, 
                "desc_short": "Measure resistance of analog lines", 
                "desc_long": "Test must be completed before attempting to measure ID resistor", 
                "TestClass": "gen_resist_test", 
                "TestPath": "/home/HGCAL_dev/sw", 
                "TestScript": "wagon_rtd.py"
                },
            
                {
                "name": "ID Resistor Measurement", 
                "required": 1, 
                "desc_short": "Measure resistance of ID resistor", 
                "desc_long": "Must be completed after the general resistance measurement", 
                "TestClass": "id_resist_test", 
                "TestPath": "/home/HGCAL_dev/sw", 
                "TestScript": "wagon_rtd.py"
                },
        
                {
                "name": "I2C Read/Write", 
                "required": 1, 
                "desc_short": "Check I2C read/write along wagon", 
                "desc_long": "Test must be completed before BERT for wagon wheel configuration", 
                "TestClass": "IIC_Check", 
                "TestPath": "/home/HGCAL_dev/sw", 
                "TestScript": "run_iic_check.py"
                },
        
                {
                "name": "Bit Error Rate Test", 
                "required": 1, 
                "desc_short": "Determine quality of data transmission", 
                "desc_long": "Needs to be completed after I2C check in order to set up wagon wheel", 
                "TestClass": "BERT", 
                "TestPath": "/home/HGCAL_dev/sw", 
                "TestScript": "run_bert.py"
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


        # Information for sending and receiving data to/from the database
        # Needs to be different based on board type
        "DBInfo": {
            "use_database": True,
            "name": "WagonDB",
            "reader": "WagonDBReadUser",
            "inserter": "WagonDBInserter",
            "baseURL": "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/WagonDB"
            }
        }

dump_to_yaml(masterCfg)
