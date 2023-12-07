#This script will convert any python dictionaries you want into yaml

import yaml

#Import any dictionary files you want to convert to yaml here
from Engine_cfg import masterCfg as master_engine
from Wagon_cfg import masterCfg as master_wagon

#Create a dictionary with the names of the yaml files you want to create as keys 
#and the dictionary files as the values
#Only put alphanumeric characters into the files name, no spaces
py_files = {
        'Engine_cfg': master_engine,
        'Wagon_cfg': master_wagon,
        }

write_yaml(py_files)

#This function can be passed a dictionary from other functions and will write a yaml file with that dictionary
def write_yaml(dictionary):
    #This for loop iterates over all entries in the dictionary and creates a corresponding yaml file
    for i in dictionary:
        file = open(i + '.yaml', 'w')
        yaml.dump(dictionary[i], file)
        file.close()
