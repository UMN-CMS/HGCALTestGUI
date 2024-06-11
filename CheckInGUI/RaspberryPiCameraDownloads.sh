#!/bin/bash


# Required installs to get the Raspberry PI Camera in Tkinter
pip3 install tkinter

apt-get install python3-pil python3-pil.imagetk

apt install python3-matplotlib python3-tk

pip3 install pyzmq

pip3 install -U numpy

apt install -y python3-picamera2


# Version type matters here

pip3 install opencv-contrib-python==4.5.3.56 
