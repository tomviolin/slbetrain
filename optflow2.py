#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cv2 as cv 
import numpy as np 
import os, sys

import sqlite3
import time
import datetime

conn = sqlite3.connect('samples.sqlite3')
conn.execute('''CREATE TABLE IF NOT EXISTS samples
        (sourcemedia_base char(32), 
        frame_no int,
        contour_id int,
        user_category int,
        user_entered TIMESTAMP,
        x int,
        y int,
        w int,
        h int,
        image blob,
        PRIMARY KEY (sourcemedia_base, frame_no, contour_id)
        )''')


# establish structuring element for dilation
kernel9 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
kernel3 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(3,3))
kernel5 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5))


# The video feed is read in as 
# a VideoCapture object 
if len(sys.argv) > 1:
    farg = sys.argv[1]
else:
    farg = "SLBE_20230904_095801.mp4"

cap = cv.VideoCapture(sys.argv[1])
base = os.path.basename(sys.argv[1])
base = base.split(".")[0]
savepath = f"trains/{base}"
sys.argv.pop(1) # remove the first argument

# ret = a boolean return value from 
# getting the frame, first_frame = the 
# first frame in the entire video sequence 
ret, first_frame = cap.read() 
#first_frame = first_frame[600:,:,:]
# Converts frame to grayscale because we 
# only need the luminance channel for 
# detecting edges - less computationally 
# expensive 
prev_gray = cv.cvtColor(cv.UMat(first_frame), cv.COLOR_BGR2GRAY) 

prev_frame = first_frame.copy()
prv2_frame = first_frame.copy()

# Creates an image filled with zero 
# intensities with the same dimensions 
# as the frame 
mask = np.zeros_like(first_frame) 

# Sets image saturation to maximum 
mask[..., 1] = 255
i=0
os.system(f"rm -rf {savepath}")
os.makedirs(savepath, exist_ok=True)
jpgdir = f"{savepath}/jpg"
mp4dir = f"{savepath}/mp4"
os.makedirs(jpgdir, exist_ok=True)
os.makedirs(mp4dir, exist_ok=True)
contsdir = f"{savepath}/conts"
os.makedirs(contsdir, exist_ok=True)
flowmeanx=[]
flowmeany=[]
prev_flow = None
klast_flow = None
flowflags = 0
lastgraymask = None
lastlastgraymask = None
framelimit = 120
if len(sys.argv) > 1:
    framelimit = int(sys.argv[1])
