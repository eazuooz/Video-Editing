"""Record directly read primary target pixels and prepare three additive guides."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(t,p);return
  except PermissionError:
   if i==39:raise
   time.sleep(.15)
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
stamp=datetime.now(timezone.utc).isoformat();s=read(BASE/'fresh-engineer02-native-extraction-v1.json')
assert s['exitCode']==0 and len(s['frames'])==36 and len(s['boards'])==6
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
for x in s['frames']+s['boards']:assert sha(ROOT/x['path'])==x['sha256']
for b in s['boards']:b['directlyRead']=True
s.update(allBoardsDirectlyRead=True,actualExitObserved=True,actualExitCodeObserved=0,sessionId=17718,processIdentityAbsentVerifiedAt=stamp);save(BASE/'fresh-engineer02-native-extraction-v1.json',s)
nativeProof=BASE/'fresh-engineer02-native-direct-review-v1.json';assert not nativeProof.exists()
save(nativeProof,dict(schemaVersion=1,reviewedAt=stamp,sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],all36NativeFramesAnd6BoardsDirectlyRead=True,sessionId=17718,exitCode=0,frames=s['frames'],boards=s['boards'],
 observationsKo='f2580/f2581과 f2699/f2700은 큰 초록 적을 두고 바위 틈을 이동하는 실제 장면. f3300/f3390/f3438까지 추격/좁은 길/폭발, f3581–3583은 열린 자리로 넘어가는 연속 장면이다. f3660에서 금빛 광물에 접근, f3780–4260에서 조각 소실과 Gold 증가를 직접 관찰했다. f4380까지 채굴 후 이동이 이어지고 f4427–4440은 LEVEL UP 광선이므로 실제 배정은73초까지로 제한한다. f4620–4740은 원이 나타나는 방향으로 접근, f4800–4980은 바위 옆/원 가까이, f5160–5280은 원 안 캐릭터와 남은 적, f5400–5460은 보급 장치이며 실제 배정은 SUPPLY 메뉴 전90.8초까지만 허용한다.',
 candidateIntervalsFrames=[[2580,3582],[3582,4380],[4620,5448]],finalCaptionPixelsApproved=False,bodyRatioApproved=False,localOnly=True,newGitRasterFiles=0))
guides=[
 dict(id='23-mining-and-pursuit',titleKo='채굴 목적과 추격이 만나는 자리',titleEn='Mining and pursuit share the same space',insertAfterScene='04-mining-route',insertAfterParagraph=4,sourceInFrame=3582,sourceOutFrameExclusive=4380,
 koLines=['새 채굴 장면입니다. 캐릭터가 금빛 광물에 다가가고, 파낸 조각이 사라집니다.','뒤따르는 적도 함께 보세요. 광물에 접근하는 목적과 위험에서 떨어지는 움직임이 같은 공간에 놓입니다.'],
 enLines=['Here is another mining shot. The character approaches the golden deposits and mined pieces disappear.','Watch the pursuing enemies too. Moving toward minerals and away from danger takes place in the same space.'],viewerFocus='Approach to visible golden deposits, pieces disappearing, pursuers remaining nearby.',diagramConnection='Projected mineral block and pursuing actor distinguish an approach vector from an avoidance vector.'),
 dict(id='24-destination-and-danger',titleKo='원 안에 도착해도 읽을 대상은 남는다',titleEn='A destination still has nearby danger',insertAfterScene='07-purpose-combination',insertAfterParagraph=1,sourceInFrame=4620,sourceOutFrameExclusive=5448,
 koLines=['이번에는 표시된 원을 향합니다. 캐릭터가 바위 옆을 지나 원 가까이로 움직이는 모습을 보세요.','안에 들어가도 가까운 적은 남아 있습니다. 목적지에 접근하는 일과 주변 위험을 살피는 일이 함께 이어집니다.'],
 enLines=['Now the character heads toward a marked circle. Watch the movement past the rocks and toward its edge.','Nearby enemies remain after the character enters. Reaching a destination and observing danger continue together.'],viewerFocus='Circle appears after approach begins; rock edge, entering actor and remaining nearby enemies. End before the supply selection menu.',diagramConnection='Projected circle and actor trajectories connect reaching a place with ongoing observations, without claiming victory or a best tactic.'),
 dict(id='25-gap-during-pursuit',titleKo='추격자를 보며 통과할 틈도 읽기',titleEn='Read the gap while watching pursuit',insertAfterScene='05-route-under-pressure',insertAfterParagraph=2,sourceInFrame=2580,sourceOutFrameExclusive=3582,
 koLines=['다른 추격 구간입니다. 큰 초록 적과 캐릭터 사이에 바위가 놓이고, 좁은 길을 따라 이동합니다.','캐릭터만 따라가지 말고 지나갈 틈도 보세요. 같은 회피 행동에 지형을 읽는 판단이 더해지는 장면입니다.'],
 enLines=['This is a separate pursuit section. Rocks stand between the large green enemy and the character moving along a narrow route.','Watch the usable gap as well as the character. Familiar avoidance is accompanied by reading the terrain.'],viewerFocus='Separate visible pursuer, avatar and rock boundaries; compare narrowing usable ground while motion continues.',diagramConnection='Projected rock volumes occlude the direct line while the actor uses a visible gap.')]
for g in guides:g.update(sourceStem='drgs-engineer-crystalline-02',sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],independentMotionCanvasRequired=True,role='proposed-actual-voice-measurement-pending')
plan=PROJECT/'planning/fresh-observation-guides-v4.json';assert not plan.exists()
save(plan,dict(schemaVersion=1,preparedAt=stamp,sourceReview=rel(nativeProof),guides=guides,preserveOriginal51AndApprovedEightGuides=True,preserveCurrentJoined04=True,sourceAudioInFinal=False,loop=False,slowdown=False,unrelatedIdle=False,measuredAudioSeconds=None,finalSourceAllocationApproved=False,bodyRatioApproved=False,humanListening='pending',publicRightsApproval='pending'))
scriptKo=PROJECT/'script/fresh-observation-guides.ko.v4.json';scriptEn=PROJECT/'script/fresh-observation-guides.en.v4.json'
for p,lang,key,title in [(scriptKo,'ko','koLines','실제 플레이 관찰 추가 안내'),(scriptEn,'en','enLines','Additional actual-play observations')]:
 save(p,dict(language=lang,independentlyAuthored=True,planning=rel(plan),title=title,scenes=[dict(id=g['id'],title=g['titleKo' if lang=='ko' else 'titleEn'],lines=g[key]) for g in guides]))
candidatePath=PROJECT/'sources/game-candidates.json';candidates=read(candidatePath)
candidates['freshEngineer02Review']=dict(reviewedAt=stamp,sourceStem='drgs-engineer-crystalline-02',officialFileUrl='https://drive.google.com/file/d/1amv63bfqpQzq3qj9U7GxLi7DlxXlYmdM/view',sourcePath=s['sourcePath'],sha256=s['sourceSha256'],version='2024-02-14 early-access official Funday press B-roll',wholeDecodeExitCode=0,coarseReview='projects/similar-game-design/production/fresh-primary-engineer02-coarse-direct-review-v1.json',nativeReview=rel(nativeProof),priorUse='New source file; no reuse from the six current source-bank files or prior video allocations.',chosen=guides,rejected='Level/Supply/Overclock menus, level-up tail beyond73s and unneeded later shots.',rights='Retain already reviewed Funday commercial original creator video conditions and internal records; public IP/rights approval remains pending.',recentGames='Same concept-matched current mining game, fresh distinct official source/segments. Bro arena and coop comparisons remain preserved.',finalAllocationApproved=False);save(candidatePath,candidates)
manifest=read(PROJECT/'project.json');settings=read(BASE/'guides-and-localized-repair-tts-request-v3.json')['ttsSettings'].copy();settings.update(outputDir='shared/output/narration/similar-game-design/qwen3-1.7b-fresh-guides-v4',filenameStem='similar-game-design-qwen3-1.7b-fresh-guides-v4')
manifest.update(status='fresh-observation-voice-measurement-override-only',tts=settings)
manifest['paths'].update(script=rel(scriptKo),scriptEn=rel(scriptEn))
override=BASE/'fresh-guides-tts-manifest-v4.json';save(override,manifest)
protected=read(BASE/'guides-and-localized-repair-tts-request-v3.json')['protectedInputs']
for d in ['shared/output/narration/similar-game-design/qwen3-1.7b-guides-and-onset-v3/chunks','shared/output/narration/similar-game-design/current-mining-pcm-join-v1']:
 for p in sorted((ROOT/d).glob('*.wav')):protected.append(dict(path=rel(p),sha256=sha(p)))
for p in [nativeProof,scriptKo,scriptEn,plan,override]:protected.append(dict(path=rel(p),sha256=sha(p)))
review=BASE/'paired-fresh-guides-direct-review-v4.json'
save(review,dict(schemaVersion=1,reviewedAt=stamp,status='prepared-awaiting-paired-whole-text-direct-read',contentReadyForApprovedVoiceMeasurement=False,wholePairedParagraphsReviewed=False,guides=guides,protectedInputs=protected,overviewPromise='Arena, mining route, together play remains actual original order; these three observations elaborate mining/route/purpose. No original paragraph or PCM shortened.',finalSourceAllocationApproved=False,bodyRatioApproved=False))
request=BASE/'fresh-guides-tts-request-v4.json';save(request,dict(schemaVersion=1,preparedAt=stamp,slug='similar-game-design',scriptReview=rel(review),pairedWholeTextReview=False,overviewPromiseReview=False,manifestOverride=rel(override),protectedInputs=protected,ttsSettings=settings,cpuThreads=2,gpuJobs=1,batchSize=1,scenes=[dict(id=g['id'],text=' '.join(g['koLines']),enLines=g['enLines'],path=settings['outputDir']+'/chunks/'+g['id']+'-scene.wav') for g in guides],sourceAllocationApproved=False,bodyRatioApproved=False,originalChunksRegenerated=False))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='fresh-primary-three-guides-prepared-awaiting-paired-read',freshPrimaryReview=rel(nativeProof),freshGuidePlan=rel(plan),ownedJob=dict(status='closed-native-targets-all36frames-read',pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],sessionId=17718,workerExpectedRunning=False,exitCode=0),nextAction='Directly read all new3 KOEN guide texts and overview promises, seal current gates; schedule single GPU TTS after foreign lease and completed research job boundary; verify original research resumes after success/failure. Preserve approved67 current PCM.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],freshPrimaryReview=rel(nativeProof),nextAction=cp['nextAction']);q.update(updatedAt=stamp,lastProgressAt=stamp);save(qp,q)
print(json.dumps(dict(guides=3,paragraphs=6,voiceCreated=False,current67Preserved=True)))
