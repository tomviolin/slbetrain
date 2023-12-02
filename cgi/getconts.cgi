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
from pandasql import sqldf

cgitb.enable()

print("Content-Type: application/json; charset=utf-8")
print()

conn = sqlite3.connect('/home/tomh/slbetrain/samples.sqlite3')

# parse the query string parameters

query_string = os.environ["QUERY_STRING"]
if query_string == "":
    pass
else:
    # get the value of the key-value pair
    # named "name"
    name = query_string.split("=")[1]
    form = cgi.FieldStorage()




giflist= sorted(glob.glob('/home/tomh/slbetrain/trains/*/conts/*.gif'))

gifpaths= [ '/'.join(x.split('/')[-3:]) for x in giflist]

category = [x.split('/')[3] for x in giflist]

merged = list(zip(gifpaths, category))


outj = json.dumps(merged)
print(outj)
