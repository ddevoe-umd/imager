Hardware:
---------
* Raspberry Pi Zero 2 W (Python3, Raspberry Pi OS)
* Pi Camera (InnoMaker CAM OV5647, 5MP)

Installation 
------------
1. Run `setup.sh` (installs required Python modules)
2. Edit `/etc/rc.local` with the following line to run server code at boot:
   `nohup python3 -u ~pi/imager/python_server.py > ~pi/imager/nohup.out &`
3. Synchronize Pi system time via "sudo timedatectl" for correct timestamps on file names

Operation:
-----------------
Open `plot.html` on the client laptop


Pi:
-----------------
* `python_server.py`
	- set up to launch on boot via `/etc/rc.local`
	- handles all Javascript client <--> Python server communication
	- manages PID control of heater
	- access `cam4_server.py` to send data to client
* `cam4_server.py`
	- get data from the camera
* `filter_data.py`
	- filter noise and evaluate time-to-positive values

Client:
--------------
* `plot.html`
	- client user interface
* `css/style.css`
	- style sheet for plot.html
* `js/canvasjs.min.js`
	- Javascript code for plotting (js folder must be in same directory as `plot.html`)
