#!/bin/bash
base=trains/`basename $1 .mp4`
ffmpeg -v 0 -f jpeg_pipe -i <(cat $base/jpg/gray*.jpg) -preset ultrafast $base/mp4/opt_gray.mp4 -y
ffmpeg -v 0 -f jpeg_pipe -i <(cat $base/jpg/fra*.jpg) -preset ultrafast $base/mp4/opt_fra.mp4 -y
