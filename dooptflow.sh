#!/bin/bash
OF_DATESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
DAY=${OF_DATESTAMP:8:2}
MONTH=${OF_DATESTAMP:5:2}
YEAR=${OF_DATESTAMP:0:4}
HOUR=${OF_DATESTAMP:11:2}
MINUTE=${OF_DATESTAMP:14:2}
SECOND=${OF_DATESTAMP:17:2}

# This script is used to run the optical flow algorithm on a set of images
LOCATIONCODE="SBLE"
# Usage: ./dooptflow.sh <directory> <output directory> <output video name>
export OF_DATESTAMP
for mf in mp4/SLBE_*.mp4; do
	echo $mf
	./optflow2.py $mf $1
	./doffmpeg.sh $mf

done
