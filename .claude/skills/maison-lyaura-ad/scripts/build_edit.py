#!/usr/bin/env python3
"""Build the beat-synced picture edit (no graphics) from an edit plan.
Usage: python3 build_edit.py plan.json out.mp4
plan.json: {"source": "...mov", "beat": 0.472, "first_beat": 0.04, "end_k": 61,
  "hdr": false,
  "clips": [[k_start, k_end, src_start, src_end, transition_in, duration, opts?], ...]}
- Cut times are on the beat grid: B(k)=first_beat+beat*k (k=0 means t=0); the last clip ends at B(end_k).
- transition_in: null for the first clip; 'fade' with 0.067 = hard cut; 'fade' 0.3 = soft dissolve;
  'smoothleft'/'smoothright' 0.2-0.27 = whip/slide. Avoid hblur/zoomin (they look hazy).
- Any source size is scaled to 720x1280 before interpolation; source cuts inside a clip are respected (scd=fdiff).
- opts: {"punch": true} adds a crisp 8% punch-in at the clip start (use on the drop instead of a zoom dissolve);
        {"endbg": true} for the end-card background clip (very slow; blurred later, frame-blended).
- Speed per clip = source length / (slot + transition handles). Keep it 0.85-1.1x: below 0.97 the clip is
  slowed with motion-compensated interpolation (sharp, no ghosting). Never use framerate blending or zoompan
  on visible footage: they cause stutter/blur (user complaint)."""
import json,subprocess,sys,os
P=json.load(open(sys.argv[1])); OUT=sys.argv[2]; V=P['source']
B=lambda k:0.0 if k==0 else P['first_beat']+P['beat']*k
TOT=B(P['end_k']); C=P['clips']; cd=os.path.splitext(OUT)[0]+'_clips'; os.makedirs(cd,exist_ok=True)
hdr=",scale=in_color_matrix=bt2020:out_color_matrix=bt709" if P.get('hdr') else ""
Ls=[]
for i,c in enumerate(C):
    ka,kb,s0,s1,tr,d=c[:6]; o=c[6] if len(c)>6 else {}
    a,b=B(ka),(B(kb) if kb<P['end_k'] else TOT); din=d/2; dout=C[i+1][5]/2 if i+1<len(C) else 0
    L=(b+dout)-(a-din); sp=(s1-s0)/L; Ls.append(L)
    rt="framerate=fps=30" if o.get('endbg') else ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=fdiff:scd_threshold=12" if sp<0.97 else "fps=30")
    print(f"clip {i}: {a:.2f}-{b:.2f}s src {s0}-{s1} speed {sp:.3f} via {rt.split('=')[0]}",file=sys.stderr)
    out=f'{cd}/c{i}_{s0}_{s1}_{L:.3f}.mp4'
    if not os.path.exists(out):
        pre=max(0,s0-1)
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(pre),'-i',V,'-vf',f"trim={s0-pre}:{s1-pre},setpts=(PTS-STARTPTS)/{sp:.5f}{hdr},scale=720:1280:flags=lanczos,{rt},tpad=stop_mode=clone:stop_duration=0.5,trim=0:{L:.4f},setpts=PTS-STARTPTS,format=yuv420p",'-r','30','-an','-c:v','libx264','-crf','10','-preset','fast',out],check=True)
    C[i]=c+[out] if len(c)>6 else c+[{},out]
inp=[];f=[]
for i,c in enumerate(C):
    inp+=['-i',c[-1]]; o=c[6]
    punch=",scale=w='2*trunc(360*(1+0.08*pow(max(0\\,1-t/0.32)\\,2)))':h=-2:eval=frame:flags=lanczos,crop=720:1280" if o.get('punch') else ""
    f.append(f"[{i}:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.3,trim=0:{Ls[i]:.4f},setpts=PTS-STARTPTS,settb=1/30,fps=30,setsar=1{punch}[c{i}]")
prev='c0'
for i in range(1,len(C)):
    tr,d=C[i][4],C[i][5]; f.append(f"[{prev}][c{i}]xfade=transition={tr}:duration={d}:offset={B(C[i][0])-d/2:.4f}[x{i}]"); prev=f"x{i}"
f.append(f"[{prev}]eq=contrast=1.04:saturation=1.05:gamma=0.99,colorbalance=rh=0.015:bh=-0.012:rm=0.01,unsharp=5:5:0.45:3:3:0,trim=0:{TOT:.4f},setpts=PTS-STARTPTS[v]")
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(f),'-map','[v]','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p',OUT],check=True)
print(f"built {OUT}: {TOT:.3f}s ({round(TOT*30)} frames expected)",file=sys.stderr)
