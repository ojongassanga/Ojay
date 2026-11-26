import subprocess,sys
V="/root/.claude/uploads/98795890-45f8-5e48-8acf-721350fc4bbc/65bce7d5-b4d40bc6-c6eb-49d6-91e8-248b3032298a.mov"
B=lambda k:0.04+0.472*k
TOT=B(61)
# k_start, k_end, src0, src1, transition_in, dur
C=[(0,4,6.30,8.18,None,0),
(4,8,8.30,10.05,'fade',0.30),
(8,11,2.40,3.85,'fade',0.30),
(11,12,4.86,5.38,'fade',0.067),
(12,13,0.95,1.45,'fade',0.067),
(13,14,3.97,4.40,'fade',0.067),
(14,23,10.15,14.48,'smoothleft',0.22),
(23,25,26.25,27.28,'smoothleft',0.2),
(25,29,18.66,20.42,'fade',0.067),
(29,33,16.75,18.56,'fade',0.067),
(33,37,15.10,16.66,'smoothright',0.22),
(37,41,20.52,22.30,'fade',0.067),
(41,45,22.38,24.20,'fade',0.067),
(45,49,24.28,26.24,'fade',0.067),
(49,61,26.24,27.28,'fade',0.067)]
T=lambda k:0.0 if k==0 else B(k)
f=[]
for i,(ka,kb,s0,s1,tr,d) in enumerate(C):
    a,b=T(ka),T(kb) if kb<61 else TOT
    din=d/2; dout=C[i+1][5]/2 if i+1<len(C) else 0
    L=(b+dout)-(a-din); sp=(s1-s0)/L
    if i==len(C)-1: rt="framerate=fps=30"
    elif sp<0.97: rt="minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none"
    else: rt="fps=30"
    print(i,'slot %.2f-%.2f len %.3f speed %.3f %s'%(a,b,L,sp,rt.split('=')[0]),file=sys.stderr)
    f.append(f"[0:v]trim={s0}:{s1},setpts=(PTS-STARTPTS)/{sp:.5f},{rt},tpad=stop_mode=clone:stop_duration=0.3,trim=0:{L:.4f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1,settb=1/30[c{i}]")
prev='c0'
for i in range(1,len(C)):
    ka,_,_,_,tr,d=C[i]; off=T(ka)-d/2
    f.append(f"[{prev}][c{i}]xfade=transition={tr}:duration={d}:offset={off:.4f}[x{i}]"); prev=f"x{i}"
f.append(f"[{prev}]eq=contrast=1.04:saturation=1.05:gamma=0.99,colorbalance=rh=0.015:bh=-0.012:rm=0.01,unsharp=5:5:0.45:3:3:0,trim=0:{TOT:.4f},setpts=PTS-STARTPTS[vout]")
print('TOT',TOT,file=sys.stderr)
subprocess.run(['ffmpeg','-v','error','-y','-i',V,'-filter_complex',';'.join(f),'-map','[vout]','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','base2.mp4'],check=True)
