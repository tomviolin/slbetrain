#!/bin/bash

# This script is used to run the optical flow algorithm on a set of images
LOCATIONCODE="SBLE"
# Usage: ./dooptflow.sh <directory> <output directory> <output video name>
rm -rf trains/$LOCATIONCODE*
for mf in mp4/$LOCATIONCODE_*.mp4; do
	echo $mf
	./optflow2.py $mf $1
	./doffmpeg.sh $mf

done
