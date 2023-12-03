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

MAX_SAMPLE_DIM = 256


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


def prep_graymask(flow):
    magnitude, _ = cv.cartToPolar(cv.UMat(flow.get()[..., 0]), cv.UMat(flow.get()[..., 1])) 
    graymask = cv.UMat(magnitude)
    graymask = cv.GaussianBlur(graymask, (51,51), 0)
    graymask = cv.normalize(graymask, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
    graymask = cv.threshold(graymask, 120, 255, cv.THRESH_BINARY)[1]
    for j in range(1):
        graymask = cv.dilate(graymask, kernel9, iterations=6)
        graymask = cv.erode(graymask, kernel9, iterations=6)
    return graymask




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


raw_frames = []
gray_frames = []

# ret = a boolean return value from 
# getting the frame, first_frame = the 
# first frame in the entire video sequence 
while len(raw_frames) < 3:
    ret, inframe = cap.read() 
    if ret==False:
        break
    eqframe = inframe.copy()
    eqframe[...,0] = cv.equalizeHist(eqframe[...,0])
    eqframe[...,1] = cv.equalizeHist(eqframe[...,1])
    eqframe[...,2] = cv.equalizeHist(eqframe[...,2])

    raw_frames.append(cv.UMat(inframe))
    gray_frames.append(cv.equalizeHist(cv.cvtColor(cv.UMat(eqframe), cv.COLOR_BGR2GRAY)))

i=0
os.system(f"rm -rf {savepath}")
os.makedirs(savepath, exist_ok=True)
jpgdir = f"{savepath}/jpg"
mp4dir = f"{savepath}/mp4"
os.makedirs(jpgdir, exist_ok=True)
os.makedirs(mp4dir, exist_ok=True)
contsdir = f"{savepath}/conts"
os.makedirs(contsdir, exist_ok=True)
#flowmeanx=[]
#flowmeany=[]

while(cap.isOpened()):

    # Calculate dense optical flow by Farneback method 
    # on GPU using OpenCL
    flow01 = cv.calcOpticalFlowFarneback(gray_frames[0], gray_frames[1],
    								None,
    								0.5, 3, 15, 5, 5, 1.2, 0) #flowflags)
    flow12 = cv.calcOpticalFlowFarneback(gray_frames[1], gray_frames[2],
                                    None,
                                    0.5, 3, 15, 5, 5, 1.2, 0) #flowflags)
    flow02 = cv.calcOpticalFlowFarneback(gray_frames[0], gray_frames[2],
                                    None,
                                    0.5, 3, 15, 5, 5, 1.2, 0) #flowflags)
    flow10 = cv.calcOpticalFlowFarneback(gray_frames[1], gray_frames[0],
                                    None,
                                    0.5, 3, 15, 5, 5, 1.2, 0) #flowflags)
    flow21 = cv.calcOpticalFlowFarneback(gray_frames[2], gray_frames[1],
                                    None,
                                    0.5, 3, 15, 5, 5, 1.2, 0) #flowflags)


    graymask_main = prep_graymask(flow12)
    graymask_comp = prep_graymask(flow21)
    conts, heirarchy = cv.findContours(graymask_main, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    #print(len(conts))
    areas = []
    this_frame = raw_frames[1].get()
    for j in range(len(conts)):
        cont = conts[j]
        x,y,w,h = cv.boundingRect(cont)
        area = cv.contourArea(cont)
        rectarea = w*h
        areas += [area]
        cv.rectangle(this_frame,(x,y),(x+w,y+h),(0,255,0),2)

    for j in range(len(conts)):
        cont = conts[j]

        blank = np.zeros_like(graymask_main.get()).astype(np.uint8)
        cv.drawContours(blank, [cont.get()], -1, 1, cv.FILLED)
        pixelcount = cv.countNonZero(blank)
        blank = cv.multiply(blank, graymask_comp)
        pixelcountafter = cv.countNonZero(blank)
        print(f"{pixelcountafter}:{pixelcount}")
        if pixelcountafter < pixelcount*0.3:
            continue
        x,y,w,h = cv.boundingRect(cont)
        blob = raw_frames[1].get()[y:y+h,x:x+w].copy()
        area = cv.contourArea(cont)
        rectarea = w*h
        if area <50:
            continue
        if w > MAX_SAMPLE_DIM or h > MAX_SAMPLE_DIM:
            continue
        sw = MAX_SAMPLE_DIM
        sh = MAX_SAMPLE_DIM

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

        subframe0[desty:(desty+desth),destx:(destx+destw),:] = raw_frames[0].get()[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()
        subframe1[desty:(desty+desth),destx:(destx+destw),:] = raw_frames[1].get()[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()
        subframe2[desty:(desty+desth),destx:(destx+destw),:] = raw_frames[2].get()[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:].copy()

        subframe1 = cv.rectangle(subframe1,(x-sx,y-sy),(x+w-sx,y+h-sy),(0,255,255),1)
        subframe0 = cv.rectangle(subframe0,(x-sx,y-sy),(x+w-sx,y+h-sy),(0,205,205),1)
        subframe2 = cv.rectangle(subframe2,(x-sx,y-sy),(x+w-sx,y+h-sy),(0,205,205),1)




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

        os.system(f'/bin/bash -c \'cat {jpgdir}/sfr{i:04d}_c{j:04d}_sf{{0,1,2,1,1,1}}.jpg\' | ffmpeg -v 0 -y -f jpeg_pipe -r 5 -i -  -vf "scale=iw:ih,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"     {contsdir}/sfr{i:04d}_c{j:04d}_sfs.gif')
        # create sqlite record
        cv.imwrite(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", blob)
        blob = open(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", 'rb').read()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO samples (sourcemedia_base, frame_no, contour_id, user_category, user_entered, x,y,w,h, image) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (base,i,j,None,None, x,y,w,h, blob))
        conn.commit()



    #plt.close('all')
    #plt.hist(areas) # bins=100)
    #plt.savefig(f"{jpgdir}/hist{i:04d}.jpg")
    #plt.close('all')

    # Opens a new window and displays the output frame 
    cv.imwrite(f"{jpgdir}/graymask{i:04d}.jpg", graymask_main) #graymaskafter - graymaskorg)

    cv.imwrite(f"{jpgdir}/frame{i:04d}.jpg",this_frame)
    i=i+1
    # Updates previous frame 



    raw_frames.pop(0)
    gray_frames.pop(0)
    ret, inframe = cap.read()
    if ret==False:
        break
    eqframe = inframe.copy()
    #eqframe[...,0] = cv.equalizeHist(eqframe[...,0])
    #eqframe[...,1] = cv.equalizeHist(eqframe[...,1])
    #eqframe[...,2] = cv.equalizeHist(eqframe[...,2])

    raw_frames.append(cv.UMat(inframe))
    gray_frames.append(cv.cvtColor(cv.UMat(eqframe), cv.COLOR_BGR2GRAY))
    #gray_frames[-1] = cv.equalizeHist(gray_frames[-1])
    print(f"frame {i:04d}", end='\r')
    # Frames are read by intervals of 1 millisecond. The 
    # programs breaks out of the while loop when the 
    # user presses the 'q' key 
    # lastlastgraymask = lastgraymask
    # lastgraymask = graymask
# The following frees up resources and 
# closes all windows 
cap.release() 

#plt.plot(flowmeanx,'-',label='x')
#plt.plot(flowmeany,'-',label='y')
#plt.legend()
#plt.savefig("flowmean.png")

