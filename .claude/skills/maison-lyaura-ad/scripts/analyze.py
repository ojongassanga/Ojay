#!/usr/bin/env python3
"""Analyze a source video before storyboarding.
Usage: python3 analyze.py VIDEO [outdir]
Prints: format/HDR info, tempo + beat grid + likely downbeat phase, strong onsets,
cut candidates, per-second saturation (to spot baked-in pink/colour wipes on B&W shots),
and writes a 4fps timecoded filmstrip (strip.jpg) to inspect shots visually."""
import sys,subprocess,re,os,json,wave
import numpy as np
V=sys.argv[1]; O=sys.argv[2] if len(sys.argv)>2 else '.'; os.makedirs(O,exist_ok=True)
def run(c): return subprocess.run(c,capture_output=True,text=True).stdout+subprocess.run(c,capture_output=True,text=True).stderr
print(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,color_transfer','-of','compact',V]))
print("If color_transfer is arib-std-b67 (HLG) or smpte2084, the source is iPhone HDR: convert with scale=in_color_matrix=bt2020:out_color_matrix=bt709.\n")
wav=os.path.join(O,'audio.wav'); subprocess.run(['ffmpeg','-v','error','-y','-i',V,'-vn','-ac','1','-ar','16000',wav],check=True)
w=wave.open(wav); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
hop=256;n=1024
fr=np.lib.stride_tricks.sliding_window_view(x,n)[::hop]*np.hanning(n)
S=np.log1p(np.abs(np.fft.rfft(fr,axis=1))*10); fq=np.fft.rfftfreq(n,1/sr)
def fl(sel): f=np.maximum(0,np.diff(S[:,sel],axis=0)).sum(1); return (f-f.mean())/f.std()
full=fl(slice(None)); low=fl(fq<150); t=np.arange(len(full))*hop/sr; D=len(x)/sr
best=(0,0,0)
for p in np.arange(0.33,0.75,0.0005):
  for o in np.arange(0,p,0.005):
    s=np.interp(np.arange(o,D-0.1,p),t,full).sum()/ (D/p)
    if s>best[0]: best=(s,p,o)
_,p,o=best; bt=np.arange(o,D,p); al=np.interp(bt,t,low); af=np.interp(bt,t,full)
print(f"TEMPO: beat {p:.4f}s = {60/p:.1f} BPM, first beat {o:.3f}s, bar {4*p:.3f}s")
for k in range(4): print(f"  beat position {k}: kick {al[k::4].mean():.2f} onset {af[k::4].mean():.2f} first at {bt[k]:.3f}s")
print("  -> treat the position with the strongest kick+onset as the bar downbeat; cut on downbeats/beats B(k)=first+beat*k")
pk=[t[i] for i in range(1,len(full)-1) if full[i]>2 and full[i]>=full[i-1] and full[i]>=full[i+1]]
print("STRONG ONSETS:",' '.join(f'{v:.2f}' for v in pk))
k=np.convolve(np.maximum(al,0),np.ones(8)/8,'same'); print("KICK ENERGY per bar:",' '.join(f'{bt[i]:.1f}:{k[i]:.1f}' for i in range(0,len(bt),4)),"(a jump marks the drop)")
sc=run(['ffmpeg','-i',V,'-an','-vf',"scale=180:-1,select='gte(scene,0)',metadata=print",'-f','null','-'])
tt=None;cuts=[]
for l in sc.split('\n'):
  m=re.search(r'pts_time:([\d.]+)',l)
  if m: tt=float(m.group(1))
  m=re.search(r'scene_score=([\d.]+)',l)
  if m and float(m.group(1))>0.2: cuts.append(f'{tt:.2f}({float(m.group(1)):.2f})')
print("CUT CANDIDATES time(score):",' '.join(cuts))
st=run(['ffmpeg','-i',V,'-an','-vf','scale=90:160,signalstats,metadata=print:key=lavfi.signalstats.SATAVG','-f','null','-'])
sat=[];tt=None
for l in st.split('\n'):
  m=re.search(r'pts_time:([\d.]+)',l)
  if m: tt=float(m.group(1))
  m=re.search(r'SATAVG=([\d.]+)',l)
  if m: sat.append((tt,float(m.group(1))))
print("SATURATION per 0.25s (spikes inside a B&W shot = baked-in colour wipe/ghost, avoid those frames):")
print(' '.join(f'{a:.2f}:{np.mean([s for t2,s in sat if a<=t2<a+0.25]):.0f}' for a in np.arange(0,D,0.25) if any(a<=t2<a+0.25 for t2,_ in sat)))
subprocess.run(['ffmpeg','-v','error','-y','-i',V,'-vf',"fps=4,scale=96:-1,drawtext=text='%{pts\\:hms}':x=2:y=2:fontsize=12:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=16x10",'-frames:v','1',os.path.join(O,'strip.jpg')])
print("Filmstrip:",os.path.join(O,'strip.jpg'),"- read it; look for black tails, glitch frames, app transitions (ghosting/glow).")
