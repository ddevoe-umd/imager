# Code to filter LAMP data
# Will remove noise due to bubbles and spurious measurement errors

import numpy as np
import json
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import pandas as pd

def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def filter(filename):
    y_filtered_dict = []
    ttp = []
    with open(filename) as f:
        df = pd.read_csv(f, header=None)
        t = df.iloc[:, 0].tolist()
        cut_number = 0    # initial data points to ignore
        t = t[cut_number:]
    
        cols = df.columns[1:]
    
        for idx in range(1,13):
            y = df.iloc[:,idx].tolist()
    
            # Remove initial data points:
            y = y[cut_number:]
            t = t[cut_number:]
    
            t0 = t[0]   # need to shift to t=0 for 1st point
            t = [float(val-t0) for val in t]
            y = [float(val) for val in y]
    
            # Remove spurious data:
            for i,val in enumerate(y):
                if val < 2 and i>0:
                    y[i] = y[i-1]
            
            # Filter requirements.
            cutoff = 0.2    # cutoff frequency (0.05 - 0.2 Hz is a good range)
            T = t[-1]       # Sample Period
            n = len(t)      # total number of samples
            fs = T/n        # sample rate, Hz
            order = 6       # filter order       
    
            yf = butter_lowpass_filter(y, cutoff, fs, order)
            
            # shift curves to min value:
            y = [x-min(yf) for x in y]
            yf = [x-min(yf) for x in yf]
    
            # normalize curves to max value:
            y_norm = [x/max(yf) for x in y]
            yf_norm = [x/max(yf) for x in yf]
    
            yf_dict = [{'x':t[i], 'y':yf_norm[i]} for i in range(len(t))]
            y_filtered_dict.append(yf_dict)

            ttp.append(get_ttp(t,yf_norm))

    all_data = [ttp, y_filtered_dict]
    #return(y_filtered_dict)
    return(json.dumps(all_data))


def get_ttp(t,y):
    # Calculate slope at midpoint and project back to baseline to find TTP
    npoints = 2   # number of points before and after midpoint to use in linear fit
    indices = [idx for idx in range(len(y)) if y[idx] >= 0.5]
    ttp = -1
    if len(indices)>0:
        idx = indices[0]    # 1st index > 0.5
        if idx > npoints+1:
            # linear curve fit:
            t_ = t[idx-npoints:idx+npoints]
            y_ = y[idx-npoints:idx+npoints]
            m,b = np.polyfit(t_, y_, 1)
            print(f'm={m}, b={b}')
            ttp = (y[idx]-b)/m   # project line onto x-axis
    return ttp
        

