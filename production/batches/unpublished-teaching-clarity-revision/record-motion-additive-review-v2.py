"""Seal observed ASR exits and sampled annotation review; keep final gates pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p): return p.relative_to(ROOT).as_posix()

sp=R/'additions-contexts-asr-execution-v1.json';s=read(sp)
assert s['pid']==67760 and s['createTime']==1791650758.324412 and s['completed']==s['total']==6 and s['exitCode']==0
s.update(actualExitObserved=True,actualExitCode=0,actualExitToolChunk='9dac5d',sessionId=6455,actualExitRecordedAt=now())
save(sp,s)
ss=sp.with_name(sp.stem+'.session.json');sv=read(ss)
sv.update(actualExitCode=0,actualExitToolChunk='9dac5d',workerCurrentlyAlive=False,recordedAt=now());save(ss,sv)
rows=[]
for x in s['results']:
    assert sha(ROOT/x['sourcePath'])==x['sourceSha256']
    assert sha(ROOT/x['contextPath'])==x['contextSha256'] and x['exactSourceSampleBytesMatched']
    ambiguous=x['id']=='00a-p03'
    rows.append(dict(id=x['id'],expectedWhole=x['expectedKo'],recognizedWhole=x['text'],
        currentPcmSha256=x['sourceSha256'],contextSha256=x['contextSha256'],
        fullTextAndAllWordTimingsDirectlyRead=True,completeSentenceAndEndingPresent=True,
        missingWords=[],repeatedWords=[],meaningClaimsRetained=True,
        particleRecognitionAlternative={'expected':'이 관찰을','independentRecognition':'이 관찰의','wholeRecognition':'이 관찰을','humanPronunciationPending':True} if ambiguous else None,
        exactParticleMatchClaimed=not ambiguous,humanListeningApproved=False,humanPronunciationApproved=False))
p=R/'additions-contexts-asr-direct-review-v1.json';assert not p.exists()
save(p,dict(schemaVersion=1,recordedAt=now(),sourceExecution=rel(sp),sourceExecutionSha256=sha(sp),
    actualOuterExitCode=0,actualSession=6455,allSixFullIndependentTextsDirectlyCompared=True,
    rows=rows,fullUnmixedContentReviewPassed=True,allParticlesExact=False,
    humanPronunciationIssues=['00a-p03 관찰을/관찰의'],humanListeningApproved=False,
    humanPronunciationApproved=False,finalMixedVoiceApproved=False,baselinePcmRegenerated=0))

for version,session,chunk in [(1,69597,'historical-observed-exit0'),(2,69804,'f5ba98'),(3,51069,'2648a7')]:
    sp=R/f'opening-overlay-pilot-execution-v{version}.json';s=read(sp)
    assert s['exitCode']==0 and s['writtenFrames']==660
    for x in s['preparedSamples']+s['boards']: assert sha(ROOT/x['path'])==x['sha256']
    s.update(sessionId=session,actualExitObserved=True,actualExitCode=0,actualExitToolChunk=chunk,actualExitRecordedAt=now());save(sp,s)
    p=R/f'opening-overlay-pilot-sampled-direct-review-v{version}.json';assert not p.exists()
    save(p,dict(schemaVersion=1,recordedAt=now(),sourceExecution=rel(sp),sourceExecutionSha256=sha(sp),
        actualOuterExitCode=0,actualSession=session,allListedSamplesDirectlyRead=True,
        samples=s['preparedSamples'],boards=s['boards'],
        sampledPixelsPassed=version==3,
        findings={1:'NCC jumped to a different structural timber despite high confidence. Held.',
                  2:'Same-post guides improved association, but color refinement hid visible post at f255/375/495. Held.',
                  3:'All47 samples/eightboards show red aim direction, same front timber blue bracket or explicit offscreen arrow, gold floor focus. Labels avoid source HUD and remain above910. First frames intentionally introduce arrows sequentially.'}[version],
        allContinuousMovingFramesApproved=False,finalCuePixelsApproved=False,finalNarratedVideoApproved=False,
        worldCoordinateMeasurement=False,clinicalComfortOutcomeClaimed=False,newImageGitAdded=0))

raw=ROOT/'shared/assets/presenting-game-scores/raw'
source=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/opening-overlay-pilot-v3/opening.annotated.silent-pilot.mp4'
link=raw/'motion-opening-annotated-pilot-v3.mp4'
if not link.exists(): os.link(source,link)
assert os.path.samefile(source,link) and sha(source)==sha(link)
page=raw/'motion-opening-annotated-review-v3.html';assert not page.exists()
page.write_text('''<!doctype html><meta charset="utf-8"><title>Motion opening annotations V3</title>
<style>body{margin:12px;background:#111;color:#fff;font:16px sans-serif}video{width:min(1280px,100%);display:block}button{padding:10px;margin:6px}#state{white-space:pre}</style>
<h1>11초 정상속도 · 조준 방향 / 같은 배경 기둥 / 닿는 바닥</h1>
<p>무음 표시 검수. 최종 내레이션·고정자막 승인은 별도입니다.</p>
<video id="v" controls muted preload="auto" src="motion-opening-annotated-pilot-v3.mp4"></video>
<button id="start">처음부터 1배속 재생</button><button id="pause">일시정지</button><label>초 <input id="seek" type="number" step="0.01" value="0"></label><button id="go">이동</button><pre id="state"></pre>
<script>const v=document.getElementById('v');const out=document.getElementById('state');
document.getElementById('start').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.muted=true;v.play()};
document.getElementById('pause').onclick=()=>v.pause();
document.getElementById('go').onclick=()=>{v.pause();v.currentTime=Number(document.getElementById('seek').value)};
function update(){out.textContent=JSON.stringify({currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate,readyState:v.readyState},null,2)};
['timeupdate','pause','play','seeked','loadedmetadata','ended'].forEach(e=>v.addEventListener(e,update));</script>''','utf-8')
save(R/'opening-overlay-pilot-browser-preparation-v3.json',dict(recordedAt=now(),existingServerPid=27140,
    existingServerCreation='2026-10-09T10:34:26.837781+09:00',serverIdentityObservedChunk='58a0ee',
    source=rel(source),sourceSha256=sha(source),hardlink=rel(link),sameFileVerified=True,helper=rel(page),
    url='http://127.0.0.1:9250/'+page.name,serverStarted=0,newMediaEncoded=0,newImageGitAdded=0))

qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qpath)
stage='additive-whole-and-contexts-reviewed-opening-moving-review-pending'
q['execution'].update(stage=stage,ownedJob=None,next='Review existing11s annotation pilot at1x; then measured additive timing, retained on-footage annotations and current inventory refresh. All final mixed/pixel/publishing/schedule gates remain pending.')
for item in q['items']:
    if item['slug']=='motion-sickness-games':
        item.update(status=stage,currentExecution=None,additiveWholeTextReviewed=True,additiveIndependentContextsReviewed=True,
                    humanPronunciationIssues=['00a-p03 관찰을/관찰의'],openingSampledPixelEvidence=rel(R/'opening-overlay-pilot-sampled-direct-review-v3.json'))
save(qpath,q)
cp=R/'latest-checkpoint.json';c=read(cp);c.update(recordedAt=now(),stage=stage,ownedJob=None,
    currentUnmixedContentReviewPassed=True,currentUnmixedAsrApproved=False,humanPronunciationApproved=False,
    additiveContextReview=rel(p),next=q['execution']['next']);save(cp,c)
print(json.dumps(dict(contextsDirectlyReviewed=6,particleAlternativePending=1,pilotSampledReview='v3',movingReview=False,finalGates=False),ensure_ascii=False))
