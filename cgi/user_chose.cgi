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
form = cgi.FieldStorage()

recid = form.getvalue("recid", "")
user = form.getvalue("user", "")
choice = form.getvalue("choice", "")

if recid == "" or choice == "":
    print(json.dumps({'error':'missing parameters'}))
    sys.exit(0)


conn = sqlite3.connect('/home/tomh/slbetrain/slbeuser_tomh.sqlite3')
conn.row_factory = sqlite3.Row
conn.execute('CREATE TABLE IF NOT EXISTS slbeuser_tomh (recid INTEGER PRIMARY KEY, user TEXT, choice TEXT)')
c = conn.cursor()

c.execute('''
    INSERT INTO slbeuser_tomh
       (recid, user, choice) VALUES (?,?,?)''', (recid, user, choice))
conn.commit()
conn.close()

print(json.dumps({'success':'true'}))
sys.exit(0)

