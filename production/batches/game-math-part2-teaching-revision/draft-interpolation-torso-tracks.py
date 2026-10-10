"""CPU-only visible-torso drafts at exact native source frames.

Draft confidence is not approval. Board/wings/car landmarks are authored
separately, and every final moving overlay needs direct pixel review.
"""
from pathlib import Path
import os,sys,json,math,hashlib,subprocess,argparse
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision';D=B/'interpolation-tracks';D.mkdir(exist_ok=True)
sys.path.insert(0,str(O/'cpu-pose-packages'));os.environ['YOLO_CONFIG_DIR']=str(O/'cpu-pose-config')
import numpy as np,torch
torch.set_num_threads(2)
from ultralytics import YOLO
model_path=O/'cpu-pose-model/yolo26n-pose.pt';model=YOLO(str(model_path))
read=lambda p:json.loads(p.read_text(encoding='utf8'))
games=read(B/'interpolation-game-insertions.json')['scenes']
parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args()
selected=set(args.only.split(',')) if args.only else None
records=[]
for row in games:
    ident=row['id']
    if selected and ident not in selected:continue
    source=ROOT/'shared/output/game-math-part2-teaching-revision/sources'/f"{row['sourceId']}.mp4"
    data=read(Path(str(source)+'.probe.json')) if Path(str(source)+'.probe.json').exists() else json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','json',str(source)]))
    n,d=map(int,data['streams'][0]['r_frame_rate'].split('/'));fps=n/d;stride=max(1,round(fps/10))
    for segment,(a,b) in enumerate(row['intervals']):
        target=D/f'{ident.lower()}-{segment+1}-torso.json'
        first=math.ceil(a*fps-1e-7);last=math.floor(b*fps-1e-7);count=(last-first)//stride+1
        cmd=['ffmpeg','-v','error','-threads','1','-ss',str(first/fps),'-i',str(source),'-t',str((last-first+stride)/fps),'-vf',f'scale=800:450,select=not(mod(n\\,{stride}))','-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        points=[];hidden=[];index=0
        while index<count:
            frames=[];times=[]
            for _ in range(min(8,count-index)):
                raw=proc.stdout.read(800*450*3);assert len(raw)==800*450*3
                times.append((first+index*stride)/fps);index+=1
                frames.append(np.frombuffer(raw,np.uint8).reshape(450,800,3)[:,:,::-1].copy())
            predictions=model.predict(frames,device='cpu',imgsz=640,conf=.45,verbose=False)
            for t,r in zip(times,predictions):
                candidates=[]
                for bbox,confidence,key in zip(r.boxes.xyxy.tolist(),r.boxes.conf.tolist(),r.keypoints.data.tolist()):
                    joint=min(key[i][2] for i in (5,6,11,12))
                    if joint<.45:continue
                    upper=np.mean([key[i][:2] for i in (5,6)],axis=0);lower=np.mean([key[i][:2] for i in (11,12)],axis=0)
                    center=(upper+lower)/2;distance=float(np.linalg.norm(center-[400,240]));length=float(np.linalg.norm(upper-lower))
                    if distance>180 or not 10<=length<=165:continue
                    candidates.append((distance-15*confidence,upper,lower,confidence,joint))
                if not candidates:hidden.append([t-.001,t+stride/fps+.001]);continue
                _,upper,lower,confidence,joint=min(candidates,key=lambda c:c[0])
                points.append({'t':round(t,9),'upper':upper.round(3).tolist(),'lower':lower.round(3).tolist(),'detectorConfidence':round(confidence,4),'jointConfidence':round(joint,4)})
        proc.stdout.read();assert proc.wait()==0
        for x,y in zip(points,points[1:]):
            if y['t']-x['t']>stride/fps+.005:hidden.append([x['t']+.001,y['t']-.001])
        merged=[]
        for x,y in sorted(hidden):
            if merged and x<=merged[-1][1]+.002:merged[-1][1]=max(merged[-1][1],y)
            else:merged.append([x,y])
        result={'id':ident,'segment':segment+1,'sourceId':row['sourceId'],'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'coordinatePixels':[800,450],'nativeFps':data['streams'][0]['r_frame_rate'],'nativeFirstFrame':first,'nativeStride':stride,'interval':[a,b],'keyframes':points,'hideIntervals':merged,'trackingMethod':'CPU YOLO26n-pose visible shoulders/hips at exact native frame indices; low-confidence spans hidden; draft only','meaning':'projected visible torso; no calibrated game-world/engine rotation','modelSha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'device':'cpu','movingPixelApproval':False}
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        records.append({'scene':ident,'segment':segment+1,'samples':count,'valid':len(points),'path':target.relative_to(ROOT).as_posix(),'movingPixelApproval':False})
        print(ident,segment+1,len(points),'/',count,flush=True)
(B/'interpolation-torso-draft-report.json').write_text(json.dumps({'records':records,'device':'cpu','pixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
