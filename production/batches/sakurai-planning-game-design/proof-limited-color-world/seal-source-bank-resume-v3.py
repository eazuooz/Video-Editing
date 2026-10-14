"""Preserve v1 and record bounded additional normal-speed source actions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,copy,subprocess,psutil
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;BASE=ROOT/'projects/limited-color-world/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=P/'plant-endpoints-execution-v6.json';d=read(sp)
assert d['exitCode']==0 and d['actualOuterExitCode']==0 and d['actualOuterExitToolObservation']=='c81b32'
out=P/'plant-contour-endpoints-direct-review-v6.json';r=read(out);c=d['cuts'][0]
assert r['all6EndpointSamplesAndOneBoardDirectlyRead'] and r['allHashesAndNativePtsVerified']
assert r['executionSha256']==sha(sp) and r['actualExitTool']=='c81b32'
for s in c['samples']:assert s['pts']==s['nativeFrame']*256 and sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['captionTestPath'])==s['captionTestSha256']
for b in c['boards']:assert sha(ROOT/b['path'])==b['sha256']
assert all(sha(ROOT/p)==h for p,h in d['protectedInputs'].items()) and all(sha(ROOT/p)==h for p,h in d['protectedOriginal8Pcm'].items())
v4=read(P/'extra-native-action-execution-v4.json');rv4=read(P/'extra-native-action-direct-review-v4.json')
v5=read(P/'extra-native-targets-execution-v5.json');rv5=read(P/'extra-native-target-direct-review-v5.json')
assert rv4['all27BoardsAnd134SamplesDirectlyRead'] and rv5['all12BoardsAnd57SamplesDirectlyRead']
old=P/'source-action-bank-v1.json';bank=copy.deepcopy(read(old));dest=P/'source-action-bank-v2.json';assert not dest.exists()
sources={s['sourceKey']:s for s in bank['sources']}
replacement={'room-door-approach':'room-door-clean-end','portrait-corridor-travel':'corridor-moving-clean-end','four-mushroom-ledged-arrival':'mushroom-arrival-moving-only'}
chosen=[]
for x in v4['cuts']:
 if x['key']=='fence-route-part1':continue
 if x['key'] in replacement:x=next(y for y in v5['cuts'] if y['key']==replacement[x['key']])
 chosen.append(x)
chosen+= [x for x in v5['cuts'] if x['key'] in ['tree-outline-step-away','mushroom-erase-shrink-and-return','flower-route-exit-before-wipe']]
chosen.append(c)
rv4notes={x['key']:x['observed'] for x in rv4['verifiedCuts']};rv5notes={x['key']:x['observed'] for x in rv5['verifiedCuts']}
for x in chosen:
 src=sources[x['source']];a,b=x['startFrame'],x['endFrameExclusive']
 note=rv5notes.get(x['key'],rv4notes.get(x['key'],r['observation']))
 key='mushroom-return-crossing' if x['key']=='mushroom-erase-shrink-and-return' else x['key']
 label={'tree-outline-paint':'나무: 색 변경에도 남는 윤곽','tree-outline-step-away':'나무와 길의 윤곽','portrait-corridor-continuation':'복도: 테두리를 따라 이동','corridor-moving-clean-end':'복도: 테두리를 따라 이동',
 'plant-contour-paint-only':'식물: 칠하기 뒤 나타나는 가지 윤곽','mushroom-return-crossing':'버섯: 접촉 뒤 바뀌는 높이','room-door-clean-end':'방: 문과 가구의 윤곽'}.get(key,'길과 대상의 경계')
 bank['windows'].append(dict(key=key,sourceKey=x['source'],sourceSha256=src['sourceSha256'],startFrame=a,endFrameExclusive=b,startPts=a*256,endPtsExclusive=b*256,
 timeBase='1/15360',frameRate='60/1',durationSeconds=(b-a)/60,framingUpPixels=x['framingUpPixels'],sameFrameBottomBlurPixels=x['framingUpPixels'],
 boundaryDirectReviewApproved=True,placeholderFramingSampleReviewApproved=True,normalSourcePlaybackBasis='Native source60fps with absolutePTS verified and selected0.5s samples/boundaries directly read; browser continuous playback not approved.',
 provisionalInsertion=x['provisionalInsertion'],visibleAction=note,viewerFocus=label,diagramConnection='Preserved spatial outline/state/foreground/contrast comparisons; map only matching generic statement and name changed game object.',
 observation=note,onScreenObjectLabel=label,normalPlaybackRate=1,loop=False,slowdown=False,sourceAudioUse=False,selectedForNarrationPlanning=True,
 finalUseDurationSeconds=None,allFinalCueUiApproved=False,trimmedDynamicFramingPlaybackApproved=False,allContinuousFramesReviewed=False))
# Different native frames, no accidental double-counting of earlier bank actions.
for sk in sources:
 intervals=sorted((x['startFrame'],x['endFrameExclusive'],x['key']) for x in bank['windows'] if x['sourceKey']==sk)
 for previous,current in zip(intervals,intervals[1:]):assert current[0]>=previous[1],(previous,current)
total=sum(x['endFrameExclusive']-x['startFrame'] for x in bank['windows']);assert total==8475
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
check=subprocess.run([node,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,check.stdout+check.stderr
bank.update(schemaVersion=2,recordedAt=now(),status='bounded-additional-source-actions-approved-for-measurement-planning',
 sourceAdoptionApproved=True,adoptionScope='Existing16+bounded15 new windows at native normal rate, selected pixels and placeholder framing only; final narration allocation, cue/UI, continuous framing, body ratio and public-rights approval remain pending.',
 baselineBank=dict(path=rel(old),sha256=sha(old)),maximumUniqueSeconds=total/60,maximumUniqueNativeFrames=total,
 currentDistinctCheck=dict(exitCode=0,stdout=check.stdout,stderr=check.stderr),actualBodyRatioApproved=False,allFinalPixelsApproved=False,
 allNativeFramesReviewed=False,wholeContinuousViewingOrListeningApproved=False,humanListeningApproved=False,publicRightsApproved=False,
 finalSourceAllocationApproved=False,externalResearchChanges=0,rasterGitAdditions=0)
for proof in [P/'extra-native-action-direct-review-v4.json',P/'extra-native-target-direct-review-v5.json',out,P/'content-studio-change-review-v7.json']:
 bank['proofs'].append(dict(path=rel(proof),sha256=sha(proof)))
bank['exclusions']+=['V4 Lemon357–359.5 standing/wipe/inaccurate fence label','V5 branch67–71 platform-height/climb not established; separate68.5–70.5 contour only','gift collection/dialogue and later letterbox are not selected','Corridor/tree/plant cuts require changed-object label and generic matching narration; never place under house-specific or mushroom-height assertions.']
save(dest,bank)
candidate=ROOT/'projects/limited-color-world/sources/game-candidates-v2.json';assert not candidate.exists();save(candidate,bank)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),sourceBankSealRecoveredAfterDuplicateRefresh=True,sourceBankFirstSealExitCode=1,sourceBankFirstSealTool='7ba4b7',stage='bounded-source-bank-v2-ready-additive3bridge-measurement',sourceBankV2=rel(dest),sourceBankV2Sha256=sha(dest),
 maximumUniqueActionSeconds=141.25,sourceBoundedPlanningApproved=True,finalTimingApproved=False,
 nextAction='Prepare one protected additive3bridge voice request; do not regenerate original8PCM/32ASR. Measure new3 under owned cooperative research handoff then review current whole/context ASR; exact voice-based unique actual60/explanation40 allocation and final cues remain pending.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
 raw=qp.read_bytes();q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='limited-color-world');assert item['videoId'] is None
 item.update(stage=cp['stage'],nextAction=cp['nextAction'],sourceBankV2=rel(dest));q['updatedAt']=q['lastProgressAt']=now()
 if qp.read_bytes()==raw:save(qp,q);break
else:raise RuntimeError('Concurrent queue change')
print(json.dumps(dict(bank=rel(dest),sha256=sha(dest),windows=len(bank['windows']),maximumUniqueSeconds=total/60,finalRatioApproved=False)))
