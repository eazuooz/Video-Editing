"""CPU-only dense pose draft; preserve manual tracks and every approval gate.

Observed image-space shoulders/hips are an approximate projected torso line,
not reconstructed game-world axes. Confidence/occlusion failures are hidden.
Actual moving render review is still required after this diagnostic refinement.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,math,copy
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='4'
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision'
config=O/'cpu-pose-config';config.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(O/'cpu-pose-packages'));os.environ['YOLO_CONFIG_DIR']=str(config)
import torch,numpy as np
torch.set_num_threads(4)
from ultralytics import YOLO
sys.path.insert(0,str(B));from importlib.machinery import SourceFileLoader
overlay=SourceFileLoader('pose_overlay',str(B/'create-game-overlay.py')).load_module()
model_path=O/'cpu-pose-model/yolo26n-pose.pt';model=YOLO(str(model_path))
registry=json.loads((B/'quaternion-annotation-tracks.json').read_text(encoding='utf8'))
D=B/'dense-body-tracks';D.mkdir(exist_ok=True)
manual_paths=sorted({p for s in registry['scenes'].values() for p in s.get('landmarkSources',[s.get('landmarks')]) if p and 'dense-body-tracks' not in p})
replacements={};results=[]
for rel in manual_paths:
 path=ROOT/rel;draft=json.loads(path.read_text(encoding='utf8'))
 if 'upper' not in draft['keyframes'][0]:continue
 target=D/path.name;source_sha=hashlib.sha256(path.read_bytes()).hexdigest()
 if target.exists():
  saved=json.loads(target.read_text(encoding='utf8'))
  if saved.get('manualDraftSha256')==source_sha and len(saved['keyframes'])>=2:
   replacements[rel]=target.relative_to(ROOT).as_posix();print('Retained dense CPU draft',path.name,flush=True);continue
 # Exactly selected native frames, never fps bins or label-time assumptions.
 first=math.ceil(draft['keyframes'][0]['t']*60-1e-6);last=math.floor(draft['keyframes'][-1]['t']*60+1e-6)
 count=(last-first)//6+1;start=first/60
 command=['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(ROOT/draft['sourceFile']),'-t',str((last-first+7)/60),'-vf','scale=800:450,select=not(mod(n\\,6))','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 decoder=subprocess.Popen(command,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 points=[];hidden=[];read_count=0
 while read_count<count:
  imgs=[];times=[];hints=[]
  for _ in range(min(8,count-read_count)):
   raw=decoder.stdout.read(800*450*3);assert len(raw)==800*450*3
   time=start+read_count*.1;read_count+=1;hint=overlay.at_points(draft,time)
   if hint is None:hidden.append([time-.001,time+.101]);continue
   imgs.append(np.frombuffer(raw,np.uint8).reshape(450,800,3)[:,:,::-1].copy());times.append(time);hints.append(hint)
  if not imgs:continue
  predictions=model.predict(imgs,device='cpu',imgsz=640,conf=.45,verbose=False)
  for time,hint,r in zip(times,hints,predictions):
   expected=(hint['upper']+hint['lower'])/2;candidates=[]
   for bbox,confidence,key in zip(r.boxes.xyxy.tolist(),r.boxes.conf.tolist(),r.keypoints.data.tolist()):
    if min(key[i][2] for i in (5,6,11,12))<.45:continue
    upper=np.mean([key[i][:2] for i in (5,6)],axis=0);lower=np.mean([key[i][:2] for i in (11,12)],axis=0);center=(upper+lower)/2
    distance=float(np.linalg.norm(center-expected));length=float(np.linalg.norm(upper-lower))
    if distance>105 or not 12<=length<=170:continue
    candidates.append((distance-10*confidence,upper,lower,confidence,min(key[i][2] for i in (5,6,11,12))))
   if not candidates:hidden.append([time-.001,time+.101]);continue
   _,upper,lower,confidence,joint=min(candidates,key=lambda c:c[0])
   p={'t':round(time,9),'upper':upper.round(3).tolist(),'lower':lower.round(3).tolist(),'detectorConfidence':round(confidence,4),'jointConfidence':round(joint,4)}
   if 'wheel' in hint:p['wheel']=hint['wheel'].round(3).tolist()
   points.append(p)
 decoder.stdout.read();assert decoder.wait()==0
 if len(points)<2:
  results.append({'manual':rel,'validPoints':len(points),'replacementApplied':False});continue
 # Do not interpolate over an unobserved/confidence-rejected sample.
 for a,b in zip(points,points[1:]):
  if b['t']-a['t']>.105:hidden.append([a['t']+.001,b['t']-.001])
 combined=[]
 for a,b in sorted(hidden+draft.get('hideIntervals',[])):
  if combined and a<=combined[-1][1]+.002:combined[-1][1]=max(combined[-1][1],b)
  else:combined.append([a,b])
 dense={**draft,'keyframes':points,'hideIntervals':combined,'manualDraft':rel,'manualDraftSha256':source_sha,
  'trackingMethod':'CPU YOLO26n-pose shoulders/hips10fps at exact native frames; confidence/occlusion failures hidden; visible wheel draft remains separately observed',
  'modelSource':'https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n-pose.pt','modelSha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
  'meaning':'Estimated projected visible torso landmarks only; no calibrated game-world orientation or engine values',
  'device':'cpu','nativeStepSeconds':.1,'movingPixelApproval':False}
 target.write_text(json.dumps(dense,ensure_ascii=False,indent=2)+'\n',encoding='utf8');replacements[rel]=target.relative_to(ROOT).as_posix()
 results.append({'manual':rel,'dense':target.relative_to(ROOT).as_posix(),'nativeSamples':count,'validPoints':len(points),'hiddenIntervals':len(combined),'replacementApplied':True,'movingReviewPassed':False})
 print('CPU dense draft',path.name,len(points),'/',count,flush=True)
archive=B/'baselines/landmark-drafts-before-native-time-fix/registry-before-dense-cpu-refinement.json'
if not archive.exists():archive.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for ident,spec in registry['scenes'].items():
 if spec.get('landmarks') in replacements:spec['landmarks']=replacements[spec['landmarks']]
 if spec.get('landmarkSources'):spec['landmarkSources']=[replacements.get(x,x) for x in spec['landmarkSources']]
 spec['movingPixelApproval']=False;spec['labelOutline']=3.5
registry['all25ActualScenesReady']=False
(B/'quaternion-annotation-tracks.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(B/'quaternion-cpu-dense-refinement.json').write_text(json.dumps({'method':'CPU-only diagnostic refinement; manual sources preserved','records':results,'movingReviewPassed':False,'researchGpuUntouched':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Dense CPU drafts prepared; render and actual native moving review remain pending.',flush=True)
