import time
from picamera import PiCamera
import numpy as np
import csv
import os
from filter_data import filter


# Globals:

# Image size:
w = 640         # min of 64, max of 2592 for 5MP camera
h = int(3*w/4)  # native 4:3 aspect ratio
res = (w,h)  

# Camera:
exposure_time = 0.05   # desired exposure time [s]
cam = PiCamera()

# Data storage:
data = np.empty((res[1],res[0],3),dtype=np.uint8)
datafile_path = 'data/'

# Set up list containing center positions of all wells:
well_upper_left = (196,252)
well_spacing = 62
well_cols = 4
well_rows = 3
well_width = 24
wells = []
for i in range(well_rows):
    for j in range(well_cols):
        x = well_upper_left[0] + well_spacing*i
        y = well_upper_left[1] + well_spacing*j
        wells.append((x,y))


def setup():
    # Set up camera:
    cam.resolution = res
    
    # Preview mode, use to test out new camera settings:
    #cam.framerate = 2
    #cam.start_preview()
    #time.sleep(10)
    #cam.stop_preview()
    
    # Shutter speed limited by framerate
    cam.framerate = 1/exposure_time
    
    # Trade off ISO and shutter speed to get desired
    # brightness while minimizing noise:
    cam.iso = 800   # sensitivity, 100-800 range, linear scale
    cam.shutter_speed = int(exposure_time * 1e6)   # microseconds, 6e6 maximum
    
    # Manually control white balance.
    # See https://picamera.readthedocs.io/en/release-1.13/api_camera.html
    # "AWB mode 'off' is special: this disables the camera’s automatic white
    #  balance permitting manual control of the white balance via the
    #  awb_gains property. However, even with AWB disabled, some attributes
    #  (still_stats and drc_strength) can cause AWB re-calculations."
    cam.awb_mode = 'off'
    cam.awb_gains = (1.2, 1.0)  # (red,blue) balance, values from 0-8
    
    # Other camera settings:
    cam.exposure_mode = 'off'
    
    time.sleep(3)   # time to stabilize settings


def get_image_data():
    data = np.empty((res[1],res[0],3),dtype=np.uint8)
    cam.capture(data,'rgb')

    # Get average value within each well ROI:
    results = [int(time.time())]  # 1st entry is the time stamp
    for (cx,cy) in wells:
        r,b,g = 0,0,0
        count = 0
        for x in range(int(cx-well_width/2),int(cx+well_width/2)):
            for y in range(int(cy-well_width/2),int(cy+well_width/2)):
                r += data[x][y][0]
                g += data[x][y][1]
                b += data[x][y][2]
                count += 1
        results.append(g)     # Green channel ~ 500 nm

    # Append new result to temp data file:
    with open('data/temp_data.csv', 'a') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(results)
    return(results[1:])  # strip time stamp for javascript code


def end_imaging():
    # Rename temp data file:
    date_str = time.strftime("%Y%m%d_%Hh%Mm%Ss")
    output_filename = 'data_' + date_str + '.csv'
    os.rename(datafile_path + 'temp_data.csv', datafile_path + output_filename)
    with open(datafile_path + 'temp_data.csv', 'w') as f:
        pass      # Delete contents of the temp data file
    return(output_filename)


def analyze_data(filename):
    results = filter(datafile_path + filename)
    return(results)

