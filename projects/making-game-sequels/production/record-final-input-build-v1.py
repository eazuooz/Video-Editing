"""Record observed builds without claiming mixed-ASR/final-pixel approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(120):
        try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
        except OSError:
            if n==119:raise
            time.sleep(.25)
r=read(W/'framed-visual-recovery-execution.json');assert r['exitCode']==0
v=read(W/'visual-build.json');m=read(W/'mix-settings.json');plan=read(W/'plan.json')
assert len(r['cuts'])==85 and len(r['white'])==7 and v['frames']==35583
assert m['planSha256']==v['planSha256']==sha(W/'plan.json')
for row in v['segments']:assert sha(ROOT/row['video'])==row['sha256']
assert sha(ROOT/v['video'])==v['sha256']
previous=read(W/'framed-visual-execution.json');assert previous['exitCode']==1
assert all(next(c for c in r['cuts'] if c['id']==old['id'])['sha256']==old['sha256'] for old in previous['cuts'])
proof=dict(schemaVersion=1,observedAt=stamp,planSha256=sha(W/'plan.json'),
    currentNativeCuts=85,independentWhiteSegments=7,bodyActualFrames=20918,
    bodyExplanationFrames=13945,bodyFrames=34863,finalFrames=35583,seconds=593.05,ratioErrorFrames=.2,
    preserved21PreviouslyCompletedCrops=True,historicalQueueLock=rel(W/'framed-visual-execution.json'),
    recoveryExecution=rel(W/'framed-visual-recovery-execution.json'),
    noRepeatedTtsOrRawNativeCompile=True,allNativeDecodeExitCode0=True,
    visualSha256=v['sha256'],mixWavSha256=m['wavSha256'],mixAacSha256=m['aacSha256'],
    mixLufs=-16.04,mixTruePeakDbtp=-1.98,allCurrent554_584SecondsPcmPreserved=True,
    finalMixedAsrApproved=False,finalEncodedCaptionPixelsReviewed=False,
    rendered=False,qaApproved=False,collected=False,privateUploaded=False,
    inputTimingApproved=True,inputPixelsApproved=True,newGitImages=0,mediaInGit=False,
    humanWholeListening='pending',humanPronunciation='pending')
write(W/'observed-media-builds.json',proof)
p=BASE.parent/'project.json';d=read(p)
d['status']='current13-guided60-inputs-built-final-mixed-ASR-and-caption-QA-pending'
d['audio']['mixStatus']='Current554.584s preserved component PCM placed and mixed with continuous approvedNimbus;593.05s AAC measured -16.04LUFS/-1.98dBTP. Final mixed ASR/direct review pending.'
d['editing']['timingStatus']='35583 frames/593.05s;85 unique native cuts and7 white segments,60:40 error0.2frame. Reviewed input timing/pixels and actual visual/mix built; final mixed ASR and encoded caption/cut QA pending.'
d['paths']['mixSettings']=rel(W/'mix-settings.json');d['paths']['visualBuild']=rel(W/'visual-build.json')
write(p,d)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath);i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
i['currentFinalMediaBuilds']=proof
if 'measuredEditCandidate' in i:
    old=i['measuredEditCandidate'].copy();i.setdefault('historicalPreFinalInputCandidate',old)
    i['measuredEditCandidate'].update(nativeCuts=85,koCues=308,enCues=173,finalFrames=35583,
        actualFrames=20918,explanationFrames=13945,finalTimingApproved=True,
        bodyRatioApproved=True,allInputSamplePixelsReviewed=True,allFinalPixelsReviewed=False)
i.update(updatedAt=stamp,finalMixBuilt=True,finalMixAsrApproved=False,allFinalPixelsApproved=False,
    rendered=False,qaApproved=False,collected=False,privateUploaded=False)
q['updatedAt']=stamp;write(qpath,q)
for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
    d=read(p)
    for key in ['currentFinalMediaBuilds','measuredEditCandidate','updatedAt']:d[key]=i[key]
    d.update(finalMixBuilt=True,finalMixAsrApproved=False,allFinalPixelsApproved=False,
        rendered=False,qaApproved=False,collected=False,privateUploaded=False)
    write(p,d)
print(json.dumps(proof,ensure_ascii=False))
