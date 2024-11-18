import time
from picamera2 import Picamera2
import numpy as np
import csv
import os
from filter_data import filter
import RPi.GPIO as GPIO

from PIL import Image, ImageDraw 
import base64
from io import BytesIO

# Globals:

# Image size:
w = 640         # min of 64, max of 2592 for 5MP camera
h = int(3*w/4)  # native 4:3 aspect ratio
res = (w,h)  

# Camera:
cam = Picamera2()

# Data storage:
data_directory = 'data'

LED_PIN = 13

# Set up list containing upper left corner of all ROIs:
well_cols = 4   # number of well columns
well_rows = 3   # number of well rows
roi_upper_left = (254,165)   # cordinates for upper left corner of upper left ROI
roi_spacing = 60     # spacing (x & y) between ROI centers
roi_width = 12
roi_height = 28 
ROIs = []            # list of all ROIs
for i in range(well_rows):
    for j in range(well_cols):
        x = roi_upper_left[0] + roi_spacing*j
        y = roi_upper_left[1] + roi_spacing*i
        ROIs.append((x,y))

# Add ROIs to a captured image
def image_with_ROIs(image):
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    for roi in ROIs:
        roi_lower_right = [0,0]
        roi_lower_right[0] = roi[0] + roi_width
        roi_lower_right[1] = roi[1] + roi_height
        roi_lower_right = tuple(roi_lower_right)
        draw.rectangle([roi, roi_lower_right])
    return(pil_image)

def setup_camera():    # Set up camera
    config = cam.create_still_configuration(main={"size": res})
    cam.configure(config)
    cam.set_controls({
        "AeEnable": False,
        "ExposureTime": int(5 * 1e4),
        "AnalogueGain": 0.5,
        "AwbEnable": False,
        "ColourGains": (1.2,1.0)
        })
    os.makedirs(data_directory, exist_ok=True)
    time.sleep(3)   # time to stabilize settings

def get_image_data():    # Extract fluorescence measurements from ROIs in image
    cam.start()
    GPIO.output(LED_PIN, GPIO.HIGH)   # Turn on LED
    data = cam.capture_array("main")
    cam.stop()
    GPIO.output(LED_PIN, GPIO.LOW)    # Turn off LED

    # Get average value within each well ROI:
    results = [int(time.time())]  # 1st entry is the time stamp
    for (px,py) in ROIs:
        r,b,g = 0,0,0
        count = 0
        for x in range(int(px),int(px+roi_width)):
            for y in range(int(py),int(py+roi_height)):
                r += data[x][y][0]
                g += data[x][y][1]
                b += data[x][y][2]
                count += 1
        results.append(g)     # Green channel ~ 500 nm

    # Append new result to temp data file:
    with open('data/temp_data.csv', 'a') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(results)
    return(results[1:])  # strip time stamp for javascript

def get_image():       # Return a full image with ROI boxes added
    # Acquire an image:
    cam.start()
    GPIO.output(LED_PIN, GPIO.HIGH)
    image = cam.capture_array("main")
    cam.stop()
    GPIO.output(LED_PIN, GPIO.LOW)
    print('cam4_server: image acquired')
    pil_image = image_with_ROIs(image)  # Add ROIs to image
    buffer = BytesIO()     # create a buffer to hold the JPG image
    pil_image.save(buffer, format="JPEG")    # Convert image to JPG
    jpeg_image = buffer.getvalue()
    jpeg_base64 = base64.b64encode(jpeg_image).decode('utf-8')  # Encode jpg as base64
    return(f"data:image/jpeg;base64,{jpeg_base64}")

def end_imaging():
    # Rename temp data file:
    date_str = time.strftime("%Y%m%d_%Hh%Mm%Ss")
    output_filename = 'data_' + date_str + '.csv'
    os.rename(data_directory + '/temp_data.csv', data_directory + '/' + output_filename)
    with open(data_directory + '/temp_data.csv', 'w') as f:
        pass      # Delete contents of the temp data file
    return(output_filename)

def analyze_data(filename):
    results = filter(datafile_directory + '/' + filename)
    return(results)

