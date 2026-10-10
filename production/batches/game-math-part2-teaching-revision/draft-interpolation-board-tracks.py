"""Independent CPU mask drafts for the visible long axis of a skateboard.

Confidence/shape failures are hidden. PCA is only a projected mask direction;
moving render review decides whether each observed span may actually be used.
"""
from pathlib import Path
import os,sys,json,math,hashlib,subprocess,argparse,urllib.request
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision';D=B/'interpolation-tracks';D.mkdir(exist_ok=True)
sys.path.insert(0,str(O/'cpu-pose-packages'));os.environ['YOLO_CONFIG_DIR']=str(O/'cpu-pose-config')
import numpy as np,torch
torch.set_num_threads(2)
from ultralytics import YOLO
model_path=O/'cpu-pose-model/yolo26s-seg.pt'
if not model_path.exists():
    release=json.load(urllib.request.urlopen('https://api.github.com/repos/ultralytics/assets/releases/tags/v8.4.0'))
    asset=next(x for x in release['assets'] if x['name']=='yolo26s-seg.pt')
    assert asset['browser_download_url'].startswith('https://github.com/ultralytics/assets/releases/download/v8.4.0/')
    urllib.request.urlretrieve(asset['browser_download_url'],model_path)
    assert model_path.stat().st_size==asset['size']
model=YOLO(str(model_path));board_class=next(k for k,v in model.names.items() if v=='skateboard')
read=lambda p:json.loads(p.read_text(encoding='utf8'))
games=read(B/'interpolation-game-insertions.json')['scenes']
parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args()
selected=set(args.only.split(',')) if args.only else None
records=[]
for row in games:
    ident=row['id']
    if selected and ident not in selected:continue
    source=ROOT/f"shared/output/game-math-part2-teaching-revision/sources/{row['sourceId']}.mp4"
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','json',str(source)]))
    n,d=map(int,info['streams'][0]['r_frame_rate'].split('/'));fps=n/d;stride=round(fps/10)
    for segment,(a,b) in enumerate(row['intervals']):
        target=D/f'{ident.lower()}-{segment+1}-board.json'
        first=math.ceil(a*fps-1e-7);last=math.floor(b*fps-1e-7);count=(last-first)//stride+1
        cmd=['ffmpeg','-v','error','-threads','1','-ss',str(first/fps),'-i',str(source),'-t',str((last-first+stride)/fps),'-vf',f'scale=800:450,select=not(mod(n\\,{stride}))','-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW);points=[];hidden=[];index=0
        while index<count:
            frames=[];times=[]
            for _ in range(min(8,count-index)):
                raw=proc.stdout.read(800*450*3);assert len(raw)==800*450*3
                times.append((first+index*stride)/fps);index+=1
                frames.append(np.frombuffer(raw,np.uint8).reshape(450,800,3)[:,:,::-1].copy())
            predictions=model.predict(frames,device='cpu',imgsz=640,classes=[board_class],conf=.30,verbose=False)
            for t,r in zip(times,predictions):
                candidates=[]
                for poly,confidence in zip(r.masks.xy if r.masks is not None else [],r.boxes.conf.tolist()):
                    poly=np.asarray(poly);center=np.mean(poly,axis=0)
                    if len(poly)<8 or not 230<=center[0]<=580 or not 160<=center[1]<=410:continue
                    eig,vectors=np.linalg.eigh(np.cov((poly-center).T));axis=vectors[:,np.argmax(eig)]
                    elongation=float(np.sqrt(max(eig)/max(min(eig),1e-6)))
                    projected=(poly-center)@axis;lo,hi=np.percentile(projected,[5,95]);length=hi-lo
                    if not 12<=length<=110 or elongation<1.45:continue
                    ends=np.array([center+lo*axis,center+hi*axis])
                    candidates.append((float(np.linalg.norm(center-[400,310]))-10*confidence,ends,confidence,elongation))
                if not candidates:hidden.append([t-.001,t+stride/fps+.001]);continue
                _,ends,confidence,elongation=min(candidates,key=lambda x:x[0])
                points.append({'t':round(t,9),'wheel':ends.round(3).tolist(),'detectorConfidence':round(confidence,4),'maskElongation':round(elongation,4)})
        proc.stdout.read();assert proc.wait()==0
        for x,y in zip(points,points[1:]):
            if y['t']-x['t']>stride/fps+.005:hidden.append([x['t']+.001,y['t']-.001])
        merged=[]
        for x,y in sorted(hidden):
            if merged and x<=merged[-1][1]+.002:merged[-1][1]=max(merged[-1][1],y)
            else:merged.append([x,y])
        record={'id':ident,'segment':segment+1,'sourceId':row['sourceId'],'sourceFile':source.relative_to(ROOT).as_posix(),'coordinatePixels':[800,450],'nativeFps':info['streams'][0]['r_frame_rate'],'nativeFirstFrame':first,'nativeStride':stride,'interval':[a,b],'keyframes':points,'hideIntervals':merged,'trackingMethod':'CPU YOLO26s-seg skateboard mask PCA; independent observed image direction; low-confidence/nonelongated spans hidden; draft only','meaning':'visible projected board length axis only; no calibrated world angle or game-engine values','modelSource':'https://github.com/ultralytics/assets/releases/tag/v8.4.0','modelSha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'device':'cpu','movingPixelApproval':False}
        target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        records.append({'scene':ident,'segment':segment+1,'samples':count,'valid':len(points),'path':target.relative_to(ROOT).as_posix(),'movingPixelApproval':False});print(ident,segment+1,len(points),'/',count,flush=True)
(B/'interpolation-board-draft-report.json').write_text(json.dumps({'records':records,'device':'cpu','pixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
