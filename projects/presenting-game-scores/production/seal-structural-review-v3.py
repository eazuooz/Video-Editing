from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
stamp=datetime.now(timezone.utc).isoformat()
q2=read(BASE/'black-structural-qa-v2.json');q3=read(BASE/'black-structural-qa-v3.json')
for q in [q2,q3]:
 assert q['decodeExitCode']==q['extractionExitCode']==0 and q['samplePtsDirectlyVerified']
 assert sha(ROOT/q['videoPath'])==q['videoSha256']
 for f in q['samples']+q['boards']:assert sha(ROOT/f['path'])==f['sha256']
 assert all(f['captionReservePixelsAboveThreshold']==0 for f in q['samples'])
review2=dict(schemaVersion=1,reviewedAt=stamp,videoSha256=q2['videoSha256'],boards=q2['boards'],
 allElevenBoardsDirectlyRead=True,allSixtySixSamplePixelsDirectlyRead=True,allThirtyPreparedParagraphStatesCompared=True,
 resolvedIssues=['02 evaluation label clears moving token','04 criterion label stays on open floor and action labels clear tokens',
 '06 numeric observations fade sequentially with no simultaneous text overlap; gap text clears arrow',
 '07 all three elevated items remain visible on the tray','09 event label clears the rising token'],
 remainingIssue={'05-events-and-total':'Retained-value label still intersects the incoming token at p2 end; keep v2 as historical review and require targeted v3.'},
 structuralApproved=False,finalTimingApproved=False,finalCaptionCuePixelsReviewed=False,finalMediaApproved=False,localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-direct-review-v2.json',review2)
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
r=subprocess.run([node,'node_modules/typescript/bin/tsc','--noEmit','--project','tsconfig.presenting-game-scores.json'],cwd=ROOT/'motion-canvas',capture_output=True,text=True)
(BASE/'scoped-typescript-v3.log').write_text(r.stdout+r.stderr,'utf-8');assert r.returncode==0,r.stdout+r.stderr
selected=[s for s in q2['samples'] if s['scene']!='05-events-and-total']+q3['samples']
source=ROOT/'motion-canvas/src/projects/presenting-game-scores'
proof=dict(schemaVersion=1,slug='presenting-game-scores',reviewedAt=stamp,
 scope='Structural prototype only: independent 12-second scenes, no measured voice or narration captions',
 v2VideoSha256=q2['videoSha256'],v3VideoSha256=q3['videoSha256'],
 allV2ElevenBoardsAndV3TwoBoardsDirectlyRead=True,allSeventyEightReviewedSamplePixelsDirectlyRead=True,
 selectedStructuralSampleCount=len(selected),selectedSamples=selected,
 selectedBoards=[b for b in q2['boards'] if b['scene']!='05-events-and-total']+q3['boards'],
 scenes=10,paragraphs=30,style='research-black-v1',
 observedGeometry='Distinct projected top/front/side faces, perspective floor, occlusion, camera yaw and elevated-token draw ordering',
 observedSemanticMotion='Contribution tokens move between quantity/evaluation, into accumulated score; comparison arrow and sequential numeric observations; temporary emphasis disappears while totals remain',
 finalRetainedLabelRepair='Move retained-value label to stationary right-hand space at world (630,60,260). Read all12 target samples, including the incoming token trajectory and fade.',
 allObservedLabelOverlapsResolved=True,allSelectedCaptionReserveSamplesClear=True,
 prototypeStructuralPixelReviewApproved=True,actualAnimationContinuousReview=False,
 measuredNarrationTimed=False,finalTimingApproved=False,finalCaptionCuePixelsReviewed=False,allFinalPixels=False,finalMediaApproved=False,
 files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [source/'spatial-score-explanation.tsx',source/'explanation-timing.ts',source/'black-explanation-preflight-v1.ts',source/'black-event-label-preflight-v3.ts',*sorted((source/'scenes').glob('[0-9]*.tsx'))]],
 scopedTypeScript=dict(exitCode=r.returncode,command='node node_modules/typescript/bin/tsc --noEmit --project tsconfig.presenting-game-scores.json',scope='Own project and imported components; unrelated global project failures are not declared passed'),
 targetRenderObserved=dict(uiRenderButtonReturned=True,rendererExitCode=None,rendererExitDirectlyObserved=False,wholeDecodeExitCode=0,frames=721,timebase='1/90000'),
 preserveOldStructuralVersions=True,localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-direct-review-v3.json',proof)
checkpoint=read(BASE/'latest-checkpoint.json');checkpoint.update(recordedAt=stamp,structuralPrototypeReview=proof,
 nextAction='Preserve serialized approved-voice request. After actual voice and mandatory research resume, compare whole ASR and independent contexts, then adopt measured timing and render final black explanations.')
save(BASE/'latest-checkpoint.json',checkpoint)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';queue=read(qp);item=next(i for i in queue['items'] if i['slug']=='presenting-game-scores')
item['structuralPreview']=dict(evidence=(BASE/'black-structural-direct-review-v3.json').relative_to(ROOT).as_posix(),stage='structural-prototype-pixels-reviewed',prototypeApproved=True,measuredNarrationTimed=False,allFinalPixels=False,
 reviewedSamples=78,selectedSamples=72,boardsRead=13,cpuHeavyJobs=0,gpu=0,imagesGitAdded=0)
item['nextAction']=checkpoint['nextAction'];queue['updatedAt']=stamp;save(qp,queue)
print('10 structural scenes/30 prepared paragraphs: v2 66 pixels + targeted v3 12 pixels directly read; 72 selected samples approved as prototype only. Final gates remain false; scoped TS exit0.')
