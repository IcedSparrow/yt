import numpy as np, json
sr=48000
KEEP=json.load(open('keep.json')); B=json.load(open('beats.json'))
OUT=[];acc=0
for a,b in KEEP: OUT.append(acc); acc+=b-a
DUR=acc
def O(r):
    for (a,b),s in zip(KEEP,OUT):
        if r<a: return s
        if r<=b: return s+(r-a)
    return DUR
a=np.fromfile('a48s.raw',np.float32).reshape(-1,2)
F=int(0.010*sr); ramp=np.linspace(0,1,F)[:,None]; parts=[]
for x,y in KEEP:
    seg=a[int(x*sr):int(y*sr)].copy(); seg[:F]*=ramp; seg[-F:]*=ramp[::-1]; parts.append(seg)
v=np.concatenate(parts)[:int(round(DUR*sr))]; v.astype(np.float32).tofile('voice_cut.raw')
rng=np.random.default_rng(3)
def swoosh():
    n=int(0.5*sr); x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/sr); X*=np.exp(-((f-1500)/1300)**2)
    x=np.fft.irfft(X,n); t=np.arange(n)/sr; x*=np.sin(np.pi*t/0.5)**2; return x/np.abs(x).max()*0.08
def tick():
    t=np.arange(int(0.05*sr))/sr; return (np.sin(2*np.pi*3000*t)*np.exp(-t/0.006)+0.4*np.sin(2*np.pi*5200*t)*np.exp(-t/0.003))*0.045
def click():
    t=np.arange(int(0.04*sr))/sr; return (rng.standard_normal(len(t))*np.exp(-t/0.002)*0.5+np.sin(2*np.pi*1500*t)*np.exp(-t/0.008))*0.065
def hit():
    t=np.arange(int(1.0*sr))/sr; ph=2*np.pi*np.cumsum(48+40*np.exp(-t/0.05))/sr
    return (np.sin(ph)*np.exp(-t/0.3)+0.12*rng.standard_normal(len(t))*np.exp(-t/0.03))*0.10
ev=[]
for b in B:
    t0=O(b['raw']); L=b['layout']
    if L=='hook': continue
    ev.append((t0,'tick' if L=='full' and not b.get('follow') else 'swoosh'))
    if L=='doc': ev+=[(O(b['ts']),'click'),(O(b['tm']),'tick'),(O(b['tc']),'tick')]
    if L=='pin': ev+=[(O(b['tp'])+0.4,'click'),(O(b['tn']),'tick')]
    if L=='brands': ev+=[(O(x),'tick') for x in b['tt']]
    if L=='funnel': ev+=[(O(b['t2']),'tick'),(O(b['t3']),'tick')]
    if b.get('ring_t'): ev.append((O(b['ring_t']),'tick'))
    if b.get('pill_t'): ev.append((O(b['pill_t']),'tick'))
    if L=='comment': ev.append((O(b['tt']),'click'))
    if b.get('follow'): ev+=[(O(b['tap']),'click'),(O(b['tap']),'hit')]
gen=dict(swoosh=swoosh,tick=tick,click=click,hit=hit)
s=np.zeros(len(v))
for t,k in ev:
    x=gen[k](); i=int(max(0,t-(0.2 if k=='swoosh' else 0))*sr); j=min(len(s),i+len(x)); s[i:j]+=x[:j-i]
np.save('sfx_mono.npy',s); json.dump(ev,open('sfx_events.json','w')); print(len(ev),'events', DUR)
