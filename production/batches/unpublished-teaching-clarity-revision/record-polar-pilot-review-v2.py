"""Seal actual v2 exits and bounded encoded-pixel/playback observations."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def verified(rows):
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in rows)
    return rows
now=datetime.now(timezone.utc).isoformat()
s=read('scene02-moving-pilot-execution-v2.json')
assert s['status']=='completed' and s['exitCode']==0
assert s['pid']==33356 and len(s['samples'])==304 and len(s['boards'])==51
assert all(s[k]==0 for k in ['sourceDecodeExitCode','annotationEncodeExitCode','captionEncodeExitCode','extractionExitCode'])
for k in ['scene02.annotated.clean','scene02.annotated.captioned']:
    assert s[k]['wholeDecodeExitCode']==0 and s[k]['allPts1500Verified']
    assert sha(ROOT/s[k]['path'])==s[k]['sha256']
observations=[]
for label in ['first','second','third']:
    p=OUT/f'pilot-v2-playback-{label}-end.ax.txt'
    text=p.read_text(encoding='utf-8')
    match=re.search(r'- generic: (".*")',text)
    assert match
    v=json.loads(json.loads(match.group(1)))
    assert v['paused'] and v['playbackRate']==1 and v['muted'] is False
    observations.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'visibleState':v})
assert len(observations[-1]['visibleState']['events'])==6
proof={'reviewedAt':now,'sessionId':84633,'actualOuterExitCode':0,
    'actualExitObservedChunk':'a63286','executionStateSha256':sha(OUT/'scene02-moving-pilot-execution-v2.json'),
    'all304EncodedSamplesDirectlyRead':verified(s['samples']),
    'all51BoardsDirectlyRead':verified(s['boards']),
    'sampledCaptionAndUiLayoutApproved':True,
    'sampledObservationBracketsApproved':True,
    'reviewNotes':[
        'Score and speed remain above fixed captions after cropping the irrelevant top180px. Original two-line source CC remains at628/654px.',
        'Red horizontal and green height components begin at the narrated ground/air cue3.35s, alongside the visible jump; blue diagonal is explicitly an illustrative component diagram.',
        '15s camera icon/arrow identifies the viewing relationship;22.72s cylinder/sphere preview follows existing narration;29.08s separates distance,height,viewpoint.',
        '34.783s shot shows ramp,air and later landing rather than implying a landing at the first frame.42.5s image-center guide is labelled screen-space.',
        'Different source runs are announced at all three cuts. Brackets identify the rider as an attention region; they are not recovered world coordinates or precise helmet motion.'],
    'normalSpeedBrowserPlaybackObservations':observations,
    'playbackLimit':'Three normal1x intervals actually started and reached their ends. Endpoint UI/screenshots plus304 encoded samples were directly read. This is not a claim that every intervening frame or continuous human listening was approved. Browser auto-pause overshoot is not an exact source cut.',
    'allContinuousFramesDirectlyReviewed':False,'humanListeningApproved':False,
    'pilotBoundedReviewPassed':True,'wholeVideoApproved':False,
    'allFinalPixelsApproved':False,'currentWholeMixedAsrApproved':False,
    'protectedBaselineUnchanged':all(sha(ROOT/r['path'])==r['sha256'] for r in read('baseline-protected-sha-v1.json')['files']),
    'researchManipulation':False,'newUpload':False,'newSchedule':False,'gitDelivered':False}
p=OUT/'scene02-pilot-direct-review-v2.json';assert not p.exists()
p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qp=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=json.loads(qp.read_text(encoding='utf-8'))
assert q['execution']['heavyJob']['sessionId']==84633
q['execution']['completedJobs'].append({'sessionId':84633,'pid':33356,'createTime':s['createTime'],
    'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/scene02-moving-pilot-execution-v2.json',
    'actualOuterExitCode':0,'exitObservedChunk':'a63286','sampledPixelApproval':True,'wholeVideoApproval':False})
q['execution'].update(stage='polar-first-gameplay-pilot-v2-bounded-review-complete',heavyJob=None,
    next='Prepare six remaining narrated gameplay annotations; exclude scene08 unrelated team-unlock UI, preserve19PCM/206KOEN/timing; then current whole audio/pair/QA/collect/private/Git/schedule.')
q['updatedAt']=now
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actualExit':0,'samplePixels':304,'boards':51,'browserIntervals':3,'wholeVideoApproved':False}),flush=True)
