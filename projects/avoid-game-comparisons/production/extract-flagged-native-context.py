"""Inspect only newly flagged raw boundaries; no downloads or final rendering."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=BASE/'measured-edit-v3/flagged-native-context-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
assert not DEST.exists();DEST.mkdir()
requests=[('mine-dissolve','CJ0_Xh59b98',sorted(set(list(range(1220,1260,5))+list(range(1260,1276))))),
          ('mine-entry-transition','CJ0_Xh59b98',sorted(set(list(range(8990,9188,16))+[9187,9188]))),
          ('rocket-word-boundary','h27ZF-hKKYM',list(range(9690,9990,20))+[9989]),
          ('drill-dialogue','o3Fomp9HdHs',list(range(720,786,8))+[785])]
sr=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research'
assets={}
for fn in ['acquisition-plucky-mine.json','acquisition-rocket-ride.json','acquisition-pepper-drill.json']:
 for result in read(sr/fn)['results']:assets[result['videoId']]=result
state={'startedAt':now(),'pid':os.getpid(),'status':'CPU-new-flagged-native-context-only','images':[],'sheets':[],'activeTasks':[],'newGitImages':0}
def save():
 (DEST/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
 item=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
 item['stage']='current15-flagged-cue-reframing-and-native-boundary-repair'
 item['execution'].update(observedAt=now(),phase=item['stage'],pid=state['pid'],sessionId=None,
  alive='endedAt' not in state,status=state['status'],activeTasks=state['activeTasks'],gpuSynthesisJobs=0,
  cpuProductionJobs=0 if 'endedAt' in state else 1,renderJobs=0,uploads=0)
 item['nextAction']='Resolve the directly observed cue occlusions and exact source transitions; preserve all current15 PCM. Final timing/caption/mix approval remains false.'
 q['updatedAt']=now();item['updatedAt']=q['updatedAt']
 qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for label,source,frames in requests:
 asset=assets[source];assert sha(ROOT/asset['localMediaPath'])==asset['fileSha256']
 folder=DEST/label;folder.mkdir()
 selection='+'.join(f'eq(n\\,{f})' for f in frames)
 cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-nostdin','-threads','2','-i',str(ROOT/asset['localMediaPath']),
      '-vf',f"select='{selection}'",'-fps_mode','passthrough','-frames:v',str(len(frames)),str(folder/'raw-%03d.png')]
 log=folder/'extraction.log'
 with log.open('wb') as fh:
  proc=subprocess.Popen(cmd,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeTasks']=[{'kind':'CPU-flagged-native-review','pid':proc.pid,'command':cmd,'log':rel(log)}];save()
  code=proc.wait()
 assert code==0 and not log.read_text().strip()
 for p,n in zip(sorted(folder.glob('raw-*.png')),frames):
  state['images'].append({'path':rel(p),'sha256':sha(p),'source':source,'sourceSha256':asset['fileSha256'],'nativeFrame':n,'request':label,'directlyRead':False})
 state['activeTasks']=[];save()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
for offset in range(0,len(state['images']),6):
 subset=state['images'][offset:offset+6];sheet=Image.new('RGB',(1920,1740),'white');d=ImageDraw.Draw(sheet)
 for k,rec in enumerate(subset):
  x,y=k%2*960,k//2*580
  with Image.open(ROOT/rec['path']) as im:sheet.paste(im.resize((960,540)),(x,y+40))
  d.text((x+8,y+7),f"{offset+k+1:03d} {rec['request']} raw n{rec['nativeFrame']}",fill='black',font=font)
 p=DEST/f"review-sheet-{offset//6+1:03d}.jpg";sheet.save(p,quality=94)
 state['sheets'].append({'path':rel(p),'sha256':sha(p),'imageIndices':list(range(offset+1,offset+len(subset)+1)),'directlyRead':False})
state.update(status='closed-new-flagged-native-context-awaiting-direct-read',endedAt=now(),exitCode=0);save()
print(json.dumps({'pid':state['pid'],'images':len(state['images']),'sheets':len(state['sheets']),'exitCode':0}))
