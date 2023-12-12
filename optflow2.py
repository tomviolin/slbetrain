#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cv2 as cv 
import cv2
import numpy as np 
import os, sys

import sqlite3
import time
import datetime

OF_DATESTAMP=os.environ['OF_DATESTAMP']
MAX_SAMPLE_DIM = 256
ANALYSIS_FRAME_COUNT = 5
PICTURE_FRAME = 2
conn = sqlite3.connect('samples.sqlite3')
conn.execute('''CREATE TABLE IF NOT EXISTS samples (
        recid INTEGER PRIMARY KEY AUTOINCREMENT,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sourcemedia_base CHAR(32), 
        frame_no INTEGER,
        contour_id INTEGER,
        x INTEGER,
        y INTEGER,
        w INTEGER,
        h INTEGER,
        image BLOB,
        still_context BLOB,
        animated_context BLOB
        )''')

conn.execute('''CREATE TABLE IF NOT EXISTS useractivity (
        recid INTEGER PRIMARY KEY AUTOINCREMENT,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user CHAR(32),
        user_choice INTEGER,
        image BLOB)''')

# establish structuring element for dilation
kernel9 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
kernel3 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(3,3))
kernel5 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5))


def prep_graymask(flow):
    magnitude, _ = cv.cartToPolar(cv.UMat(flow.get()[..., 0]), cv.UMat(flow.get()[..., 1])) 
    graymask = cv.UMat(magnitude)
    graymask = cv.GaussianBlur(graymask, (51,51), 0)
    #graymask = cv.normalize(graymask, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
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


# Calculate dense optical flow by Farneback method 
# on GPU using OpenCL
def calcFlow(i1,i2):
    global gray_frames
    flow = cv.calcOpticalFlowFarneback(gray_frames[i1], gray_frames[i2],
                                    None,
                                    0.5, 3, 3, 5, 5, 1.2, 0)
    flowmag, flowdir = cv.cartToPolar(cv.UMat(flow.get()[..., 0]), cv.UMat(flow.get()[..., 1]))

    return flow, flowmag, flowdir

def calcFlowRLOF(i1,i2):
    global raw_frames, gray_frames
    flow = cv.optflow.calcOpticalFlowDenseRLOF(	raw_frames[i1], raw_frames[i2], 
            None, rlofParam=0.5, forwardBackwardThreshold=3, gridStep=15, interp_type=5,
            epicK=5, epicSigma=1.1, epicLambda=0.01, ricSPSize=15, ricSLICType=100,
            use_post_proc=True, fgsLambda=500.0, fgsSigma=1.5, use_variational_refinement=True)
    return flow

def putShadowedText(img, text, xorigin, yorigin, fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), 
        shadowcolor=(0,0,0), thickness=1, lineType=cv.LINE_AA):
    cv.putText(img,text, (xorigin+0,yorigin+0), fontFace=font, fontScale=fontScale, color=shadowcolor, thickness=thickness, lineType=lineType)
    cv.putText(img,text, (xorigin+1,yorigin+1), fontFace=font, fontScale=fontScale, color=color,       thickness=thickness, lineType=lineType)

def normalize(img):
    return cv.normalize(img, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)


nextWindowx = 0
nextWindowy = 0
nextRowWindowy = 0

keyq = []

# readKey() allows the GUI to update, and queues any keypress events
# so they can be checked at the end of the display loop
def readKey(n=1):
    global keyq
    k = cv.waitKey(n)
    if k != -1:
        keyq.append(k)

def getKey():
    readKey()
    global keyq
    if len(keyq) > 0:
        return keyq.pop(0)
    else:
        return -1


def newNamedWindow(wname, psizex=320,psizey=240, pposx=-1, pposy=-1):
    sizex=psizex
    sizey=psizey
    global nextWindowx, nextWindowy, nextRowWindowy
    if pposx == -1:
        posx = nextWindowx
    else:
        posx = pposx
    if pposy == -1:
        posy = nextWindowy
    else:
        posy = pposy

    # positions the window.
    # if it's too far to the right, move it to the next row
    if posx + sizex > 1920:
        print(f"{wname}: sizex({sizex}) + posx({posx}) > 1920; moving {wname} to next row")
        posx = 0
        print(f"{wname}: posx={posx}")
        posy = nextRowWindowy
        print(f"{wname}: posy={posy}; nextRowWindowy={nextRowWindowy}")
        nextRowWindowy = nextRowWindowy + sizey

    cv.namedWindow(wname, cv.WINDOW_AUTOSIZE); readKey(100)
    print(f"{wname}: moving to posx={posx} posy={posy}")
    for qq in range(1):
        cv.moveWindow(wname, posx, posy); readKey()
    readKey(1)
    for qq in range(1):
        cv.resizeWindow(wname, sizex, sizey); readKey();
    readKey(1)
    # now compute where the next window should go
    nextWindowx += sizex
    nextRowWindowy = max(nextRowWindowy, posy+sizey)
    if nextWindowx > 1920:
        nextWindowx = 0
        nextWindowy = nextRowWindowy
        nextRowWindowy += sizey

    #print(f"{wname}: nextWindowx={nextWindowx} nextWindowy={nextWindowy} nextRowWindowy={nextRowWindowy}")
    return wname


