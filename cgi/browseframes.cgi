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

frames = sorted(glob.glob("/home/tomh/slbetrain/trains/*/jpg/frame*.jpg"))

# parse query string
form = cgi.FieldStorage()

# get the frame number
frame = form.getvalue("frameno")

# if no frame number, set to 0
if frame is None:
    frame = "0"

frameuri = frames[int(frame)]
frameuri = '/' + '/'.join(frameuri.split('/')[-5:])

# create html page with javascript to use right arrow to advance to next frame and left arrow to go back a frame
print("Content-type: text/html\n\n")
print("<html>")
print("<head>")
print("<title>SLBE Train</title>")
print("<script>")
print("function nextFrame() {")
print("  var frame = parseInt(document.getElementById('frame').value);")
print("  frame++;")
print("  document.getElementById('frame').value = frame;")
print("  document.getElementById('frameform').submit();")
print("}")
print("function prevFrame() {")
print("  var frame = parseInt(document.getElementById('frame').value);")
print("  frame--;")
print("  document.getElementById('frame').value = frame;")
print("  document.getElementById('frameform').submit();")
print("}")
print("</script>")
print("<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'></script>")
print("</head>")
print("<body>")
print("<form id='frameform' action='browseframes.cgi' method='get'>")
print("<input type='button' value='<' onclick='prevFrame()'>")
print("<input id='frame' name='frameno' value='" + frame + "'>")
print("<input type='button' value='>' onclick='nextFrame()'>")
print("</form>")
print("<img width='100%' src='" + frameuri + "'>")
print("</body>")
print("""
<script>
        $(window).keydown(function(e) {
  switch (e.keyCode) {
    case 37: // left arrow key
    case 38: // up arrow key
      e.preventDefault(); // avoid browser scrolling due to pressed key
      prevFrame();
      return;
    case 39: // right arrow key
    case 40: // up arrow key
      e.preventDefault();
      nextFrame();
      return;
  }
});
</script>
""")
print("</html>")


