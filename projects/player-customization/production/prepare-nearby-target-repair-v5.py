"""Keep four verified repairs; replace one unclear nearby-target sentence only."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
e=read(BASE/'action-repaired-pixels-execution-v2.json')
assert e['exitCode']==0 and len(e['boards'])==46 and len(e['samples'])==272
for x in [*e['boards'],*e['samples']]:assert sha(ROOT/x['path'])==x['sha256']
review=dict(schemaVersion=1,slug='player-customization',reviewedAt=now,execution='projects/player-customization/production/action-repaired-pixels-execution-v2.json',
 allBoardsDirectlyRead=True,allSamplesDirectlyRead=True,boardCount=46,sampleCount=272,hashVerifiedFiles=318,hashMismatches=0,
 boards=[{**b,'directlyRead':True} for b in e['boards']],samples=[{**s,'directlyRead':True} for s in e['samples']],
 resolvedIssues=[
  dict(issue='09p1 stationary rush opening',boards='001–006',observation='New24s Gauss shows caster rushing and blue trail;129391s rush continues. Preserved26.2s separate shot supports following foe relation. Fixed cues34–37 readable; no invented single continuous trial.'),
  dict(issue='09p4 ten-frame early cut',boards='007–018',observation='Yareli rotating Aquablades and moving caster retained through cue60. Dante first frame88.2833 exactly receives cue61 directional-action phrase; following projectile target sequence and cues62–63 readable.'),
  dict(issue='04p1 twenty-three-frame late cut',boards='019–025',observation='Gauss moving straight remains through cue149; Yareli first214.2s matches cue150 surrounding-range phrase. Ring/caster/nearby foes and cue151 shown; later04p2 begins217.4167 with preserved launch.'),
  dict(issue='04p2 Merulina mismatched nearby action',boards='025–031',observation='New72.8–74.75 Aquablades caster passes close foe and turns toward two foes. Cues155/156 match spatial relation;75.05 burst excluded. White04p3 begins224.3333 with projected top/front/side platforms and moving comparison.'),
 ],
 unresolvedIssues=[dict(issue='12p1 nearby target not clearly identifiable',boards='032–046',outputFrames=[14753,14931],observation='New154.3167–157.2833 cropped2021 segment shows ring/caster around fountain and stairs, but cue173 nearby-target view contains an unclear golden shape beside a decorative planter. Read full/cropped source through CUA; neither that shape nor its identity is adequate near-foe evidence. Do not approve from earlier native-candidate note. Earlier/later2024 targets are visible, but this clause still needs replacement.')],
 prior355BoardFullReview='projects/player-customization/production/selected-pixels-direct-review-v1.json',
 allSelectedPixelsApproved=False,sourceAllocationApproved=False,finalTimingApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,imagesLocalOnly=True,newGitImages=0)
write(BASE/'action-repaired-pixels-direct-review-v2.json',review)
p=read(ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v4.json');src=next(s for s in p['sources'] if s['key']=='yareli')
pts=read(ROOT/src['ptsPath'])['frames'];new=copy.deepcopy(p)
for idx,c in enumerate(new['cuts'],1):
 c['baselineCutIndex']=idx;c['repairNativeOnly']=False
 if c['scene']=='12-nearby-space-guide' and c['paragraph']==1 and c.get('sourceKey')=='yareli155':
  assert c['sourceInFrame']==9259 and c['frames']==178
  c.update(sourceKey='yareli',sourcePath=src['path'],sourceSha256=src['sha256'],sourceInFrame=3990,sourceOutFrame=4168,cropCandidate=src['cropCandidate'],firstNativePts=int(pts[3990]['best_effort_timestamp']),lastNativePts=int(pts[4167]['best_effort_timestamp']),firstNativeSeconds=float(pts[3990]['best_effort_timestamp_time']),originalSourceInSeconds=66.5,
   visibleAction='Aquablades overhead caster within rotating circle and nearby armored foes, followed by visible close target reaction; camera changes retained as visible source edits',repairNativeOnly=True,sourceActionAligned=False,continuousSelectedPixelsReviewed=False,fixedCaptionPixelsReviewed=False)
assert sum(c['repairNativeOnly'] for c in new['cuts'])==1
intervals={}
for c in new['cuts']:
 if c['role']!='actual-game-candidate':continue
 a,b=c['sourceInFrame'],c['sourceOutFrame'];used=intervals.setdefault(c['sourcePath'],[])
 assert all(max(a,x)>=min(b,y) for x,y in used),(c,used)
 used.append((a,b))
new.update(preparedAt=now,status='one-nearby-target-repair-candidate',priorCandidate='projects/player-customization/planning/integer-action-allocation-candidate-v4.json',priorCandidateSha256=sha(ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v4.json'),
 revisionReason='Four encoded action repairs directly passed; one unclear near-target clause replaced by fresh official profile66.5–69.4667. Preserve exact178frames, all PCM/captions/starts, original explanations and other138segments.',
 priorFocusedReview='projects/player-customization/production/action-repaired-pixels-direct-review-v2.json',
 nativeCuaReview=dict(tab=75,url='http://127.0.0.1:9242/',boundedPlayback=[66.5,69.466667],directScreenshots=[66.5,68,69.45],observation='66.5 overhead caster clearly inside Aquablades with armored targets;68 close target with rotating arc;69.45 humanoid target reacting within arc. Source cuts retained; no damage-number/current-build/superiority claim. Candidate caption/cut matching awaits encoded review.'),
 issues=[],sourceAllocationApproved=False,finalTimingApproved=False,bodyRatioApproved=False,allFinalPixels=False,finalMixedAsrApproved=False)
write(ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v5.json',new)
text=(BASE/'compile-action-repaired-inputs-v2.py').read_text('utf-8')
text=text.replace('selected-inputs-v2','selected-inputs-v3').replace('integer-action-allocation-candidate-v4.json','integer-action-allocation-candidate-v5.json')
text=text.replace("STATE=BASE/'selected-inputs-execution-v2.json'", "STATE=BASE/'selected-inputs-execution-v3.json'")
text=text.replace("baseline=read(BASE/'selected-inputs-execution-v1.json');assert baseline['exitCode']==0 and baseline['completedCuts']==136", "baseline=read(BASE/'selected-inputs-execution-v2.json');assert baseline['exitCode']==0 and baseline['completedCuts']==139\nassert read(BASE/'action-repaired-pixels-direct-review-v2.json')['allBoardsDirectlyRead']")
text=text.replace('Reused129', 'Reused138')
a=text.index(" cp=OUT/'candidate-body.captioned-silent.mp4';")
b=text.index(" s.update(status='closed-selected-candidate-inputs-built-pixel-review-pending'",a)
text=text[:a]+''' cp=OUT/'repair-window.captioned-silent.mp4';asspath=ROOT/baseline['captionAss'];assert sha(asspath)==baseline['captionAssSha256'];s['status']='encode-one-repair-fixed-caption-preview';checkpoint()
 lo=14513;hi=14931;wn=hi-lo
 ff(['-ss',f'{lo/60-.00001:.8f}','-i',body,'-an','-filter_threads','1','-vf',f'setpts=PTS-STARTPTS+{lo}/60/TB,ass={rel(asspath)},setpts=PTS-STARTPTS','-frames:v',str(wn),'-fps_mode','passthrough',
  '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',cp],'encode-one-repair-captions')
 probe(cp,wn)
 assert not ff(['-i',cp,'-an','-f','null','-'],'whole-repair-caption-window-decode').strip()
 s.update(captionPreviewBodyStartFrame=lo,captionPreviewFrames=wn,captionPreviewFullBody=False)
''' +text[b:]
target=BASE/'compile-nearby-repaired-inputs-v3.py';assert not target.exists();target.write_text(text,'utf-8')
# Only the418-frame encoded window gets new samples; completed four repairs are retained.
text=(BASE/'extract-action-repaired-pixels-v2.py').read_text('utf-8')
text=text.replace('action-repaired-pixels-v2','nearby-repaired-pixels-v3').replace('selected-inputs-execution-v2.json','selected-inputs-execution-v3.json')
text=text.replace("STATE=BASE/'action-repaired-pixels-execution-v2.json'", "STATE=BASE/'nearby-repaired-pixels-execution-v3.json'")
text=text.replace('assert len(changed)==10','assert len(changed)==1')
text=text.replace("expr=\"select='\"+'+'.join(f'eq(n,{n})' for n in indices)+\"'\"", "offset=build['captionPreviewBodyStartFrame'];assert all(0<=n-offset<build['captionPreviewFrames'] for n in indices)\n expr=\"select='\"+'+'.join(f'eq(n,{n-offset})' for n in indices)+\"'\"")
text=text.replace('changedCuts=10','changedCuts=1').replace('Five changed action/caption regions with two-second adjacent context; baseline355boards retained; final full-pair pixels pending','One newly replaced nearby-target sentence with two-second adjacent context; prior355+46boards retained, four other repairs passed; final full-pair pixels pending')
target=BASE/'extract-nearby-repaired-pixels-v3.py';assert not target.exists();target.write_text(text,'utf-8')
print(json.dumps(dict(planCuts=len(new['cuts']),reused=138,newNative=1,frames=35321,focusedFrames=418,approvals=False)))
