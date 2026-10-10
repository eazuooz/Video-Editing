"""Editable wing-tip tracking preview; disagreement is hidden, never guessed."""
from pathlib import Path
import sys,json,subprocess,math
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision'
sys.path.insert(0,str(O/'python-deps'))
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
d=json.loads((B/'wing-annotation-keyframes.json').read_text(encoding='utf8'))
start,end=d['interval'];fps=30;w,h=d['coordinatePixels'];frames=[]
dec=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(start),'-i',str(ROOT/d['sourceFile']),'-t',str(end-start),'-vf',f'scale={w}:{h},fps={fps}','-an','-f','rawvideo','-pix_fmt','bgr24','pipe:1'],stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
while True:
    raw=dec.stdout.read(w*h*3)
    if len(raw)!=w*h*3:break
    frames.append(np.frombuffer(raw,np.uint8).reshape(h,w,3).copy())
assert dec.wait()==0
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in frames];dense={}
for a,b in zip(d['keyframes'],d['keyframes'][1:]):
    ia=round((a['t']-start)*fps);ib=min(len(frames)-1,round((b['t']-start)*fps))
    if d.get('trackingMethod','').startswith('manual'):
        for i in range(ia,ib+1):
            t=start+i/fps;u=(t-a['t'])/(b['t']-a['t'])
            points=np.array([a['left'],a['right']])*(1-u)+np.array([b['left'],b['right']])*u
            dense[i]={'sourceTime':t,'points':points.tolist(),'disagreementPixels':None,'hidden':False,'method':'manual-quarter-second-interpolation-not-yet-pixel-approved'}
        continue
    def track(seed,indices):
        points=np.array(seed,np.float32).reshape(-1,1,2);result={indices[0]:(points[:,0].copy(),True)}
        for prev,i in zip(indices,indices[1:]):
            points,ok,err=cv2.calcOpticalFlowPyrLK(gray[prev],gray[i],points,None,winSize=(21,21),maxLevel=3)
            result[i]=(points[:,0].copy(),bool(ok.all()))
        return result
    forward=track([a['left'],a['right']],list(range(ia,ib+1)))
    backward=track([b['left'],b['right']],list(range(ib,ia-1,-1)))
    for i in range(ia,ib+1):
        u=(i-ia)/max(1,ib-ia);f,fok=forward[i];r,rok=backward[i]
        disagreement=float(np.linalg.norm(f-r,axis=1).max());points=f*(1-u)+r*u
        dense[i]={'sourceTime':start+i/fps,'points':points.tolist(),'disagreementPixels':disagreement,'hidden':not(fok and rok) or disagreement>16}
out=O/'source-review/wing-annotation-preview.mp4';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',13)
enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2',str(out)],stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
sheet=Image.new('RGB',(1600,3*245),'white');sd=ImageDraw.Draw(sheet);samples=np.linspace(0,len(frames)-1,12,dtype=int).tolist()
for i,frame in enumerate(frames):
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));draw=ImageDraw.Draw(im);t=i/fps;r=dense[i];left,right=np.array(r['points']);center=(left+right)/2;colors=d['colors']
    if not r['hidden']:
        if t>=d['reveal']['midpoint']:draw.ellipse((*tuple(center-4),*tuple(center+4)),fill=colors['midpoint'])
        if t>=d['reveal']['wingVector']:
            draw.line([tuple(left),tuple(right)],fill=colors['wingVector'],width=4)
            vec=(right-left)/np.linalg.norm(right-left);perp=np.array([-vec[1],vec[0]])
            draw.polygon([tuple(right),tuple(right-12*vec+5*perp),tuple(right-12*vec-5*perp)],fill=colors['wingVector'])
            draw.text((center[0]-60,min(left[1],right[1])-30),'날개 방향',font=font,fill=colors['wingVector'],stroke_width=1,stroke_fill='black')
        if t>=d['reveal']['screenReference']:
            for x in range(-110,110,12):draw.line([tuple(center+[x,0]),tuple(center+[x+6,0])],fill=colors['screenReference'],width=3)
        if t>=d['reveal']['projectedAngle']:
            theta=math.atan2((right-left)[1],(right-left)[0]);arc=[tuple(center+35*np.array([math.cos(theta*j/20),math.sin(theta*j/20)])) for j in range(21)]
            draw.line(arc,fill=colors['projectedAngle'],width=3)
    draw.rectangle((190,55,650,82),fill='#171717');draw.text((199,61),'화면에 투영된 날개 방향 · 카메라도 이동하고 기울어짐',font=small,fill='white')
    enc.stdin.write(np.asarray(im).tobytes())
    if i in samples:
        k=samples.index(i);x=k%4*400;y=k//4*245;sheet.paste(im.resize((400,225)),(x,y));sd.text((x+5,y+228),f'{r["sourceTime"]:.2f}s / hidden={r["hidden"]} / method={"manual" if r["disagreementPixels"] is None else "optical-flow"}',fill='black')
enc.stdin.close();assert enc.wait()==0
sheet.save(O/'source-review/wing-annotation-moving-pixels.jpg')
report={'frames':len(frames),'hiddenFrames':sum(r['hidden'] for r in dense.values()),'tracking':list(dense.values()),'narrationTimed':False,'motionPixelApproval':False,'screenSpaceOnly':True}
(O/'wing-tracking-dense.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='tracking'}))
