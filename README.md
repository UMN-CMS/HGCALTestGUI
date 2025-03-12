


# HGCALTestGUI

This repository contains the GUI used to run the quality control testing for all HGCAL Wagons and Engines.
It also contains the CheckIn GUI and the Photo Taking GUI.

## Setup 

Run these commands from your working area to pull the code in:

    git clone git@github.com:UMN-CMS/HGCALTestGUI.git
    
When updating the code, you can use the following commands:
    
    git add <your files>
    git commit -m "Message about what you are committing"
    git push origin <LocalBranchName>:<RemoteBranchName>
    
You can then open a pull request (PR) by going to the Github repo and then we can merge your code into the master branch. 

## Package Installation
_You must use python3_. To install all of the dependancies for this project, you will need to run the following installation commands. Notice that the versioning for the opencv is important (this is to prevent extensive installation times). 
```
# If permissions denied, add a 'sudo' before each line
apt-get install python3-pil python3-pil.imagetk
apt  install python3-tk
pip3 install -U numpy
pip3 install pyzmq
pip3 install pyyaml

# Version type matters here
pip3 install opencv-contrib-python==4.5.3.56 
```
For Photo Taking Stand Only
```
apt install -y python3-picamera2
```
The drivers for the scanner can be found here; choose the appropriate drivers for your OS:
https://www.zebra.com/us/en/support-downloads/software/scanner-software/scanner-sdk-for-linux.html?downloadId=dfb89068-1045-4411-961e-6499333ef749

After downloading the .zip file, run
```
unzip <filename.zip>
cd <filename>
sudo dpkg -i *
```

You will also need to run "make" in the following directory of each GUI for the scanner to work:
```
./PythonFiles/Scanner/
```

## To run the program:

To run the program:

You will need to run "python REPServer.py" on the appropriate machine after pulling the server code from `REPSERVER GITHUB REPO LINK HERE`.

Note:


You may need to update the ip address the sockets connect to in the following files:

```
REPServer.py
PUBServer.py
SUBClient.py
REQClient.py

``` 
Be sure to update REPServer.py and PUBServer.py on the testing station and SUBClient.py and REQClient.py on the computer running the GUI

You will also need to install and set up the database that you will be using at `DATABASE GITHUB REPO LINK HERE`

This program is built to be compatible with a Zebra `MODEL NUMBER GOES HERE` Scanner. Please connect it to the computer and do any required setup before running the program. 

The database and webpage script hostnames need to be specified in the Configuration file, along with how running of the test is to be handled (locally, through SSH, or through ZMQ).

With those set up and running, open these files in VS Code (or any application that runs Python) and run the following commands in the terminal:

```
pip install -r requests.txt
./__main__.py for HGCAL Testing GUI
./MainFunction.py for PhotoTakingGUI and CheckInGUI

```
## Using the program

When the GUI loads in there will be a loading screen, this will change to the login scene when the GUI is loaded.

The login scene will require you to choose a user to continue into the program further. If you wish to add a new user or specify information about the testing components being used, you may click the "Admin Tools" button. However, this will require admin privileges within the database.

The scan scene will require a board id number to be scanned to progress forward. Simply scan the QR code on the board and then hit the "Submit" button. If you scan the wrong QR Code, you may push the "Rescan" button to scan another QR code. An id number can also be entered manually.
 
Most scenes in the GUI will contain the "Change Boards" and "Logout" buttons. This will allow you to return to scan scene and scan a new board in or return to login scene to choose a new user respectively.

When using the Testing GUI, the sidebar will allow you to navigate to any frame that is not greyed out simply by click on the respective named button. If a test has been completed, it cannot be selected from the navigator, but instead requires the user to use the respective "Retest" button found on the test summary scene.

While a test is in progress, the GUI will disable sidebar navigation and prevent you from leaving the GUI. This can be overriden using CTRL + C, but it will not halt the test. That would require a similar override on the test station's computer.

The test summary scene contains a "More Info" button. This button will display the information found in the "data" portion of the test results in the python dictionary. This information is also viewable from the website. It also contain's a "Next Test" button. This functions identically to the "Change Boards" button found on other scenes.

To access the website, you simply need to type "cmslab1.spa.umn.edu/Factory/EngineDB/home_page.py" into the web browser of your choice
 

## Goals for this Framework:

The main goal for this framework is to have an efficient and easy-to-use user interface for running Wagon QC testing. The points of focus are:
- Integration the GUI with the test results database to store information about which boards have been tested and what tests have been run
- Easy to understand step-by-step instructions for QC testers to follow
- Implementation of a barcode scanning functionality for registering new boards and uploading test results
- Tracking of who is doing a tests, where it is taking place, and where the boards will be moved to after testing is finished

## Background Information

### What is a GUI?

A GUI (or Graphical User Interface) is a program which allows users to interact with software via buttons, text entry boxes, and other module types. Most software that we are familiar with includes a user interface where we can modify data, navigate pages, and perform actions. An example of a GUI is the webpage you are currently on! You can choose to look at some of the code in this repository or perform actions to updated it with the click of a button. 

The GUI we will be developing for testing wagon functionality will be python based. There are a few packages that can be used for developing python based GUIs. The example GUI ([here](gui/initial_test_gui.py)) uses [TKinter](https://docs.python.org/3/library/tkinter.html) to produce the user interface. You can try out this GUI by performing the following command line call: `python initial_test_gui.py`.

### What is a Wagon?

Wagons are the motherboard connecting the active detector modules (what is measuring particle intractions) and the engines (the "brains" of the front-end electronics). Wagons are responsible for carrying clock, trigger, DAQ, and control infromation to between 2-4 modules simultaneously. They are completely passive boards and have no chips for communicating with the rest of the system. 

The purpose of wagons in the front-end readout train is to tranasmit data and control information to and from modules. Thus, we would like to ensure that each wagon in the final version of the detector has been checked for good communication ability.

### What tests are being run?

There are four tests that need to be run in order to verify a wagon is funcitioning properly plus an initial test to make sure the tester is working properly:

- ADC Self Check: checks that the ADC functions properly before running further tests
- Analog line connection check: measure the resistance of each of the analog lines on the wagon to ensure good connection
- Measurement of ID resistor: each wagon has a precision resistor used for identification of wagon type that must be measured and compared to the nominal value
- I2C read/write test: verify that the slow control communication along the wagon lines is working
- Bit error rate measurement: check the quality of the data sent along the wagon elinks

These are just the tests for LD Wagons, to view all tests for LD and HD Wagons and Engine, visit the testing webpage.
