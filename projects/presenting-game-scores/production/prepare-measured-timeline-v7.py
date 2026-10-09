"""Prepare a measured, sample-preserving candidate timeline. No render/QA approval."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import hashlib, json, math, os, subprocess, wave
import numpy as np

BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[2]; PROJECT=BASE.parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
    t=p.with_name(p.name+'.recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
destination=BASE/'measured-timeline-candidate-v7.json'
assert not destination.exists(), 'Preserve the measured candidate; revise with a new version.'
selectionp=BASE/'current-voice-selection-v7.json';selection=read(selectionp)
assert selection['currentVoiceApproved'] and selection['originalParagraphsPreserved']==30
bankp=ROOT/'production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json'
assert sha(bankp)=='6317296ed845e2aefb34f45872f880e8f63557a1a0c3ffc44fb87cac52923ab2'
bank=read(bankp); sources={s['name']:s for s in bank['sources']}; cuts={c['cutId']:c for c in bank['cuts']}
voices={r['id']:r for r in selection['scenes']}; arrays={}
for r in voices.values():
    assert sha(ROOT/r['path'])==r['sha256']
    with wave.open(str(ROOT/r['path']),'rb') as w:
        assert (w.getframerate(),w.getsampwidth(),w.getnchannels(),w.getnframes())==(24000,2,1,r['samples'])
        arrays[r['id']]=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
for s in sources.values():
    assert sha(Path(s['rawPath']))==s['sha256'] and sha(Path(s['ptsPath']))==s['ptsSha256']

# Complete-clause quiet boundaries read against current whole ASR. No samples
# are removed, faded or sped up; these boundaries permit example insertions.
boundary_seconds={
 '01-overview':[3.395,10.67], '02-score-and-lines':[4.735,11.945],
 '03-same-count':[2.835,10.145], '04-evaluation-weights':[5.485,14.14],
 '05-events-and-total':[4.945,13.195], '06-relative-gap':[3.775,12.59],
 '07-name-and-unit':[4.315,11.30], '08-scoring-feedback':[6.695,14.68],
 '09-feedback-hierarchy':[4.46,12.25], '10-audit-and-close':[5.69,14.85]}
boundaries={k:[0]+[round(x*24000) for x in v]+[voices[k]['samples']] for k,v in boundary_seconds.items()}
quiet_rows=[]
for sid,points in boundaries.items():
    for n in points[1:-1]:
        b=arrays[sid][n-120:n+120].astype(float)
        quiet_rows.append(dict(id=sid,sample=n,seconds=n/24000,
            rms=float(np.sqrt(np.mean(b*b))),peak=int(np.max(np.abs(b))),
            method='10ms centered actual PCM bin; complete-paragraph ASR boundary; no removal or fade'))
split06=195480 # 8.145s, between full 2920 sentence and full later141 sentence.
b=arrays['06-relative-gap'][split06-120:split06+120].astype(float)
quiet_rows.append(dict(id='06-relative-gap',sample=split06,seconds=split06/24000,
    rms=float(np.sqrt(np.mean(b*b))),peak=int(np.max(np.abs(b))),
    method='Complete p2 first sentence ending8.10s / next sentence8.32s; actual10ms quiet bin inspected'))
assert quiet_rows[-1]['rms']<100 and quiet_rows[-1]['peak']<350

segments=[]; chapters=[]; placements=[]; cursor=120
def segment(sid,role,frames,chapter,**extra):
    global cursor
    assert frames>0
    row=dict(id=sid,role=role,startFrame=cursor,endFrameExclusive=cursor+frames,frames=frames,
        startSeconds=cursor/60,durationSeconds=frames/60,chapter=chapter,**extra)
    segments.append(row);cursor+=frames;return row
def actual(cid,chapter,start=None,end=None,frames=None,suffix=''):
    c=cuts[cid];s=sources[c['source']]
    start=c['startFrame'] if start is None else start;end=c['endFrameExclusive'] if end is None else end
    fps=Fraction(s['nativeFps']);duration=Fraction(end-start,1)/fps
    frames=round(duration*60) if frames is None else frames
    return segment(cid+suffix,'actual-existing-game',frames,chapter,source=s['name'],sourcePath=s['rawPath'],
        sourceSha256=s['sha256'],sourceStartFrame=start,sourceEndFrameExclusive=end,
        nativeFps=s['nativeFps'],nativeTimebase=s['timebase'],nativeStartPts=int(Fraction(start,1)/fps/Fraction(s['timebase'])),
        sourceDurationSeconds=float(duration),normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,
        standard60fpsSamplingOnly=True,framing=c['framing'],captionMaxLines=c['captionMaxLines'],
        visibleAction=c['visibleAction'],diagramConnection=c['diagramConnection'],sourceBankCutId=cid,
        nativePtsEvidence=s['ptsPath'],nativePtsEvidenceSha256=s['ptsSha256'],
        finalCuePixelsReviewed=False)
def black(sid,frames,chapter,diagram,phases,note):
    return segment(sid,'explanation',frames,chapter,style='research-black-v1',diagram=diagram,
        measured=True,paragraphMotionStarts=phases,narrationConnection=note,
        finalAnimatedPixelsReviewed=False,captionMaxLines=2)
def audio(sid,start,a=0,b=None,purpose='Whole reviewed PCM'):
    r=voices[sid];b=r['samples'] if b is None else b
    assert 0<=a<b<=r['samples']
    p=dict(id=f'{sid}-part-{len(placements)+1:02d}',voiceId=sid,sourcePath=r['path'],sourceSha256=r['sha256'],
        sourceStartSample=a,sourceEndSampleExclusive=b,samples=b-a,
        startSample=start,endSampleExclusive=start+b-a,startSeconds=start/24000,durationSeconds=(b-a)/24000,
        exactPcmBytesMustMatch=True,speechTrimmed=False,purpose=purpose)
    placements.append(p);return p['endSampleExclusive']
def chapter(n,title):
    row=dict(id=n,title=title,startFrame=cursor);chapters.append(row);return cursor*400
def close(): chapters[-1].update(endFrameExclusive=cursor,frames=cursor-chapters[-1]['startFrame'])

t=chapter('01','점수는 무엇을 말해 줄까?')
black('black-01-overview',1018,'01','01-overview',[0,3.395,10.67],'Full three-sentence overview; actual voice16.96s, not reported as20–30s.')
audio('01-overview',t);close()

t=chapter('02','진행량과 평가는 다르다');a=actual('classic-01','02')
e=black('black-02-separate-metrics',420,'02','02-score-and-lines',[0,.35,2.2],'Read separate updates during actual play, then preserve full original final paragraph comparing quantity/evaluation.')
n=boundaries['02-score-and-lines'][2]
end=audio('02-score-and-lines',t,0,n);audio('11-observe-separate-updates',end)
audio('02-score-and-lines',e['startFrame']*400,n);close()

t=chapter('03','같은 양, 다른 점수');a=actual('classic-02','03')
e=black('black-03-equal-counts',420,'03','03-same-count',[0,.2,2.4],'Original question and explanation over action; guide ends at equality sample f2057. Full design conclusion on projected towers.')
n=boundaries['03-same-count'][2];audio('03-same-count',t,0,n)
audio('12-observe-equal-quantity',t+round(15.04*24000))
audio('03-same-count',e['startFrame']*400,n);close()

t=chapter('04','무엇을 높게 평가할까?');actual('modern-01','04',frames=1305)
black('black-04-event-evaluation',450,'04','04-evaluation-weights',[0,.3,2.0],'Action labels observed in normal play; retained original conclusion and full reviewed 배점표 paragraph on illustrative gate, not a scoring formula.')
n=boundaries['04-evaluation-weights'][2];end=audio('04-evaluation-weights',t,0,n)
end=audio('13-observe-action-label',end);audio('04-evaluation-weights',end,n);close()

t=chapter('05','이번 행동과 누적 결과');actual('modern-02','05',frames=1259)
black('black-05-event-and-record',420,'05','05-events-and-total',[0,.15,4.3],'Full notice/record guide across actual-to-diagram cut. Contribution moves into retained stack; label fades after both roles are visible.')
n=boundaries['05-events-and-total'][2];end=audio('05-events-and-total',t,0,n)
end=audio('14-observe-notice-and-record',end);audio('05-events-and-total',end,n);close()

t=chapter('06','누구와 비교한 숫자일까?');a=actual('modern-03','06',frames=839)
first=black('black-06-observed-2920',720,'06','06-observed-2920',[0,6.24,9.5],
    'After complete actual modern03, compare exact previously observed f2915:27/14096 vs27/17016. Narration never pretends changing live values stay constant.')
audio('06-relative-gap',t,0,boundaries['06-relative-gap'][1])
end=audio('15-observe-equal-lines-gap',first['startFrame']*400)
audio('06-relative-gap',end,boundaries['06-relative-gap'][1],split06,'Complete first sentence of original p2, exact samples preserved')
head=actual('modern-04','06',end=3456,frames=318,suffix='-through-observation')
second=black('black-06-observed-141',690,'06','06-observed-141',[0,7.04,9.0],
    'After actual f3455, separate later snapshot29/19919 vs32/19778,+141. Full guide and original later sentence. Not a final winner or simultaneous earlier state.')
end=audio('16-observe-later-point-lead',second['startFrame']*400)
audio('06-relative-gap',end,split06,boundaries['06-relative-gap'][2],'Complete second sentence of original p2, exact samples preserved')
tail=actual('modern-04','06',start=3456,frames=703,suffix='-changing-lead-after-observation')
audio('06-relative-gap',tail['startFrame']*400,boundaries['06-relative-gap'][2],purpose='Resume normal action; full caution about intermediate lead versus final victory')
close()

t=chapter('07','이름과 단위를 붙이기');actual('classic-03','07')
e=black('black-07-names-units',807,'07','07-name-and-unit',[0,.2,6.985],
    'Named SCORE/LINES read during live play; original full object/unit/direction paragraphs on independently labeled illustrative tray.')
n=boundaries['07-name-and-unit'][1];end=audio('07-name-and-unit',t,0,n)
audio('24-observe-named-fields-clear-start',end);audio('07-name-and-unit',e['startFrame']*400,n);close()

t=chapter('08','계산을 읽는 순간');actual('balatro-hand','08')
black('black-08-read-inputs',240,'08','08-scoring-feedback',[0,.5,3.3],
    'Historic scored-hand shot then full retained explanation of labels. Illustrative chips and multiplier; never reproduce the press clip final score.')
count=actual('balatro-countup','08')
black('black-08-contribution-result',909,'08','08-scoring-feedback',[0,.4,5.4183333333],
    'Second distinct montage shot, followed by remaining original p2 and entire repaired p3. Illustrative2x3=6; no claimed continuous run.')
n=boundaries['08-scoring-feedback'][1]
audio('08-scoring-feedback',t,0,n,'Complete original p1 continues across shot-to-diagram without a speech cut')
audio('08-scoring-feedback',count['startFrame']*400,n,purpose='Complete original p2 and full reviewed p3; no repeated montage')
close()

t=chapter('09','남아 있는 숫자와 지나가는 알림');actual('classic-04','09')
black('black-09-stable-and-transient',446,'09','09-feedback-hierarchy',[0,.15,4.0],
    'Stable UI and fading notices read during actual play, then full conclusion continues on stable spatial value stacks.')
n=boundaries['09-feedback-hierarchy'][2];end=audio('09-feedback-hierarchy',t,0,n)
end=audio('18-observe-stable-reading',end);audio('09-feedback-hierarchy',end,n);close()

t=chapter('10','세 가지 질문으로 점검하기');actual('modern-05','10',frames=1079)
black('black-10-three-audit-gates',793,'10','10-audit-and-close',[0,2.8,7.0],
    'Read meanings/comparison/change before top-out. Entire original coaching conclusion preserved; no results/wait counted as action.')
n=boundaries['10-audit-and-close'][2];end=audio('10-audit-and-close',t,0,n)
end=audio('19-observe-reading-audit',end);audio('10-audit-and-close',end,n);close()

body_end=cursor;member_start=cursor;cursor+=600
actual_frames=sum(s['frames'] for s in segments if s['role']=='actual-existing-game')
black_frames=sum(s['frames'] for s in segments if s['role']=='explanation')
assert (actual_frames,black_frames,body_end-120,cursor)==(10999,7333,18332,19052)
assert abs(actual_frames-(body_end-120)*.6)<1
coverage=[]
for sid,r in voices.items():
    parts=sorted((p for p in placements if p['voiceId']==sid),key=lambda p:p['sourceStartSample'])
    pos=0;last_output=-1
    for p in parts:
        assert p['sourceStartSample']==pos and p['startSample']>last_output
        pos=p['sourceEndSampleExclusive'];last_output=p['endSampleExclusive']-1
    assert pos==r['samples']
    coverage.append(dict(id=sid,samples=pos,exactCoverage=True,repeatedSamples=0,removedSamples=0))
last=120*400
for p in sorted(placements,key=lambda p:p['startSample']):
    assert p['startSample']>=last, (p['id'],last,p['startSample'])
    assert p['endSampleExclusive']<=member_start*400
    last=p['endSampleExclusive']
for cid,c in cuts.items():
    pieces=sorted([s for s in segments if s.get('sourceBankCutId')==cid],key=lambda s:s['sourceStartFrame'])
    pos=c['startFrame']
    for s in pieces:
        assert s['sourceStartFrame']==pos;pos=s['sourceEndFrameExclusive']
    assert pos==c['endFrameExclusive']
plan=dict(schemaVersion=7,preparedAt=datetime.now(timezone.utc).isoformat(),slug='presenting-game-scores',
    currentVoiceSelection=rel(selectionp),currentVoiceSelectionSha256=sha(selectionp),
    bank=rel(bankp),bankSha256=sha(bankp),fps=60,width=1920,height=1080,timebase='1/90000',ptsStep=1500,
    narrationSampleRate=24000,narrationSamples=selection['narrationSamples'],currentPcmSeconds=selection['currentPcmSeconds'],
    originalParagraphsPreserved=30,currentParagraphs=39,currentNarratives=19,
    introFrames=120,memberFrames=600,bodyFrames=18332,actualFrames=10999,explanationFrames=7333,
    finalFrames=19052,durationSeconds=19052/60,bodyRatioFrameError=10999-18332*.6,
    segments=segments,chapters=chapters,voicePlacements=placements,paragraphBoundaries=boundaries,
    completeSentence06BoundarySample=split06,quietBoundaryInspection=quiet_rows,exactPcmCoverage=coverage,
    allOriginalAndSelectedSamplesRetained=True,speechTrimmed=False,sourceAudio=False,loop=False,slowdown=False,
    numericObservationPolicy='Show exact native normal-speed observed frame first; explain separate snapshots on black diagrams. Resume later live action to show that the lead changes.',
    stillFramesCountedAsActual=False,standardFpsConversionNotLoop=True,captionStyle='boxed-white-forest-v1',
    captionCenterPx=[960,970],captionMaxLines=2,balatroCaptionMaxLines=1,
    candidateMeasuredTimingPrepared=True,mathRatioVerified=True,finalTimingApproved=False,
    allInputSegmentCaptionPixelsReviewed=False,allFinalPixels=False,finalMixedAsrApproved=False,
    pairRendered=False,qaApproved=False,collected=False,privateUploaded=False,actualId=None,
    humanListening='pending',humanPronunciation='pending',publicRights='pending',
    finalPlanAdopted=False,preparedOnly=True,newImagesGitAdded=0)
save(destination,plan)
save(BASE/'measured-timeline-direct-editorial-review-v7.json',dict(schemaVersion=1,reviewedAt=plan['preparedAt'],
    plan=rel(destination),planSha256=sha(destination),all39KoEnParagraphsRetained=True,
    all11NativeSourceIntervalsUnique=True,sourceNumericMomentsReadAgainstSealedBank=True,
    both2920And141ShownAsDifferentObservedMoments=True,balatroShortsNotTreatedAsContinuousRun=True,
    guide12EndsAtEqualityObservationSeconds=23.280041666666666,exactEqualityNativeFrame=2057,
    explanationFrames=7333,actualFrames=10999,bodyRatioFrameError=plan['bodyRatioFrameError'],
    currentPcmSeconds=selection['currentPcmSeconds'],allPcmSamplesCoveredExactly=True,
    approvalScope='Measured editorial candidate only; final caption/UI and motion render pixels required before adoption',
    finalTimingApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,preparedOnly=True))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=plan['preparedAt'],
    stage='measured-current19-candidate-native-and-black-inputs-pending',ownedJob=None,
    measuredCandidate=rel(destination),nextAction='Build singleCPU2 normal-speed native inputs and measured independent black MC; review every selected caption/UI/motion frame before final plan adoption/mix.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
    item.update(stage=cp['stage'],currentExecution=None,measuredCandidate=rel(destination),nextAction=cp['nextAction'])
    q['updatedAt']=plan['preparedAt'];q['lastProgressAt']=plan['preparedAt']
    if qp.read_text('utf-8-sig')==raw:save(qp,q);break
else:raise RuntimeError('Concurrent queue change; preserve foreign work.')
print(json.dumps(dict(actualFrames=actual_frames,explanationFrames=black_frames,bodyFrames=18332,
    finalFrames=19052,seconds=19052/60,currentPcmSeconds=selection['currentPcmSeconds'],preparedOnly=True)))
