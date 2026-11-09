import cv2, numpy as np, json
cap=cv2.VideoCapture('raw.mov')
cc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
res=[];i=0
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    fs=cc.detectMultiScale(g,1.1,5,minSize=(100,100))
    if len(fs): x,y,w,h=max(fs,key=lambda r:r[2]*r[3]); res.append([int(x),int(y),int(w),int(h)])
    else: res.append(None)
    i+=1
json.dump(res,open('faces.json','w'))
a=np.array([r for r in res if r]); print(i,'frames, detected',len(a))
print('x',np.percentile(a[:,0],[5,50,95]),'y',np.percentile(a[:,1],[1,5,50,95]),'w',np.percentile(a[:,2],[5,50,95]))
