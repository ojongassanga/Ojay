#!/usr/bin/env bash
# Usage: compose.sh base.mp4 overlay_frames_dir source_with_music end_card_start duration out.mp4 [audio_offset]
# Blurs the base from the end-card start, lays the PNG graphics on top, takes the music from the source,
# fades it out over the last 1.5s, and encodes an Instagram/Facebook-ready 720p H.264 (CRF 16, ~10 Mbps, AAC 256k 48kHz).
set -e; BASE=$1; OV=$2; SRC=$3; END=$4; DUR=$5; OUT=$6; AOFF=${7:-0}
FADE=$(python3 -c "print(max(0,$DUR-1.53))")
ffmpeg -v error -y -i "$BASE" -framerate 30 -i "$OV/%04d.png" -i "$SRC" -filter_complex "\
[0:v]split[a][b];[b]boxblur=20:2,format=yuva420p,fade=t=in:st=$END:d=0.7:alpha=1[bb];[a][bb]overlay=format=auto[base];\
[base][1:v]overlay=format=auto,format=yuv420p,setsar=1[vo];\
[2:a]atrim=$AOFF:$(python3 -c "print($AOFF+$DUR)"),asetpts=PTS-STARTPTS,afade=t=out:st=$FADE:d=1.53,aresample=48000[ao]" \
-map "[vo]" -map "[ao]" -c:v libx264 -preset slower -crf 16 -maxrate 12M -bufsize 24M -profile:v high -level 4.0 -g 60 -keyint_min 30 \
-pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -r 30 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size,bit_rate -of compact "$OUT"
