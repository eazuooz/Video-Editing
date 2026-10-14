"""Check actual encoded caption pixels at every cue and boundary, plus cuts.

Opaque artwork is compared with the exact CaptionBox PNG, never OCR guesses.
Blank intervals are compared with the retained clean master. Agent visual/motion
review remains a separate, explicitly scoped ledger entry.
"""
from pathlib import Path
import json, subprocess, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG;QA=OUT/'caption-pixel-qa';QA.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/f'projects/{SLUG}/project.json');layout=read(OUT/'caption-overlays/layout.json')
data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
cues=layout['layout'];total=layout['totalFrames'];frames=set([0,119,120,total-601,total-600,total-1])
for c in cues:
 frames.add((c['startFrame']+c['endFrame']-1)//2)
 for edge in [c['startFrame'],c['endFrame']]:frames.update([edge-1,edge,edge+1])
for s in data['scenes']:
 cut=120+round(s['start']*60);frames.update([cut-1,cut,cut+1])
frames=sorted(f for f in frames if 0<=f<total)
def active(f):return next((c for c in cues if c['startFrame']<=f<c['endFrame']),None)
blanks=[f for f in frames if active(f) is None]
def extract(key,indices):
 path=ROOT/m['paths'][key];dest=QA/key;dest.mkdir(exist_ok=True)
 receipt=dest/'input.json';stamp={'sourceSha256':sha(path),'frames':indices,'crop':[0,870,1920,210]}
 if receipt.exists() and read(receipt)==stamp and len(list(dest.glob('*.png')))==len(indices):return dest
 assert not list(dest.glob('*.png')),'Changed extraction must use an explicit new QA version'
 vf=dest/'filter.txt';vf.write_text("select='"+'+'.join(f'eq(n,{f})' for f in indices)+"',crop=1920:210:0:870",encoding='ascii')
 subprocess.run(['ffmpeg','-v','error','-i',str(path),'-filter_script:v',str(vf),'-fps_mode','vfr','-compression_level','2',str(dest/'%06d.png')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 assert len(list(dest.glob('*.png')))==len(indices)
 receipt.write_text(json.dumps(stamp,indent=2)+'\n',encoding='utf-8');return dest
encoded=extract('videoBurnedCaptions',frames);clean=extract('videoClean',blanks)
blankmap={f:clean/f'{i+1:06}.png' for i,f in enumerate(blanks)};cache={};records=[];fail=[]
for i,f in enumerate(frames):
 actual=np.array(Image.open(encoded/f'{i+1:06}.png').convert('RGB'),dtype=np.int16)
 cue=active(f)
 if cue:
  cid=cue['cue']
  if cid not in cache:cache[cid]=np.array(Image.open(OUT/'caption-overlays'/f'cue-{cid:04}.png').convert('RGBA'))[:210]
  art=cache[cid];mask=art[:,:,3]==255
  delta=np.abs(actual-art[:,:,:3].astype(np.int16))[mask]
 else:
  reference=np.array(Image.open(blankmap[f]).convert('RGB'),dtype=np.int16);delta=np.abs(actual-reference).reshape(-1,3)
 mean=float(delta.mean());p95=float(np.percentile(delta,95));ok=mean<6 and p95<25
 row={'frame':f,'seconds':f/60,'cue':cue['cue'] if cue else None,'meanAbsoluteRgbError':mean,'p95RgbError':p95,'status':'pass' if ok else 'fail'}
 records.append(row)
 if not ok:fail.append(row)
result={'status':'pass' if not fail else 'fail','method':'decoded1920px caption strips; exact canvas artwork; clean control for no-caption intervals',
 'captionedSha256':sha(ROOT/m['paths']['videoBurnedCaptions']),'cleanSha256':sha(ROOT/m['paths']['videoClean']),
 'cues':len(cues),'sampledFrames':len(frames),'everyCueMidpoint':True,'everyCueStartEndNeighbors':True,'everySceneCutNeighbors':True,
 'comparisonThreshold':{'meanAbsoluteRgbErrorLessThan':6,'p95LessThan':25},'failures':fail,'frames':records,
 'agentVisualAndMovementReview':'separate scoped review required'}
(QA/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'cues':len(cues),'frames':len(frames),'failures':len(fail)}))
assert not fail,'Review failed actual frames; do not raise thresholds blindly'
