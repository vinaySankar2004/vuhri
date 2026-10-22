#!/bin/sh
# frame_grid.sh video first_frame count step cols crop out.png
# Lays out frames in a grid of 360 px tiles, for checking motion one frame at a time.
# crop is w:h:x:y in source pixels, for example 1080:1100:0:250.
v=$1; a=$2; n=$3; s=$4; c=$5; crop=$6; o=$7
rows=$(( (n + c - 1) / c ))
ffmpeg -v error -y -i "$v" -vf "select='between(n\,$a\,$((a+n*s-1)))*not(mod(n-$a\,$s))',crop=$crop,scale=360:-1,tile=${c}x${rows}:padding=4:color=gray" -vsync vfr -frames:v 1 "$o"
