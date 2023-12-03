#!/bin/bash

# Install dependencies
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-venv

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt


