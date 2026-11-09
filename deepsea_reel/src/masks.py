# decode raw, compute border-connected white background -> alpha, store rgba memmap + per-frame stats
import numpy as np, subprocess, json
from scipy import ndimage
W,H=352,626
N=2644
rgba=np.lib.format.open_memmap('rgba.npy',mode='w+',dtype=np.uint8,shape=(N,H,W,4))
p=subprocess.Popen(['ffmpeg','-v','error','-i','raw.mov','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
stats=[]
i=0
while i<N:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    a=np.frombuffer(b,np.uint8).reshape(H,W,3).astype(np.float32)
    d=255-a.min(2)
    near=d<40
    lab,n=ndimage.label(near)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    fg=~bg
    fg=ndimage.binary_opening(fg,iterations=1)
    # keep largest component
    l2,n2=ndimage.label(fg)
    if n2>1:
        sizes=ndimage.sum(fg,l2,range(1,n2+1)); fg=l2==(1+np.argmax(sizes))
    fg=ndimage.binary_fill_holes(fg)
    # soft alpha: inside fg, edge pixels get alpha from whiteness
    er=ndimage.binary_erosion(fg,iterations=1)
    edge=fg&~er
    alpha=fg.astype(np.float32)
    soft=np.clip((d-6)/60,0,1)
    alpha[edge]=soft[edge]
    alpha=ndimage.gaussian_filter(alpha,0.6)*fg + 0  # tiny feather inside
    alpha=np.clip(alpha,0,1)
    # decontaminate white
    am=np.maximum(alpha,1e-3)[...,None]
    col=(a-(1-am)*255)/am
    col=np.clip(col,0,255)
    col[alpha<0.02]=0
    out=np.dstack([col,alpha*255]).astype(np.uint8)
    rgba[i]=out
    rows=np.where(fg.sum(1)>2)[0]
    if len(rows):
        top=int(rows.min()); bot=int(rows.max())
        hw=[]; hc=[]
        for r in range(top+50,min(top+110,H)):
            c=np.where(fg[r])[0]
            if len(c): hw.append(c.max()-c.min()); hc.append((c.max()+c.min())/2)
        stats.append([top,bot,float(np.median(hw)) if hw else 0,float(np.median(hc)) if hc else 0])
    else: stats.append([0,0,0,0])
    i+=1
rgba.flush()
json.dump(stats,open('stats.json','w'))
print('frames',i)
