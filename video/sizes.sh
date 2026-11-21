#!/bin/bash
cd /home/claude/menu/video
for f in Colossal_Potato_Spud_Yoel Option_A_Narrated_Explainer Option_B_15s_Punchy_Ad Option_C_Spud_Deep_Voice Option_C_Spud_Talks_Calm Option_C_Spud_Talks_LipSync Option_C_Spud_Tells_It Option_D_Explainer_With_Captions; do
 for s in "4x5 1080 1350" "1x1 1080 1080" "16x9 1920 1080"; do set -- $s; tag=$1; W=$2; H=$3
  out="sizes/${f}_${tag}.mp4"; [ -s "$out" ] && continue
  ffmpeg -y -loglevel error -i "$f.mp4" -filter_complex "[0:v]split[a][b];[a]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},boxblur=30:3,eq=brightness=-0.08[bg];[b]scale=-2:${H}[fg];[bg][fg]overlay=(W-w)/2:0,format=yuv420p" -c:v libx264 -preset veryfast -crf 21 -c:a copy -movflags +faststart "$out"
 done; done
echo DONE
