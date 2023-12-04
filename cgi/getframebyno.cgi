#!/home/tomh/slbetrain/venv/bin/python3

import cgi
import cgitb
import os
import sys
import json
import datetime
import time
import glob

cgitb.enable()


# parse query string
form = cgi.FieldStorage()

# get the frame number
frame = form.getvalue("frameno")

filepat = form.getvalue("filepat")
if filepat is None:
    filepat = "frame"

# if no frame number, set to 0
if frame is None:
    frame = "0"

frames = sorted(glob.glob(f"/home/tomh/slbetrain/trains/*/jpg/{filepat}*.jpg"))
if int(frame) > len(frames):
    frame = str(len(frames) - 1)
frameuri = frames[int(frame)]
frameuri = '/' + '/'.join(frameuri.split('/')[-5:])


print("Content-type: application/json\n\n")
print(json.dumps({"frameno": frame, "frameuri": frameuri}))

