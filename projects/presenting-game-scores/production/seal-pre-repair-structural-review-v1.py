from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=read(BASE/'black-structural-qa-v1.json')
for f in [*qa['samples'],*qa['boards']]:assert sha(ROOT/f['path'])==f['sha256']
issues={
 '02-score-and-lines':'Evaluation label intersects moving contribution token near p2 end.',
 '04-evaluation-weights':'Evaluation-criterion ground label has poor contrast behind growing gold tower; action labels touch moving tokens.',
 '05-events-and-total':'Contribution and retained-value labels overlap when the token reaches the accumulated tower.',
 '06-relative-gap':'Two numeric observations overlap during crossfade; rightward arrow crosses the later gap text.',
 '07-name-and-unit':'Left collected token disappears behind tray during camera yaw because XY-only draw ordering ignores elevated base.',
 '09-feedback-hierarchy':'Transient-event label touches token when it rises along its trajectory.'}
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),videoSha256=qa['videoSha256'],boards=qa['boards'],
 allTenBoardsDirectlyRead=True,allSixtySamplePixelsDirectlyRead=True,allThirtyPreparedParagraphStatesCompared=True,
 projectedTopFrontSideFacesObserved=True,spatialMotionChangesObservedInSamples=True,continuousWholeAnimationReviewed=False,
 blackPaletteReadable=True,allSelectedCaptionReserveSamplesClear=all(x['captionReservePixelsAboveThreshold']==0 for x in qa['samples']),
 issues=issues,structuralApproved=False,revisionRequired=True,finalTimingApproved=False,finalCaptionCuePixelsReviewed=False,finalMediaApproved=False,
 preserveOldVideoAndSixtyPngTenBoards=True,localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-pre-repair-direct-review-v1.json',review)
renderer=[p for p in psutil.process_iter(['pid','create_time','cmdline']) if p.info['cmdline'] and p.name().lower().startswith('ffmpeg') and 'presenting-game-scores-structural-preview-v2.mp4' in ' '.join(p.info['cmdline'])]
assert len(renderer)==1,[(p.pid,p.cmdline()) for p in renderer]
p=renderer[0]
execution=dict(schemaVersion=1,slug='presenting-game-scores',stage='black-structural-label-repair-v2-rendering',recordedAt=review['reviewedAt'],
 pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),previewServerPid=63080,previewServerSession=31622,cuaTabId='135',
 output='shared/output/presenting-game-scores/black-structural-preview-v1/presenting-game-scores-structural-preview-v2.mp4',
 ownCpuHeavyJobs=1,cpuThreads=2,gpu=0,measuredNarrationTimed=False,allFinalPixels=False,finalMediaApproved=False,
 engineSha256=sha(ROOT/'motion-canvas/src/projects/presenting-game-scores/spatial-score-explanation.tsx'),
 repairedIssues=issues,voiceWaitingSession=30677,voiceWaitingPid=38172,ownedResearchPauseOrProcessChanges=0)
save(BASE/'black-structural-label-repair-execution-v2.json',execution)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
item['structuralPreview']=execution;item['nextAction']='Inspect actual revised structural render completion and all changed pixels. Voice request remains serialized before loading; preserve foreign lease.'
q['updatedAt']=review['reviewedAt'];save(qp,q)
print('All original60 samples/10 boards directly reviewed,6 issues preserved; one actual CPU2 repair renderer recorded.')
