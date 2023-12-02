#!/home/tomh/slbetrain/venv/bin/python3

import os, sys
import numpy as np
import cv2

#noise background

bakg = np.random.randint(0,255,(300,300),dtype=np.uint8)
bakg = cv2.GaussianBlur(bakg,(5,5),0)
# smaller noise patch

block = np.random.randint(0,255,(50,50),dtype=np.uint8)
block = cv2.GaussianBlur(block,(5,5),0)

lastgray = None

x = 150
y = 150
u = 5
v = 5
while True:
    # create scene
    fig = bakg.copy()
    fig[y-25:y+25,x-25:x+25] = block
    cv2.imshow('fig',fig)
    if lastgray is not None:
        oflow = cv2.calcOpticalFlowFarneback(lastgray,fig,None,0.5,3,15,9,5,1.2,0)
        mag, ang = cv2.cartToPolar(oflow[...,0], oflow[...,1])
        hsv = np.zeros_like(fig)
        cv2.imshow('mag',mag)
    lastgray = fig.copy()
    x += u
    y += v
    if x > 275 or x < 25:
        u = -u
        x += u
    if y > 275 or y < 25:
        v = -v
        y += v
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