while(cap.isOpened()) and i<framelimit:

    # ret = a boolean return value from getting 
    # the frame, frame = the current frame being 
    # projected in the video 
    ret, this_frame = cap.read() 
    if ret==False:
        break
    orgframe = this_frame.copy()
    # convert the first frame to grayscale 
    gray = cv.cvtColor(cv.UMat(this_frame), cv.COLOR_BGR2GRAY) 
    
    # Calculates dense optical flow by Farneback method 
    # on GPU using OpenCL
    flow = cv.calcOpticalFlowFarneback(prev_gray, gray, 
    								prev_flow,
    								0.5, 3, 19, 9, 5, 1.2, flowflags)
    prev_flow = flow
    
    flowflags = cv.OPTFLOW_USE_INITIAL_FLOW
    cpuflow = flow.get()
    if klast_flow is None:
        klast_flow = cpuflow
    klast_flow = cpuflow # klast_flow * .7 + cpuflow * .3
    flow = klast_flow
    #flow = cpuflow
    meanx = np.mean(flow[...,0])
    meany = np.mean(flow[...,1])
    flowmeanx.append(meanx)
    flowmeany.append(meany)

    # Computes the magnitude and angle of the 2D vectors 
    magnitude, angle = cv.cartToPolar(cv.UMat(flow[..., 0]), cv.UMat(flow[..., 1])) 
    #
    # Sets image hue according to the optical flow 
    # direction 
    mask0 = cv.multiply(angle, 180)
    mask0 = cv.divide(mask0, np.pi * 2)
    mask2 = cv.UMat(magnitude)
    graymask = mask2 
    grayasmk = cv.GaussianBlur(graymask, (15,15), 0)
    graymask = cv.normalize(graymask, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
    graymask = cv.threshold(graymask, 160, 255, cv.THRESH_BINARY)[1]
    graymaskorg = cv.UMat(graymask)
    for j in range(1):
        graymask = cv.dilate(graymask, kernel9, iterations=2)
        graymask = cv.erode(graymask, kernel9, iterations=2)
    graymaskafter = cv.add(graymask,0)
    graymask1 = cv.add(graymask,0)

    conts, heirarchy = cv.findContours(graymask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    #print(len(conts))
    areas = []
    for j in range(len(conts)):
        cont = conts[j]
        x,y,w,h = cv.boundingRect(cont)
        area = cv.contourArea(cont)
        rectarea = w*h
        areas += [area]
        cv.rectangle(this_frame,(x,y),(x+w,y+h),(0,255,0),2)

    for j in range(len(conts)):
        cont = conts[j]

        if lastgraymask is not None:
            blank = np.zeros_like(graymask.get()).astype(np.uint8)
            cv.drawContours(blank, [cont.get()], -1, 1, cv.FILLED)
            pixelcount = cv.countNonZero(blank)
            lgm = lastgraymask.get()
            lgm[lgm>0] = 1
            blank = blank * lgm
            pixelcountafter = cv.countNonZero(blank)
            print(f"{pixelcountafter}:{pixelcount}")
            if pixelcountafter < pixelcount * .5:
                continue

        x,y,w,h = cv.boundingRect(cont)
        blob = orgframe[y:y+h,x:x+w].copy()
        area = cv.contourArea(cont)
        rectarea = w*h
        if area <500:
            continue
        if w >150 or h > 150:
            continue
        sw = 150
        sh = 150

        sx = x + (w // 2) - (sw // 2)
        sy = y + (h // 2) - (sh // 2)

        destx=0
        desty=0
        destw = sw
        desth = sh

        sourcex = sx
        sourcey = sy
        sourcew = sw
        sourceh = sh

        if sourcex < 0:
            destx = -sourcex
            sourcew = sw + sourcex
            sourcex = 0

        if sourcey < 0:
            desty = -sourcey
            sourceh = sh + sourcey
            sourcey = 0

        if sourcex + sourcew > this_frame.shape[1]:
            sourcew = this_frame.shape[1] - sourcex
            destw = sourcew

        if sourcey + sourceh > this_frame.shape[0]:
            sourceh = this_frame.shape[0] - sourcey
            desth = sourceh

        if destx + destw > sw:
            destw = sw - destx

        if desty + desth > sh:
            desth = sh - desty

        if destx < 0:
            sourcew += destx
            sourcex -= destx
            destx = 0

        if desty < 0:
            sourceh += desty
            sourcey -= desty
            desty = 0

        if sourcew <= 0 or sourceh <= 0:
            continue

        if destw <= 0 or desth <= 0:
            continue

        subframe0 = np.zeros((sh,sw,3), dtype=np.uint8)
        subframe1 = np.zeros((sh,sw,3), dtype=np.uint8)
        subframe2 = np.zeros((sh,sw,3), dtype=np.uint8)

        subframe0[desty:(desty+desth),destx:(destx+destw),:] = prv2_frame[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()
        subframe1[desty:(desty+desth),destx:(destx+destw),:] = prev_frame[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()
        subframe2[desty:(desty+desth),destx:(destx+destw),:] = this_frame[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()

        subframe2 = cv.rectangle(subframe2,(x-sx,y-sy),(x+w-sx,y+h-sy),(0,255,255),2)



        # Write some Text

        font                   = cv.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,10)
        bottomLeftCornerOfBlack = (11,11)
        fontScale              = 0.3
        fontColor              = (0,255,255)
        fontBlack              = (0,0,0)
        lineType               = 1

        
        cv.putText(subframe0,'-2', bottomLeftCornerOfBlack, font, fontScale, fontBlack, lineType)
        cv.putText(subframe0,'-2', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        cv.putText(subframe1,'-1', bottomLeftCornerOfBlack, font, fontScale, fontBlack, lineType)
        cv.putText(subframe1,'-1', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        cv.putText(subframe2,'0', bottomLeftCornerOfBlack, font, fontScale, fontBlack, lineType)
        cv.putText(subframe2,'0', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)




        cv.imwrite(f"{jpgdir}/sfr{i:04d}_c{j:04d}_sf0.jpg", subframe0)
        cv.imwrite(f"{jpgdir}/sfr{i:04d}_c{j:04d}_sf1.jpg", subframe1)
        cv.imwrite(f"{jpgdir}/sfr{i:04d}_c{j:04d}_sf2.jpg", subframe2)

        os.system(f'cat {jpgdir}/sfr{i:04d}_c{j:04d}_sf*.jpg {jpgdir}/sfr{i:04d}_c{j:04d}_sf2.jpg | ffmpeg -v 0 -y -f jpeg_pipe -r 2 -i -  -vf "scale=iw:ih,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"     {contsdir}/sfr{i:04d}_c{j:04d}_sfs.gif')
        # create sqlite record
        cv.imwrite(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", blob)
        blob = open(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", 'rb').read()
        c = conn.cursor()
        c.execute("INSERT INTO samples (sourcemedia_base, frame_no, contour_id, user_category, user_entered, x,y,w,h, image) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (base,i,j,None,None, x,y,w,h, blob))
        conn.commit()



    plt.close('all')
    plt.hist(areas) # bins=100)
    plt.savefig(f"{jpgdir}/hist{i:04d}.jpg")
    plt.close('all')

    # Opens a new window and displays the output frame 
    cv.imwrite(f"{jpgdir}/graymask{i:04d}.jpg", graymask) #graymaskafter - graymaskorg)

    cv.imwrite(f"{jpgdir}/frame{i:04d}.jpg",this_frame)
    i=i+1
    # Updates previous frame 
    prev_gray = gray

    prv2_frame = prev_frame.copy()
    prev_frame = this_frame.copy()

    lastgraymask = cv.add(graymask,0)

    print(f"frame {i:04d}", end='\r')
    # Frames are read by intervals of 1 millisecond. The 
    # programs breaks out of the while loop when the 
    # user presses the 'q' key 
    # lastlastgraymask = lastgraymask
    # lastgraymask = graymask
# The following frees up resources and 
# closes all windows 
cap.release() 

plt.plot(flowmeanx,'-',label='x')
plt.plot(flowmeany,'-',label='y')
plt.legend()
plt.savefig("flowmean.png")

