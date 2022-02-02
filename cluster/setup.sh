#!/bin/bash

#####################################################
# BRAINWORKS - Cluster Computing Setup Script
# When run on an Unbuntu 20.04 portal machine, this
# script will configure the machine with all requirements
# needed to run the NLP pipeline of BRAINWORKS
#####################################################

######################################################
# 1. Update the Machine and install Python dependencies
######################################################
sudo apt-get update
sudo apt-get install python3.8-venv
sudo apt install libcairo2-dev pkg-config python3-dev
pip3 install --upgrade pip

######################################################
# 2. Create output directory structure
######################################################
mkdir output; mkdir output/out; mkdir output/err
mkdir module_src; mkdir module_src/java

######################################################
# 3. Install Java Dependencies
######################################################
cd module_src/java
wget https://download.oracle.com/java/17/archive/jdk-17.0.1_linux-x64_bin.tar.gz
tar zxvf jdk-17.0.1_linux-x64_bin.tar.gz
rm *.tar.gz
cd ~/brainworks/cluster
cp -r privatemodules ~/privatemodules

######################################################
# 3. Create and bind to python virtual environemnt
######################################################
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
Pip install wheel
pip install -r ../requirements/full_requirements.txt

