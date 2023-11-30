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

gifpaths= [ '/'.join(x.split('/')[-3:]) for x in giflist]

flagpaths = [('/'.join(x.split('/')[-3:])).replace('.gif','.flg') for x in giflist]

flagsexist = [os.path.isfile('../'+x) for x in flagpaths]


merged = list(zip(gifpaths,flagpaths,flagsexist))


outj = json.dumps(merged)
print(outj)
