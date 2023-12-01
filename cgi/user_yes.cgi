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

print("Cache-Control: no-cache, no-store, must-revalidate")
print("Pragma: no-cache")
print("Expires: 0")

# get values from the query string from an HTTP GET
#
# get the query string from an HTTP GET
#query_string = os.environ["QUERY_STRING"]
# get the value of the key-value pair
# named "name"
name = query_string.split("=")[1]
form = cgi.FieldStorage()
# get the value of the key-value pair
# named "name"
name = form.getvalue("base", "(no name)")


print("Content-Type: application/json; charset=utf-8")
print()



"""
giflist= sorted(glob.glob('/home/tomh/slbetrain/trains/*/conts/*.gif'))

gifpaths= [ '/'.join(x.split('/')[-3:]) for x in giflist]

flagpaths = [('/'.join(x.split('/')[-3:])).replace('.gif','.flg') for x in giflist]

flagsexist = [os.path.isfile('../'+x) for x in flagpaths]


merged = list(zip(gifpaths,flagpaths,flagsexist))
"""

