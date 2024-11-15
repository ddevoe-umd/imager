#! /bin/bash

# Make script executable via "chmod 755 setup.sh"
#
# Setup on a Pi Zero 2 takes >1 hour

echo "==========================================="
echo "apt-get update"
echo "==========================================="
sudo apt-get update

#echo "==========================================="
#echo "apt-get upgrade"
#echo "==========================================="
#sudo apt-get upgrade

echo "==========================================="
echo "picamera2"
echo "==========================================="
sudo apt-get --yes install python3-picamera2

echo "==========================================="
echo "numpy"
echo "==========================================="
sudo apt-get --yes install python3-numpy

echo "==========================================="
echo "sudo scipy"
echo "==========================================="
sudo apt-get --yes install python3-scipy

echo "==========================================="
echo "pandas"
echop "(may take a long time for sympy setup')
echo "==========================================="
sudo apt-get --yes install python3-pandas

echo "==========================================="
echo "pip"
echo "==========================================="
sudo apt install python3-pip

echo "==========================================="
echo "simple-pid"
echo "==========================================="
python3 -m pip install --break-system-packages simple-pid

echo "==========================================="
echo "              SETUP COMPLETE"
echo "==========================================="