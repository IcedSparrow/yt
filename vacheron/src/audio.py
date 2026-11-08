import numpy as np, subprocess, json, wave, sys
sys.argv=['x','info']
import importlib.util
spec=importlib.util.spec_from_file_location("r","render.py"); r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
SR=48000
R="/root/.claude/uploads/d39590b1-32f9-5337-8bd8-ff80190cfa08/74ae2ed5-af8af992e7814eff9a56c65177006700-compressed.mov"
raw=subprocess.run(["ffmpeg","-v","error","-i",R,"-vn","-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
a=np.frombuffer(raw,np.float32).copy()
segs=[];f=int(0.010*SR)
for (fa,fb) in r.KEEP:
    s=a[int(fa/30*SR):int(fb/30*SR)].copy()
    s[:f]*=np.linspace(0,1,f); s[-f:]*=np.linspace(1,0,f); segs.append(s)
v=np.concatenate(segs)
v=v[:int(r.NF/30*SR)]
def ww(p,x):
    x=np.clip(x,-1,1); w=wave.open(p,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
ww("voice_cut.wav",v)
# SFX synthesis
rng=np.random.default_rng(7)
def env(n,att,dec):
    t=np.arange(n)/SR; return np.minimum(1,t/att)*np.exp(-t/dec)
def bp(x,lo,hi):
    X=np.fft.rfft(x); fr=np.fft.rfftfreq(len(x),1/SR); X[(fr<lo)|(fr>hi)]=0; return np.fft.irfft(X,len(x))
def swoosh(d=0.5,lo=400,hi=3500):
    n=int(d*SR); x=rng.standard_normal(n); t=np.linspace(0,1,n)
    out=np.zeros(n); k=8
    for i in range(k):
        sl=slice(i*n//k,(i+1)*n//k); c=lo*(hi/lo)**(i/k); out[sl]=bp(x,c*0.6,c*1.6)[sl]
    e=np.sin(np.pi*t)**2; return out*e/np.max(np.abs(out*e))
def tick():
    n=int(0.05*SR); t=np.arange(n)/SR
    x=np.sin(2*np.pi*3200*t)*env(n,0.0005,0.006)+0.5*np.sin(2*np.pi*5400*t)*env(n,0.0003,0.004)+0.2*bp(rng.standard_normal(n),2000,8000)*env(n,0.0002,0.003)
    return x/np.max(np.abs(x))
def click():
    n=int(0.04*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*1800*t)*env(n,0.0005,0.008); return x/np.max(np.abs(x))
def hit():
    n=int(0.9*SR); t=np.arange(n)/SR; f=55+40*np.exp(-t/0.05)
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.003,0.25)+0.3*bp(rng.standard_normal(n),60,600)*env(n,0.001,0.04)
    return x/np.max(np.abs(x))
def typ():
    n=int(0.6*SR); x=np.zeros(n)
    for i in range(7):
        o=int(i*0.075*SR+rng.integers(0,300)); c=click()*0.6; x[o:o+len(c)]+=c[:n-o]
    return x
lib={"swoosh":swoosh(0.55),"swoosh_s":swoosh(0.42,700,4500),"tick":tick(),"click":click(),"hit":hit(),"type":typ()}
gain={"swoosh":0.10,"swoosh_s":0.06,"tick":0.07,"click":0.10,"hit":0.30,"type":0.05}
fx=np.zeros(len(v)+SR)
r.build("A")
for t,k in r.SFX:
    o=int(max(0,t-(0.15 if k.startswith("swoosh") else 0))*SR); s=lib[k]*gain[k]; fx[o:o+len(s)]+=s[:len(fx)-o]
ww("sfx.wav",fx[:len(v)])
print("ok",len(v)/SR, len(r.SFX))
