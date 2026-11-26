import subprocess,sys
V="/root/.claude/uploads/98795890-45f8-5e48-8acf-721350fc4bbc/65bce7d5-b4d40bc6-c6eb-49d6-91e8-248b3032298a.mov"
TOT=30.5333
# out_start, out_end, src_start, src_end, transition_in, dur_in
C=[(0,2.40,6.30,8.18,None,0),
(2.40,4.29,8.30,10.05,'fade',0.40),
(4.29,6.18,2.40,3.85,'hblur',0.35),
(6.18,6.65,4.86,5.38,'fade',0.30),
(6.65,7.13,0.95,1.45,'fade',0.067),
(7.13,7.60,3.99,4.38,'fade',0.067),
(7.60,12.78,10.15,14.48,'smoothleft',0.30),
(12.78,13.73,26.25,27.28,'smoothleft',0.25),
(13.73,15.62,18.66,20.42,'fade',0.067),
(15.62,17.51,16.75,18.56,'fade',0.067),
(17.51,19.40,22.38,24.20,'zoomin',0.30),
(19.40,21.29,20.52,22.30,'fade',0.067),
(21.29,23.18,15.10,16.66,'smoothright',0.35),
(23.18,25.06,24.28,26.24,'fade',0.067),
(25.06,TOT,26.24,27.28,'fade',0.067)]
f=[];W=[]
for i,(a,b,s0,s1,tr,d) in enumerate(C):
    din=d/2
    dout=C[i+1][5]/2 if i+1<len(C) else 0
    wa,wb=a-din,b+dout; L=wb-wa; sp=(s1-s0)/L
    W.append((L,sp))
    push=0.05 if i<len(C)-1 else 0.03
    f.append(f"[0:v]trim={s0}:{s1},setpts=(PTS-STARTPTS)/{sp:.5f},framerate=fps=30,scale=1440:2560:flags=lanczos,"
             f"zoompan=z='1+{push}*on/{L*30:.1f}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=30,"
             f"trim=0:{L:.4f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1,settb=1/30[c{i}]")
prev='c0'
for i in range(1,len(C)):
    a,_,_,_,tr,d=C[i]; off=a-d/2
    f.append(f"[{prev}][c{i}]xfade=transition={tr}:duration={d}:offset={off:.4f}[x{i}]"); prev=f"x{i}"
f.append(f"[{prev}]eq=contrast=1.04:saturation=1.05:gamma=0.99,colorbalance=rh=0.015:bh=-0.012:rm=0.01,unsharp=5:5:0.4:3:3:0,trim=0:{TOT},setpts=PTS-STARTPTS[vout]")
for i,(L,sp) in enumerate(W): print(i,'len %.2f speed %.3f'%(L,sp),file=sys.stderr)
cmd=['ffmpeg','-v','error','-y','-i',V,'-filter_complex',';'.join(f),'-map','[vout]','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','base.mp4']
subprocess.run(cmd,check=True)
