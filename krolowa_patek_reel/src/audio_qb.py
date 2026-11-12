import numpy as np, json
sr=48000
KEEP=json.load(open('keep.json')); B=json.load(open('beats_qb.json'))
OUT=[];acc=0
for a,b in KEEP: OUT.append(acc); acc+=b-a
DUR=acc
def O(r):
    for (a,b),s in zip(KEEP,OUT):
        if r<a: return s
        if r<=b: return s+(r-a)
    return DUR
rng=np.random.default_rng(5)
def T(d): return np.arange(int(d*sr))/sr
def whoosh():
    n=int(0.32*sr); x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/sr); X*=np.exp(-((f-1800)/1600)**2); x=np.fft.irfft(X,n)
    t=T(0.32)[:n]; e=np.sin(np.pi*np.clip(t/0.32,0,1))**1.5; x*=e; return x/np.abs(x).max()*0.13
def pop():
    t=T(0.09); f=900*np.exp(-t/0.03)+250; return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t/0.03)*0.11
def ding():
    t=T(0.9); return (np.sin(2*np.pi*1760*t)+0.5*np.sin(2*np.pi*2640*t)+0.25*np.sin(2*np.pi*3520*t))*np.exp(-t/0.25)*0.05
def cash():
    t=T(0.7); n=rng.standard_normal(len(t))*np.exp(-t/0.02)*0.4
    b=(np.sin(2*np.pi*2093*t)+0.6*np.sin(2*np.pi*3136*t))*np.exp(-np.maximum(0,t-0.06)/0.18)*(t>0.06)
    return (n+b)*0.06
def boom():
    t=T(0.8); ph=2*np.pi*np.cumsum(55+70*np.exp(-t/0.04))/sr
    return (np.sin(ph)*np.exp(-t/0.22)+0.25*rng.standard_normal(len(t))*np.exp(-t/0.025))*0.16
def click():
    t=T(0.03); return (rng.standard_normal(len(t))*np.exp(-t/0.002)*0.5+np.sin(2*np.pi*1800*t)*np.exp(-t/0.006))*0.05
def swish():
    n=int(0.2*sr); x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/sr); X*=np.exp(-((f-3500)/1500)**2); x=np.fft.irfft(X,n)
    t=np.arange(n)/sr; x*=np.sin(np.pi*t/0.2)**2; return x/np.abs(x).max()*0.06
ev=[]
for i,b in enumerate(B):
    t0=O(b['raw']); L=b['layout']
    if i>0 and not (L=='full' and B[i-1]['layout']=='full'): ev.append((t0-0.12,'whoosh'))
    if L=='full' and not b.get('follow'): ev.append((t0+0.02,'pop'))
    for x in b.get('impacts',[]): ev.append((O(x),'boom'))
    for e in b.get('emoji',[]): ev.append((O(e[1]),'pop'))
    for sub,st in b.get('strikes',[]): ev.append((O(st),'swish'))
    if b.get('arrow'): ev.append((O(b['arrow'][4]),'swish'))
    if b.get('ring_t'): ev.append((O(b['ring_t']),'swish'))
    for ps,pt in b.get('pills',[]): ev.append((O(pt),'pop'))
    if L=='timeline': ev+=[(O(x),'ding') for x in b['lit'] if x is not None and x>=b['raw']]
    if L=='timeline' and b.get('queue'): ev+=[(O(x),'pop') for x in b['queue']]
    if L=='chat':
        ts,te=O(b['tq']),O(b['tq_end']); ev+=[(x,'click') for x in np.arange(ts,te,0.085)]
    if L=='comment':
        ts=O(b['tt']); ev+=[(x,'click') for x in np.arange(ts,ts+1.2,0.085)]
    if L=='money': ev+=[(O(b['tc'])+0.9,'cash')]+[(O(b['tw'])+k*0.13,'click') for k in range(7)]
    if L=='inflate': ev.append((O(b['tc'])+0.7,'cash'))
    if L=='pizzas': ev+=[(O(b['tg0'])+(O(b['tg1'])-O(b['tg0']))*k/27,'click') for k in range(27)]
    if L=='model': ev+=[(O(b[k]),'pop') for k in ('t1','t2','t3')]+[(O(b['t4']),'ding')]
    if L=='loan': ev+=[(O(b['ta']),'swish'),(O(b['tw']),'pop')]
    if L=='count': ev+=[(O(b['tg0'])+(O(b['tg1'])-O(b['tg0']))*k/40,'click') for k in range(40)]+[(O(b['tc'])+0.6,'ding')]
    if L=='rwait': ev+=[(O(b['tr']),'pop')]
    if L=='rank': ev+=[(O(b['tq'])+0.65,'cash')]
    if L=='scramble':
        ts=O(b['ts']); ev+=[(x,'click') for x in np.arange(O(b['raw']),ts,0.07)]
    if b.get('icon'): ev.append((O(b['icon'][3]),'ding'))
    if L=='hook': ev+=[(0.45,'swish'),(1.45,'ding')]
    if b.get('follow'): ev+=[(O(b['tap']),'click'),(O(b['tap'])+0.02,'ding')]
gen=dict(whoosh=whoosh,pop=pop,ding=ding,cash=cash,boom=boom,click=click,swish=swish)
s=np.zeros(int(round(DUR*sr)))
for t,k in ev:
    x=gen[k](); i=int(max(0,t)*sr); j=min(len(s),i+len(x)); s[i:j]+=x[:j-i]
np.save('sfx_beast.npy',s); print(len(ev),'events')
