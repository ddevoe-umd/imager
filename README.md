
Developed on Pi Zero 2 W (Python3, Raspberry Pi OS)

Installation 
------------
chmod 755 setup.sh
setup.sh
	- install needed Python modules

Operation:
-----------------
1. Synchronize Pi system time via "sudo timedatectl" for correct timestamps on file names
2. Launch python_server.py on the Pi (see below)
	- starts web server to handle all code execution via POST requests from HTML code
	- wait for "ready" message before opening web page (next step)
3. Open plot.html on a laptop & hit Start


Pi:
-----------------
python_server.py
	- launch on boot via /etc/rc.local
	- ...or start via: nohup python3 -u python_server.py &
	- handles all Javascript client <--> Python server communication
	- manages PID control of heater
	- access cam4_server.py to send data to client
cam4_server.py
	- get data from the camera
filter_data.py
	- filter noise and evaluate time-to-positive values

Client:
--------------
plot.html
	- client user interface
style.css
	- style sheet for plot.html
js/canvasjs.min.js
	- Javascript code for plotting (js folder must be in same directory as plot.html)