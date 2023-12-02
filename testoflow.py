#!/home/tomh/slbetrain/venv/bin/python3

import os, sys
import numpy as np
import cv2

#noise background

bakg = np.random.randint(0,255,(300,300),dtype=np.uint8)
bakg = cv2.GaussianBlur(bakg,(11,11),0)
# smaller noise patch

block = np.random.randint(0,255,(50,50),dtype=np.uint8)
block = cv2.GaussianBlur(block,(3,3),0)

lastgray = None
lst2gray = None

x = 150
y = 103
u = 19.56
v = 19.55
heading = np.random.randint(0,np.pi*2)
rotvel = 0.3
speed = 22
while True:
    u = speed*np.cos(heading)
    v = speed*np.sin(heading)
    # create scene
    fig = bakg.copy()
    blockpos = (int(x)-25,int(y)-25)
    fig[blockpos[1]:blockpos[1]+50,blockpos[0]:blockpos[0]+50] = block
    fig[int(y)-25:int(y)+25,int(x)-25:int(x)+25] = block
    cv2.imshow('fig',fig)
    if lastgray is not None:
        oflow = cv2.calcOpticalFlowFarneback(cv2.UMat(lastgray),cv2.UMat(fig),None,0.5,3,15,99,5,1.2,0).get()
        mag, ang = cv2.cartToPolar(oflow[...,0], oflow[...,1])
        hsv = np.zeros_like(fig)
        cv2.rectangle(mag,blockpos,(blockpos[0]+50,blockpos[1]+50),0,2)
        cv2.rectangle(mag,lastpos,(lastpos[0]+50,lastpos[1]+50),0,2)
        cv2.imshow('mag',mag)

    lst2gray = lastgray.copy()
    lastgray = fig.copy()

    lastpos = blockpos
    x += u
    y += v
    if x > 275 or x < 25:
        u = -u
        x += u
    if y > 275 or y < 25:
        v = -v
        y += v
    k = cv2.waitKey(1) & 0xff
    if k == ord('q'):
        break
    if k == ord('a'):
        u=u-0.6
    if k == ord('d'):
        u=u+0.6
    if k == ord('w'):
        v=v-0.6
    if k == ord('s'):
        v=v+0.6

    heading = np.arctan2(v,u) + rotvel
    speed = np.sqrt(u**2+v**2)



cv2.destroyAllWindows()
