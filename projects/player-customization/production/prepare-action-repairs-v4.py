"""Preserve the measured narration timeline; change only five pixel mismatches."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
s=read(BASE/'action-repair-candidate-execution-v2.json')
assert s['exitCode']==0 and len(s['boards'])==8 and len(s['samples'])==47
for e in [*s['boards'],*s['samples']]:assert sha(ROOT/e['path'])==e['sha256']
notes=[
 {'window':1,'observation':'24–24.75 clear full caster rushing along orange riverbank with blue trajectory;25–26.183 low closeup shows moving legs and track, no nearby reaction proof. Select only24–25.1 for movement opening, not an enemy-effect claim.'},
 {'window':2,'observation':'391–392.25 blue forward rush over ground with moving caster and trace;392.5–392.983 visible humanoid ahead/right and slowing approach. Select391–393 for movement phrase; later existing shots separately show foe reaction.'},
 {'window':3,'observation':'72.8 caster passes close foe with orbiting blades;73.05 side movement,73.3–74.55 caster/orbit and two forward foes visibly change relative position;74.8 target shot and75.05+ large burst. Select72.8–74.75; exclude burst tail.'},
 {'window':4,'observation':'153.9–154.9 caster ring while turning around fountain/stairs, nearby foes intermittently at edges;155.15–155.65 close humanoid beside/behind caster;155.9–157.483 caster turns away and another foe appears beyond fountain. Select154.3167–157.2667 for center/nearby-position sentence; no damage, reach number or superiority claim.'}
]
r=dict(schemaVersion=1,slug='player-customization',reviewedAt=now,execution='projects/player-customization/production/action-repair-candidate-execution-v2.json',all8BoardsDirectlyRead=True,all47NativeSamplesDirectlyRead=True,hashVerifiedFiles=55,hashMismatches=0,boards=s['boards'],samples=s['samples'],notes=notes,sourceAllocationApproved=False,allFinalPixels=False,imagesLocalOnly=True,newGitImages=0)
rp=BASE/'action-repair-candidate-direct-review-v2.json';assert not rp.exists();rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
oldpath=ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v3.json'
p=read(oldpath);old=copy.deepcopy(p);sources={s['key']:s for s in p['sources']}
pts={k:read(ROOT/v['ptsPath'])['frames'] for k,v in sources.items()}
def piece(c,key,start,n,action):
 x=copy.deepcopy(c);src=sources[key]
 x.update(sourceKey=key,sourcePath=src['path'],sourceSha256=src['sha256'],sourceInFrame=start,sourceOutFrame=start+n,frames=n,
  cropCandidate=src['cropCandidate'],firstNativePts=int(pts[key][start]['best_effort_timestamp']),lastNativePts=int(pts[key][start+n-1]['best_effort_timestamp']),firstNativeSeconds=float(pts[key][start]['best_effort_timestamp_time']),
  originalSourceInSeconds=float(pts[key][start]['best_effort_timestamp_time'])+src.get('originalOffsetSeconds',src.get('sourceOffsetSeconds',0)),visibleAction=action,sourceActionAligned=False,continuousSelectedPixelsReviewed=False,fixedCaptionPixelsReviewed=False,repairNativeOnly=True)
 return x
cuts=[];changes=[]
for idx,c in enumerate(old['cuts'],1):
 c['baselineCutIndex']=idx
 if c['scene']=='09-path-and-projectile-guide' and c['paragraph']==1 and c['sourceKey']=='gauss129' and c['sourceInFrame']==24186:
  out=[piece(c,'gauss',1440,66,'Visible caster rush with blue trail along riverbank'),piece(c,'gauss129',23460,120,'Forward blue rush with caster and subsequent nearby foe ahead')]
 elif c['scene']=='09-path-and-projectile-guide' and c['paragraph']==4 and c['sourceKey']=='yareli155':
  out=[piece(c,'yareli155',8706,325,c['visibleAction'])]
 elif c['scene']=='09-path-and-projectile-guide' and c['paragraph']==4 and c['sourceKey']=='dante' and c['sourceInFrame']==3324:
  out=[piece(c,'dante',3334,86,c['visibleAction'])]
 elif c['scene']=='04-situations' and c['paragraph']==1 and c['sourceKey']=='gauss129':
  out=[piece(c,'gauss129',720,97,c['visibleAction'])]
 elif c['scene']=='04-situations' and c['paragraph']==1 and c['sourceKey']=='yareli' and c['sourceInFrame']==3900:
  out=[piece(c,'yareli',3877,113,'Caster-centered Aquablades surround caster, preserved endpoint66.5')]
 elif c['scene']=='04-situations' and c['paragraph']==2 and c['sourceInFrame']==2880:
  out=[piece(c,'yareli',4368,117,'Aquablades caster passes near foes, turns with visible caster and target position')]
 elif c['scene']=='12-nearby-space-guide' and c['paragraph']==1:
  # ASS cue172 begins245.88s; first video tick245.8833 receives this cue.
  # Replace its center/nearby sentence through248.8333 with a fresh native sequence.
  first=14753-c['outputStartFrame'];mid=178;last=c['frames']-first-mid
  out=[piece(c,'jadeYareli',31440,first,c['visibleAction']),piece(c,'yareli155',9259,mid,'Caster-centered ring and nearby humanoid; caster turns and changes relation to next target'),piece(c,'jadeYareli',31440+first+mid,last,c['visibleAction'])]
 else:out=[c]
 if len(out)!=1 or out[0].get('repairNativeOnly'):
  changes.append(dict(baselineCutIndex=idx,scene=c['scene'],paragraph=c['paragraph'],oldSource=c.get('sourceKey'),oldIn=c['sourceInFrame'],oldFrames=c['frames'],new=[dict(source=x.get('sourceKey'),sourceInFrame=x['sourceInFrame'],frames=x['frames']) for x in out]))
 cuts.extend(out)
pos=120;local={}
for c in cuts:
 start=local.get(c['scene'],0);c.update(sceneLocalStartFrame=start,sceneLocalEndFrame=start+c['frames'],outputStartFrame=pos)
 local[c['scene']]=start+c['frames'];pos+=c['frames']
assert pos==35441 and local=={c['scene']:max(v['sceneLocalEndFrame'] for v in old['cuts'] if v['scene']==c['scene']) for c in old['cuts']}
assert sum(c['frames'] for c in cuts if c['role']=='actual-game-candidate')==21193
assert sum(c['frames'] for c in cuts if c['role']=='explanation')==14128
intervals={};conflicts=[]
for c in cuts:
 if c['role']!='actual-game-candidate':continue
 key=c['sourcePath'];a,b=c['sourceInFrame'],c['sourceOutFrame']
 for x,y in intervals.setdefault(key,[]):
  if max(a,x)<min(b,y):conflicts.append([key,a,b,x,y])
 intervals[key].append((a,b))
assert not conflicts,conflicts
p.update(preparedAt=now,status='five-action-alignment-repairs-candidate',priorCandidate='projects/player-customization/planning/integer-action-allocation-candidate-v3.json',priorCandidateSha256=sha(oldpath),revisionReason='Five observed source/caption mismatches; original355boards preserved as baseline, repaired encoded pixels still pending.',cuts=cuts,cutCount=len(cuts),repairChanges=changes,repairCandidateReviews=['projects/player-customization/production/action-repair-candidate-direct-review-v1.json','projects/player-customization/production/action-repair-candidate-direct-review-v2.json'],allNativeSourceFramesUnique=True,issues=[],sourceAllocationApproved=False,finalTimingApproved=False,bodyRatioApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,next='Encode only changed native cuts, reuse verified baseline segments. Directly inspect every repaired cue/cut before final allocation and Nimbus mix.')
target=oldpath.with_name('integer-action-allocation-candidate-v4.json');assert not target.exists();target.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(cuts=len(cuts),changedBaselineCuts=len(changes),nativeFrames=21193,whiteFrames=14128,bodyFrames=35321,ratioErrorFrames=.4,approval=False)))
