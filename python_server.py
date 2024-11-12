# HTTP server code adapted from:
# https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
#
# Start in background, with stdout logged to nohup.out:
# nohup python3 -u python_server.py &
#
# Need to create a directory called "data" in same directory as code file

import simple_pid   # see https://pypi.org/project/simple-pid/
import json
import cam4_server  # our code for camera access

from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
import time
import threading
from simple_pid import PID
import RPi.GPIO as GPIO
from gpiozero import MCP3008

# GLOBALS:

# PID:
PWM_PIN = 19
FAN = 14
LED_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(FAN, GPIO.OUT) 
GPIO.setup(PWM_PIN, GPIO.OUT) 
pwm = GPIO.PWM(PWM_PIN,490)
pid = PID(Kp=13, Ki=0.17, Kd=1.2, setpoint=60)     # Can add sample_time, output_limits, etc.
pid.output_limits = (0,100)
b_bias = 0.48                   # value for linear interpolation of temperature
chip_temp = 0                   # current chip temperature

# Start heater PWM:
duty_cycle = 0
pwm.start(duty_cycle)

# ADC for temperature sensing:
const = MCP3008(channel=0)
Tb = MCP3008(channel=1)
Tt = MCP3008(channel=2)


# Flag to halt temperature control thread:
stop_event = threading.Event()


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*');
        self.end_headers()

    def do_GET(self):
        self._set_response()
        results = cam4_server.get_data()
        #self.wfile.write(bytes(results).encode('utf-8'))
        self.wfile.write(",".join([str(x) for x in results]).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self._set_response()
        post_data_decoded = post_data.decode('utf-8')
        post_dict = dict(pair.split('=') for pair in post_data_decoded.split('&'))
        info = json.loads(post_dict['todo'])
        action = info[0]
        data = info[1]
        print(action)
        print(data)
        if action == 'start':            # Start the PID loop for temp control
            start_pid()
        if action == 'getData':          # Capture & analyze single camera image
            results = cam4_server.get_image_data()
            results.append(chip_temp)
            self.wfile.write(",".join([str(x) for x in results]).encode('utf-8'))
        elif action == 'end':            # Turn off PID loop and rename final data file
            results = cam4_server.end_imaging()
            end_pid()
            self.wfile.write(results.encode('utf-8'))
        elif action == 'analyze':        # Filter curves & extract TTP values
            results = cam4_server.analyze_data(data)
            #self.wfile.write(json.dumps(results).encode('utf-8'))
            self.wfile.write(results.encode('utf-8'))


# Calibration function for PWM (temperature control):
def cali_fun(y_data):
    y_adj = (
        0.00000000000225474 * y_data ** 5 -
        0.00000000027648357 * y_data ** 4 -
        0.00000000611604906 * y_data ** 3 +
        0.00005022119088712 * y_data ** 2 +
        0.10392688339191500 * y_data +
        24.8772182731984000
        )
    return y_adj

# Temperature control (run in separate thread):
def run_pid(stop_event):
    global chip_temp
    global const, Tb, Tt
    times, board, chip, well  = [], [], [], []
    rd = 50*1e6
    ptrd = time.time_ns()
    start_time = time.time_ns()
    while not stop_event.is_set():
        try:
            # Establish list that will store values from ADC and read the ADC
            vals_raw = [const.value, Tb.value, Tt.value]
            vals = [1023*v for v in vals_raw]
                
            # Change the duty cycle based on the ADC reading    
            duty_cycle = pid(b_bias*cali_fun(vals[1] -  vals[0]) + (1-b_bias)*cali_fun(vals[2] - vals[0]))
            pwm.ChangeDutyCycle(duty_cycle)
    
            # Store values every 50ms to use for plotting
            if time.time_ns() - ptrd >= rd:
                ptrd = time.time_ns()
                times += [(ptrd - start_time)/60e9]
                board += [cali_fun(vals[1] -  vals[0])]
                chip += [cali_fun(vals[2] -  vals[0])]
                well += [b_bias*cali_fun(vals[1] -  vals[0]) + (1-b_bias)*cali_fun(vals[2] - vals[0])]
                # print(f"{times[-1]:.3f}\t{board[-1]:.3f}\t{chip[-1]:.3f}\t{well[-1]:.3f}")
            chip_temp = well[-1]
        except Exception as e:
            print(e)


def start_pid():
    GPIO.output(FAN, GPIO.HIGH)   # Turn on system fan
    t = threading.Thread(target=run_pid, args=(stop_event,))    # Start the PID loop
    t.daemon = True
    t.start()

def end_pid():
    stop_event.set()
    pwm.ChangeDutyCycle(0)

def run(port):
    handler_class=S
    server_address = ('', port)
    httpd = HTTPServer(server_address, handler_class)
    print("Python server started")
    cam4_server.setup()
    print("Camera setup done")
    print("System ready")
    try:
        httpd.serve_forever()     # blocking call
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    run(8080)


