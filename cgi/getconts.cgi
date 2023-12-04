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

conn = sqlite3.connect('/home/tomh/slbetrain/samples.sqlite3')
conn.enable_load_extension(True)
conn.load_extension("/home/tomh/slbetrain/sqlean/dist/sqlean.so")
conn.row_factory = sqlite3.Row
c = conn.cursor()

# parse the query string parameters

form = cgi.FieldStorage()
user = form.getvalue('user', 'nobody')

# select the records waiting for this user.

#c.execute("INSERT OR IGNORE INTO samples (sourcemedia_base, frame_no, contour_id, x,y,w,h, image, still_context, animated_context) VALUES (?,?,?,?,?,?,?,?,?,?)",
c.execute('''SELECT s.recid,s.sourcemedia_base, s.frame_no, s.contour_id, s.x,s.y,s.w,s.h, 
            encode(s.image,'base64') image, 
            encode(s.still_context,'base64') still_context, 
            encode(s.animated_context,'base64') animated_context
        FROM samples s
        LEFT JOIN useractivity u ON s.recid=u.recid
        WHERE u.recid IS NULL LIMIT 8
        ''', ())

rows = c.fetchall()


rowlist = [ dict(row) for row in rows ]

outj = json.dumps(rowlist, indent=4, sort_keys=False, default=str)
print(outj)

