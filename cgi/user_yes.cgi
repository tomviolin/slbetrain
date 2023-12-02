#!/home/tomh/slbetrain/venv/bin/python3
import cgitb
import cgi
import json
import os
import sys
import time
import datetime
import glob
import sqlite3


cgitb.enable()

print("Cache-Control: no-cache, no-store, must-revalidate")
print("Pragma: no-cache")
print("Expires: 0")

print("Content-Type: application/json; charset=utf-8")
print()
# get values from the query string from an HTTP GET
#
# get the query string from an HTTP GET
query_string = os.environ["QUERY_STRING"]
if query_string == "":
    print("No data received")
    sys.exit(0)
# get the value of the key-value pair
# named "name"
name = query_string.split("=")[1]
form = cgi.FieldStorage()
# get the value of the key-value pair
# named "name"
base = form.getvalue("base", "(no name)")
frame = form.getvalue("frame", "(no name)")
cont = form.getvalue("cont", "(no name)")



conn = sqlite3.connect('/home/tomh/slbetrain/samples.sqlite3')
c = conn.cursor()
c.execute('''
    UPDATE samples 
       SET user_category=1 where mediasource_base=? and frame_no=? and contour_id=?", (base, frame, cont))
print(json.dumps({'base':base,'frame':frame,'cont':cont}))



