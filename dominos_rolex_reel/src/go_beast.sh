#!/bin/bash
# usage: go.sh OUTPREFIX [hookvariant] ; renders all frames in 4 parallel chunks
N=$(python3 render_beast.py info 2>/dev/null | head -1 | awk '{print $4}')
P=$1; HV=$2
C=$(( (N+3)/4 ))
for i in 0 1 2 3; do a=$((i*C)); b=$(( (i+1)*C )); [ $b -gt $N ] && b=$N
  python3 render_beast.py range $a $b ${P}_part$i.mp4 $HV 2>/dev/null &
done; wait
printf "file '%s'\n" ${P}_part0.mp4 ${P}_part1.mp4 ${P}_part2.mp4 ${P}_part3.mp4 > ${P}_list.txt
ffmpeg -v error -y -f concat -safe 0 -i ${P}_list.txt -c copy ${P}_video.mp4
echo done $N
