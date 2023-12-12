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

print("Content-Type: application/json; charset=utf-8")
print()


form = cgi.FieldStorage()
user = form.getvalue('user', 'nobody')
pass = form.getvalue('pass', 'nobody')

if user == 'nobody' or pass == 'nobody':
    print(json.dumps({'status': 'error', 'message': 'Invalid username or password'}))
    sys.exit(0)

print(json.dumps({'status': 'ok', 'message': 'Login successful', 'user': user}))
exit(0)


conn = sqlite3.connect('/home/tomh/slbetrain/samples.sqlite3')
conn.enable_load_extension(True)
conn.load_extension("/home/tomh/slbetrain/sqlean/dist/sqlean.so")
conn.row_factory = sqlite3.Row
c = conn.cursor()
