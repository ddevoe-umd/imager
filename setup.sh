#! /bin/bash

# Make script executable via "chmod 755 setup.sh"
#
# Setup on a Pi Zero 2 takes >1 hour

echo("===========================================")
echo("apt-get update")
echo("===========================================")
sudo apt-get update

echo("===========================================")
echo("apt-get upgrade")
echo("===========================================")
sudo apt-get upgrade

echo("===========================================")
echo("picamera")
echo("===========================================")
sudo apt-get --yes install python3-picamera

echo("===========================================")
echo("numpy")
echo("===========================================")
sudo apt-get --yes install python3-numpy

echo("===========================================")
echo("sudo scipy")
echo("===========================================")
sudo apt-get --yes install python3-scipy

echo("===========================================")
echo("pandas")
echo("===========================================")
sudo apt-get --yes install python3-pandas

echo("===========================================")
echo("pip")
echo("===========================================")
sudo apt install python3-pip

echo("===========================================")
echo("simple-pid")
echo("===========================================")
python3 -m pip install simple-pid

echo("===========================================")
echo("              SETUP COMPLETE")
echo("===========================================")