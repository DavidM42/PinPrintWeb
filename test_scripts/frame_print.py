#!/usr/bin/env python
from importlib import import_module
import os
import cv2
import cups

FILENAME = "test.jpg"
# set that in cups web ui
PRINTER_NAME = "HP"

#CAMERA PART

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

cam = Camera()

# cv2.imwrite('neu.jpg', cam.get_frame())

with open(FILENAME, 'wb') as f:
    f.write(cam.get_frame())


#PRINTER PART

# Set up CUPS
conn = cups.Connection()
# printers = conn.getPrinters()
# print(printers.keys())

# re enable
quit()

cups.setUser('pi')

# Send the picture to the printer
print_id = conn.printFile(PRINTER_NAME, FILENAME, "Projekt Webcam ausdruck", {})

# Wait until the job finishes
from time import sleep
while conn.getJobs().get(print_id, None):
    sleep(1)