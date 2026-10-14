"""Correct observed screen anchors, preserve held history, prepare two-piece CPU renderer."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stamp=datetime.now(timezone.utc).isoformat()
ep=R/'held-role-anchors-execution-v2.json';e=read(ep);assert e['exitCode']==0 and not psutil.pid_exists(e['pid'])
e.update(actualOuterExitCode=0,actualSession=37657,actualCompletion='1d897a',actualWorkerAbsent=True);ep.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
anchors=read(R/'remaining-action-annotation-anchors-v1.json');fresh={(w['sourceKey'],r['nativeFrame']):r for w in e['windows'] for r in w['samples']}
files=[]
for w in e['windows']:
 for row in w['samples']+w['boards']:assert sha(ROOT/row['path'])==row['sha256'];files.append(dict(path=row['path'],sha256=row['sha256']))
def corrected(tr,points):
 old={r['nativeFrame']:r for r in tr['rows']};result=[]
 for n,xy in points:
  row=dict(fresh.get((tr['sourceKey'],n),old.get(n)));assert sha(ROOT/row['path'])==row['sha256']
  row.update(nativeFrame=n,screenPoint1280=xy);result.append(row)
 tr['rows']=result
laser=next(t for t in anchors['tracks'] if t['id']=='portal-target-status')
corrected(laser,[(2352,[851,148]),(2368,[862,148]),(2383,[856,148]),(2398,[722,214]),(2413,[633,241]),(2428,[633,246])]);laser['rangeEndExclusive']=2428
laser['rule']='Point at visible lower blue-X/yellow-check endpoint on wall, not floor. Six native anchors. Hide after2428. Encoded dense samples and normal-speed review required.'
board=next(t for t in anchors['tracks'] if t['id']=='alyx-board-object')
corrected(board,[(3357,[900,550]),(3387,[900,565]),(3417,[900,650]),(3477,[900,630]),(3507,[900,525]),(3537,[900,550])]);board['segments']=[dict(start=3357,endExclusive=3418),dict(start=3477,endExclusive=3537)]
board['rule']='Observed lower foreground plank. Hide3418..3476 while this plank exits lower frame; no interpolation through uncertain viewpoint. Same plank reappears3477..3536. No background target or engine-space claim.'
anchors.update(preparedAt=stamp,previous='remaining-action-annotation-anchors-v1.json',newExactNativeSamplesDirectlyRead=6,newBoardsDirectlyRead=2,newSamplesShaBound=files,allIntermediateTrackingApproved=False,narrationTimedPixelApproval=False)
ap=R/'remaining-action-annotation-anchors-v2.json';assert not ap.exists();ap.write_text(json.dumps(anchors,ensure_ascii=False,indent=2)+'\n','utf-8')
text=(B/'render-motion-remaining-action-roles-v1.py').read_text('utf-8')
text=text.replace('eight unrendered source windows','two held source windows').replace('remaining-action-roles-v1','remaining-action-roles-v2').replace('remaining-action-annotation-anchors-v1.json','remaining-action-annotation-anchors-v2.json')
text=text.replace('remaining-action-roles-execution-v1.json','remaining-action-roles-execution-v2.json').replace('remaining-action-roles-current-cim-v1.json','remaining-action-roles-current-cim-v2.json')
text=text.replace("assert len(pieces)==8 and sum(p['frames'] for p in pieces)==4915","pieces=[p for p in pieces if p['id'] in ['07b-laser-target','08b-board-removal']]\nassert len(pieces)==2 and sum(p['frames'] for p in pieces)==1619")
text=text.replace("rows=tr['rows']\n if n<", "rows=tr['rows']\n if 'segments' in tr and not any(s['start']<=n<s['endExclusive'] for s in tr['segments']):return None\n if n<")
text=text.replace("selected.update(range(0,count,60))","selected.update(range(0,count,60))\n  # Dense quarter-second sampling through both repaired marker windows.\n  if piece['id']=='07b-laser-target':selected.update(range(509,662,15))\n  if piece['id']=='08b-board-removal':selected.update(range(120,302,15))")
text=text.replace("for threshold in [1159,2352,1932,3365,3063,3069,2948]:","for threshold in [1159,2352,1932,3365,3418,3477,3537,3063,3069,2948]:")
text=text.replace("frames=4915,samples=", "frames=1619,samples=")
text=text.replace('Reuse actual remaining-eight-action-role worker.', 'Reuse actual narrow two-piece role repair worker; other six completed pieces stay unchanged.')
path=B/'render-motion-remaining-action-roles-v2.py';assert not path.exists();path.write_text(text,'utf-8');compile(text,str(path),'exec')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(recordedAt=stamp,activeOwnedWorkers=0,ownedJob=dict(active=False,status='six-new-native-anchors-read',sessionId=37657,exitCode=0,completion='1d897a'),correctedRoleAnchors=ap.name,next='Run prepared single CPU2 two-piece repair after fresh resources, preserve all six other source pieces and completed voice/ASR/explanation work. No final adoption until dense encoded points and normal1x checked.');cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(newSamplesRead=6,newBoardsRead=2,correctedTracks=2,rendererPrepared=True,rendererExecuted=False)))
