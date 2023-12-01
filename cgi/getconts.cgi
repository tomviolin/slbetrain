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

giflist= sorted(glob.glob('/home/tomh/slbetrain/trains/*/conts/*.gif'))

gifpaths= [ '/'.join(x.split('/')[-3:]) for x in giflist]

dfs = [sqldf("select * from df where gifpath like '%s'" % x) for x in gifpaths]

merged = list(zip(gifpaths, category)


outj = json.dumps(merged)
print(outj)
