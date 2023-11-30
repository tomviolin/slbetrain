#!/home/tomh/slbetrain/venv/bin/python3
import cgitb
import cgi
import json
import os
import sys
import time
import datetime
import glob

cgitb.enable()

print("Content-Type: application/json; charset=utf-8")
print()

giflist= sorted(glob.glob('/home/tomh/slbetrain/trains/*/conts/*.gif'))

outj = json.dumps(giflist)
print(outj)
