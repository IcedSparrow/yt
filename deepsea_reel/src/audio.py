import numpy as np, json, subprocess, sys
sys.argv=['x','info']
exec(open('render.py').read().split("# ---------------- easing helpers")[0].replace("os.chdir(HERE)",""))
sr=48000
a=np.fromfile('a48s.raw',np.float32).reshape(-1,2)
F=int(0.010*sr); ramp=np.linspace(0,1,F)[:,None]
parts=[]
for x,y in KEEP:
    seg=a[int(x*sr):int(y*sr)].copy()
    seg[:F]*=ramp; seg[-F:]*=ramp[::-1]
    parts.append(seg)
v=np.concatenate(parts)
v=v[:int(round(DUR*sr))]
v.astype(np.float32).tofile('voice_cut.raw')
print(len(v)/sr, DUR)
# ---- SFX synth ----
rng=np.random.default_rng(7)
def env(n,a_,d_):
    t=np.arange(n)/sr; return np.minimum(1,t/a_)*np.exp(-np.maximum(0,t-a_)/d_)
def swoosh():
    n=int(0.55*sr); x=rng.standard_normal(n)
    # sweep lowpass by moving average of varying width -> simple: filter via FFT band
    X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/sr)
    X*=np.exp(-((f-1400)/1300)**2); x=np.fft.irfft(X,n)
    t=np.arange(n)/sr; e=np.sin(np.pi*np.clip(t/0.55,0,1))**2
    x=x*e; return x/np.abs(x).max()*0.16
def tick():
    n=int(0.05*sr); t=np.arange(n)/sr
    x=np.sin(2*np.pi*3200*t)*np.exp(-t/0.006)+0.4*np.sin(2*np.pi*5400*t)*np.exp(-t/0.003)
    return x*0.09
def click():
    n=int(0.04*sr); t=np.arange(n)/sr
    x=rng.standard_normal(n)*np.exp(-t/0.002)*0.5+np.sin(2*np.pi*1500*t)*np.exp(-t/0.008)
    return x*0.13
def hit():
    n=int(1.1*sr); t=np.arange(n)/sr
    f=48+40*np.exp(-t/0.05); ph=2*np.pi*np.cumsum(f)/sr
    x=np.sin(ph)*np.exp(-t/0.35)+0.15*rng.standard_normal(n)*np.exp(-t/0.03)
    return x*0.30
B=json.load(open('beats.json'))
ev=[]
for b in B:
    t0=O(b['raw']); L=b['layout']
    if L=='hook': continue
    if L in ('card','dial','dim','sapph','cameron','beam'): ev.append((t0,'swoosh'))
    elif L=='full' and not b.get('follow'): ev.append((t0,'tick'))
    else: ev.append((t0,'swoosh'))
    if L=='dial': ev.append((O(b['to'])+0.6,'tick'))
    if L=='dim': ev.append((O(b['to'])+0.6,'tick'))
    if L=='sapph': ev.append((O(b['to'])+0.6,'tick'))
    if L=='can': ev.append((O(b['tc']),'click'))
    if L=='material': ev+= [(O(b['tb']),'tick'),(O(b['ts']),'click')]
    if L=='bars': ev.append((O(b['ts']),'tick'))
    if L=='divers': ev+=[(O(x),'tick') for x in b['tr']]
    if L=='cameron': ev+=[(O(b['z1']),'swoosh'),(O(b['z2']),'swoosh')]
    if L=='dive': ev+=[(O(b['tb']),'tick'),(O(b['td']),'tick')]
    if L=='full' and b.get('punch') and not b.get('follow'): ev.append((O(b['punch'])-0.12,'tick'))
    if b.get('follow'): ev+=[(O(b['tap']),'click'),(O(b['tap']),'hit')]
gen={'swoosh':swoosh,'tick':tick,'click':click,'hit':hit}
s=np.zeros(len(v))
for t,k in ev:
    x=gen[k](); i=int(max(0,t-(0.2 if k=='swoosh' else 0))*sr); j=min(len(s),i+len(x)); s[i:j]+=x[:j-i]
np.stack([s,s],1).astype(np.float32).tofile('sfx.raw')
json.dump(ev,open('sfx_events.json','w'))
print(len(ev),'events')
