import subprocess,sys,os
V="/root/.claude/uploads/98795890-45f8-5e48-8acf-721350fc4bbc/65bce7d5-b4d40bc6-c6eb-49d6-91e8-248b3032298a.mov"
exec(open('build2.py').read().split("f=[]")[0].split("import subprocess,sys")[1])
os.makedirs('clips',exist_ok=True)
Ls=[]
for i,(ka,kb,s0,s1,tr,d) in enumerate(C):
    a,b=T(ka),T(kb) if kb<61 else TOT
    din=d/2; dout=C[i+1][5]/2 if i+1<len(C) else 0
    L=(b+dout)-(a-din); sp=(s1-s0)/L; Ls.append(L)
    if i==len(C)-1: rt="framerate=fps=30"
    elif sp<0.97: rt="minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none"
    else: rt="fps=30"
    out=f'clips/c{i}.mp4'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(max(0,s0-1)),'-i',V,'-vf',f"trim={s0-max(0,s0-1)}:{s1-max(0,s0-1)},setpts=(PTS-STARTPTS)/{sp:.5f},{rt},tpad=stop_mode=clone:stop_duration=0.5,trim=0:{L:.4f},setpts=PTS-STARTPTS,format=yuv420p",'-r','30','-an','-c:v','libx264','-crf','10','-preset','fast',out],check=True)
    n=subprocess.run(['ffprobe','-v','error','-count_frames','-show_entries','stream=nb_read_frames','-of','csv=p=0',out],capture_output=True,text=True).stdout.strip()
    print(i,'L %.3f expect %d got %s speed %.3f'%(L,round(L*30),n,sp),file=sys.stderr)
inp=[];f=[]
for i in range(len(C)):
    inp+=['-i',f'clips/c{i}.mp4']; punch=",scale=w='2*trunc(360*(1+0.08*pow(max(0\\,1-t/0.32)\\,2)))':h=-2:eval=frame:flags=lanczos,crop=720:1280" if i==11 else ""
    f.append(f"[{i}:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.3,trim=0:{Ls[i]:.4f},setpts=PTS-STARTPTS,settb=1/30,fps=30,setsar=1{punch}[c{i}]")
prev='c0'
for i in range(1,len(C)):
    ka,_,_,_,tr,d=C[i]; off=T(ka)-d/2
    f.append(f"[{prev}][c{i}]xfade=transition={tr}:duration={d}:offset={off:.4f}[x{i}]"); prev=f"x{i}"
f.append(f"[{prev}]eq=contrast=1.04:saturation=1.05:gamma=0.99,colorbalance=rh=0.015:bh=-0.012:rm=0.01,unsharp=5:5:0.45:3:3:0,trim=0:{TOT:.4f},setpts=PTS-STARTPTS[vout]")
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(f),'-map','[vout]','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','base2.mp4'],check=True)
