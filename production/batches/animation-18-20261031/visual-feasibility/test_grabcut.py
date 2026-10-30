"""CPU-only feasibility baseline; NOT a production-approved matte."""
from pathlib import Path
import sys, json, time, subprocess
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'local-deps'))
import cv2
import numpy as np
cv2.setNumThreads(2)
cap=cv2.VideoCapture(str(HERE/'source-4s.mp4'))
w,h=1920,1080
aw,ah=960,540
fps=cap.get(cv2.CAP_PROP_FPS)
writer=cv2.VideoWriter(str(HERE/'grabcut-raw.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
grid=np.full((h,w,3),238,np.uint8)
for x in range(0,w,40): cv2.line(grid,(x,0),(x,h),(209,209,209),1)
for y in range(0,h,40): cv2.line(grid,(0,y),(w,y),(209,209,209),1)
cv2.line(grid,(0,1010),(w,1010),(50,50,230),5)
cv2.line(grid,(1240,0),(1240,h),(225,120,70),4)
grid[1015:]=np.minimum(grid[1015:],208)
prevgray=None
prevmask=None
metrics=[]
start=time.time()
frameid=0
while True:
    ok,frame=cap.read()
    if not ok: break
    small=cv2.resize(frame,(aw,ah))
    gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
    if prevmask is None:
        mask=np.full((ah,aw),cv2.GC_BGD,np.uint8)
        # Loose foreground window and internal positive strokes observed at 12 s.
        mask[245:539,510:850]=cv2.GC_PR_FGD
        strokes=[((622,298),(634,335),10),((666,329),(705,382),17),
                 ((706,397),(737,426),13),((737,426),(796,513),10),
                 ((670,402),(618,486),9),((636,359),(563,370),7)]
        for a,b,r in strokes: cv2.line(mask,a,b,cv2.GC_FGD,r)
    else:
        # Backward optical flow transports the previous segmentation, without inventing motion.
        flow=cv2.calcOpticalFlowFarneback(gray,prevgray,None,.5,3,19,3,5,1.1,0)
        xx,yy=np.meshgrid(np.arange(aw,dtype=np.float32),np.arange(ah,dtype=np.float32))
        warped=cv2.remap(prevmask,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_NEAREST)
        dil=cv2.dilate(warped,np.ones((13,13),np.uint8))
        core=cv2.erode(warped,np.ones((9,9),np.uint8))
        mask=np.full((ah,aw),cv2.GC_BGD,np.uint8)
        mask[dil>0]=cv2.GC_PR_BGD
        mask[warped>0]=cv2.GC_PR_FGD
        mask[core>0]=cv2.GC_FGD
    bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
    try: cv2.grabCut(small,mask,None,bg,fg,2,cv2.GC_INIT_WITH_MASK)
    except cv2.error: pass
    matte=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    prevmask=matte
    prevgray=gray
    alpha=cv2.resize(matte.astype(np.float32)/255,(w,h),interpolation=cv2.INTER_LINEAR)
    alpha=cv2.GaussianBlur(alpha,(3,3),.5)[...,None]
    result=(frame*alpha+grid*(1-alpha)).astype(np.uint8)
    cv2.rectangle(result,(18,18),(1130,102),(22,22,22),-1)
    cv2.putText(result,'CPU BASELINE / EDITORIAL BACKGROUND COMPOSITE',(38,54),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(result,'NOT an animation-editor output. Quality test only.',(38,84),cv2.FONT_HERSHEY_SIMPLEX,.65,(80,220,255),1,cv2.LINE_AA)
    writer.write(result)
    metrics.append({'frame':frameid,'foregroundPixels':int((matte>0).sum())})
    if frameid in [0,15,30,45,60,90,120,150,180,210,238]:
        cv2.imwrite(str(HERE/f'compare-{frameid:03d}.jpg'),np.concatenate((cv2.resize(frame,(960,540)),cv2.resize(result,(960,540))),axis=1))
    frameid+=1
writer.release();cap.release()
meta={'method':'OpenCV GrabCut + backward optical-flow propagation; manual first-frame interior strokes','sourceStartSeconds':12,'sourceEndSeconds':16,'frames':frameid,'fps':fps,'output':[w,h],'segmentationAnalysis':[aw,ah],'gpuUsed':False,'elapsedSeconds':time.time()-start,'metrics':metrics,'productionAccepted':False,'review':'pending moving visual review'}
(HERE/'grabcut-test-metrics.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in meta.items() if k!='metrics'}))