newNamedWindow('flow1', 400,500)
newNamedWindow('flow2', 400,500)
newNamedWindow('flow3', 400,500)
newNamedWindow('flow4', 400,500)
newNamedWindow('flowdiff',600,500)

def showImage(wname, img):
    cv.imshow(wname, img)
    readKey()

while(cap.isOpened()):

    while len(raw_frames) < ANALYSIS_FRAME_COUNT:
        ret, inframe = cap.read() 
        if ret==False:
            break

        raw_frames.append(cv.UMat(inframe))
        gray_frames.append((cv.cvtColor(cv.UMat(inframe), cv.COLOR_BGR2GRAY)))
    if not ret:
        break


    flow1,flow1mag,flow1dir = calcFlow(0,1)
    flow2,flow2mag,flow2dir = calcFlow(1,2)
    flow3,flow3mag,flow3dir = calcFlow(2,3)
    flow4,flow4mag,flow4dir = calcFlow(3,4)

    #flow01mag = cv.normalize(flow01mag, None, 0.0, 0.1, cv.NORM_MINMAX, cv.CV_32F)
    #flow12mag = cv.normalize(flow12mag, None, 0.0, 0.1, cv.NORM_MINMAX, cv.CV_32F)
    #flowdiff = cv.UMat(np.zeros_like(flow01.get()))
    flowdiff = cv.multiply(cv.multiply(cv.multiply(flow1mag, flow2mag), flow3mag), flow4mag)
    flowdiff = cv.divide(flowdiff,4)

    if True:
        #flowdiff = cv.UMat(np.zeros_like(flow01.get()))
        #flowdiff = cv.subtract(flow12, flow01)
        #flowdiffmag, _ = cv.cartToPolar(cv.UMat(flowdiff.get()[..., 0]), cv.UMat(flowdiff.get()[..., 1]))

        flowdiffmag = cv2.multiply(flowdiff , 2, dtype=cv.CV_8UC1)
        print(flowdiffmag.get().max())
        #cv.normalize(flowdiff, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
        #cv.imwrite(f"{jpgdir}/flowdiffmag{i:04d}.jpg", flowdiffmag)
        #cv.imwrite(f"{jpgdir}/flow01{i:04d}.jpg", flow01)

        showImage('flow1', flow1mag)
        showImage('flow2', flow2mag)
        showImage('flow3', flow3mag)
        showImage('flow4', flow4mag)
        showImage('flowdiff', flowdiffmag)

        k=getKey()
        if (k & 0xFF) in { ord('q'), 27,3 }:
            cap.release()
            break
        if (k & 0xFF) == ord(' '):
            break
        if (k & 0xFF) == ord('s'):
            cv.imwrite(f"{jpgdir}/flow01{i:04d}.jpg", flow01)
            cv.imwrite(f"{jpgdir}/flow12{i:04d}.jpg", flow12)
            cv.imwrite(f"{jpgdir}/flowdiff{i:04d}.jpg", flowdiff)
            cv.imwrite(f"{jpgdir}/flow01mag{i:04d}.jpg", flow01mag)
            cv.imwrite(f"{jpgdir}/flow12mag{i:04d}.jpg", flow12mag)
            cv.imwrite(f"{jpgdir}/flowdiffmag{i:04d}.jpg", flowdiffmag)
            print("saved.")

    """flow01mag = cv.multiply(flow01mag, 1) #cv.normalize(flow01mag, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
    cv.imwrite(f"{jpgdir}/flow01mag{i:04d}.jpg", flow01mag)
    flow12mag = cv.multiply(flow12mag, 1) #cv.normalize(flow12mag, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
    cv.imwrite(f"{jpgdir}/flow12mag{i:04d}.jpg", flow12mag)
    flowdiffmag = cv.multiply(flowdiffmag, 1) #cv.normalize(flowdiffmag, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
    cv.imwrite(f"{jpgdir}/flowdiffmag{i:04d}.jpg", flowdiffmag)"""



    graymask_main = cv.threshold(flowdiffmag, 30, 255, cv.THRESH_BINARY)[1]


    #graymask_main = prep_graymask(calcFlow(2,4))
    #graymask_comp = prep_graymask(calcFlow(1,3))
    conts, heirarchy = cv.findContours(graymask_main, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    #print(len(conts))
    areas = []
    this_frame = raw_frames[PICTURE_FRAME].get()
    for j in range(len(conts)):
        cont = conts[j]
        x,y,w,h = cv.boundingRect(cont)
        area = cv.contourArea(cont)
        rectarea = w*h
        areas += [area]
        cv.rectangle(this_frame,(x,y),(x+w,y+h),(0,255,0),2)

    for j in range(len(conts)):
        cont = conts[j].get()
        if False: # comparison with previous flow, disabled for now
            blank = np.zeros_like(graymask_main.get()).astype(np.uint8)
            cv.drawContours(blank, [cont], -1, 1, cv.FILLED)
            pixelcount = cv.countNonZero(blank)
            blank = cv.multiply(blank, graymask_comp)
            pixelcountafter = cv.countNonZero(blank)
            print(f"[{pixelcountafter}:{pixelcount}]")
            if pixelcountafter < pixelcount*0.3:
                continue
        x,y,w,h = cv.boundingRect(cont)
        blob = raw_frames[PICTURE_FRAME].get()[y:y+h,x:x+w].copy()
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

        subframes = [ np.zeros((MAX_SAMPLE_DIM,MAX_SAMPLE_DIM,3), dtype=np.uint8) ] * ANALYSIS_FRAME_COUNT
        print(f"({destx},{desty}) ({destw},{desth}) ({sourcex},{sourcey}) ({sourcew},{sourceh})")
        print(f"len(subframes)={len(subframes)}")
        for k in range(ANALYSIS_FRAME_COUNT):
            this_raw_frame = raw_frames[k].get()
            subframes[k] = np.zeros((MAX_SAMPLE_DIM,MAX_SAMPLE_DIM,3), dtype=np.uint8)
            subframes[k][desty:(desty+desth),destx:(destx+destw),:] = this_raw_frame[sourcey:(sourcey+sourceh),sourcex:(sourcex+sourcew),:]
            subframes[k] = cv.rectangle(subframes[k],(x-sx,y-sy),(x+w-sx,y+h-sy),(0,205,205),1)

        # Write some Text

        font                   = cv.FONT_HERSHEY_SIMPLEX
        fontScale              = 0.3
        fontColor              = (0,255,255)
        lineType               = 1
       
        for k in range(ANALYSIS_FRAME_COUNT):
            putShadowedText(subframes[k],f"{k-PICTURE_FRAME}", 10,10, font, fontScale, fontColor, lineType)
            putShadowedText(subframes[k],f"{j}", 10,20, font, fontScale, fontColor, lineType)
            putShadowedText(subframes[k],f"{i}", 10,30, font, fontScale, fontColor, lineType)
        for k in range(ANALYSIS_FRAME_COUNT):
            cv.imwrite(f"{jpgdir}/sfr{i:04d}_c{j:04d}_sf{k}.jpg", subframes[k])

        os.system(f'/bin/bash -c \'cat {jpgdir}/sfr{i:04d}_c{j:04d}_sf{{0,1,2,3,4,2,2,2,2}}.jpg\' | ffmpeg -v 0 -y -f jpeg_pipe -r 5 -i -  -vf "scale=iw:ih,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"     {contsdir}/sfr{i:04d}_c{j:04d}_sfs.gif')
        # create sqlite record
        cv.imwrite(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", blob)
        blob = open(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfBLOB.jpg", 'rb').read()
        blob_still_context = open(f"{jpgdir}/sfr{i:04d}_c{j:04d}_sf{PICTURE_FRAME}.jpg", 'rb').read()
        blob_animated_context = open(f"{contsdir}/sfr{i:04d}_c{j:04d}_sfs.gif", 'rb').read()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO samples (sourcemedia_base, frame_no, contour_id, x,y,w,h, image, still_context, animated_context) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (base,i,j, x,y,w,h, blob, blob_still_context, blob_animated_context))
        conn.commit()




    cv.imwrite(f"{jpgdir}/graymask{i:04d}.jpg", graymask_main)
    #cv.imwrite(f"{jpgdir}/graycomp{i:04d}.jpg", graymask_comp)
    cv.imwrite(f"{jpgdir}/frame{i:04d}.jpg",this_frame)
    # Updates previous frame 


    i += 1
    raw_frames.pop(0)
    gray_frames.pop(0)
    print(f"frame {i:04d}", end='\r')

cap.release() 

#plt.plot(flowmeanx,'-',label='x')
#plt.plot(flowmeany,'-',label='y')
#plt.legend()
#plt.savefig("flowmean.png")

