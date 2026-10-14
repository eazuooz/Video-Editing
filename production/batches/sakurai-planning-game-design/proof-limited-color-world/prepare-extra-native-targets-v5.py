"""Prepare a distinct missing-PTS worker; do not repeat completed v4 extraction."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
out=P/'review-extra-native-targets-v5.py'
assert not out.exists()
cuts=[
 dict(key='room-door-clean-end',source='chicory-b-roll-1',startFrame=5940,endFrameExclusive=6090,candidateSeconds=2.5,framingUpPixels=0,endpointsOnly=True,provisionalInsertion='generic-outline-check',caveat='Revised end excludes observed wipe; preserve v4 interior review.'),
 dict(key='corridor-moving-clean-end',source='chicory-b-roll-1',startFrame=6480,endFrameExclusive=6630,candidateSeconds=2.5,framingUpPixels=0,endpointsOnly=True,provisionalInsertion='generic-outline-check',caveat='Remove final half-second stand. Explicit corridor label; not house painting.'),
 dict(key='mushroom-arrival-moving-only',source='chicory-b-roll-2',startFrame=6660,endFrameExclusive=6690,candidateSeconds=.5,framingUpPixels=0,endpointsOnly=True,provisionalInsertion='04-height-and-motion',caveat='Brief exit movement; prior110–111 stationary portion excluded.'),
 dict(key='tree-outline-step-away',source='chicory-b-roll-1',startFrame=35880,endFrameExclusive=35970,candidateSeconds=1.5,framingUpPixels=0,provisionalInsertion='07b-cues-to-check',caveat='After already reviewed paint/erase/repaint, player walks beside tree. Exclude later collectible603s; name tree and only generic outline claim.'),
 dict(key='mushroom-erase-shrink-and-return',source='chicory-b-roll-2',startFrame=1620,endFrameExclusive=1770,candidateSeconds=2.5,framingUpPixels=0,provisionalInsertion='04-height-and-motion',caveat='Separate continuation after first bounce: erase/shrink and movement back. Native samples must confirm motion and no early wipe; no permanent unlock.'),
 dict(key='branch-height-change-and-climb',source='chicory-b-roll-2',startFrame=4020,endFrameExclusive=4260,candidateSeconds=4,framingUpPixels=120,provisionalInsertion='03b-static-to-state',caveat='New branch-like plant at67–71; explicitly label changed plant. Verify paint/growth and character climb. Later gift73s excluded; no medical or win claim.'),
 dict(key='flower-route-exit-before-wipe',source='chicory-b-roll-2',startFrame=5760,endFrameExclusive=5835,candidateSeconds=1.25,framingUpPixels=120,provisionalInsertion='06-route-information',caveat='Normal exit navigation after preceding flowers, before98s wipe. Keep character/path above caption; exclude stationary, unrelated or transitioning frames.')
]
for c in cuts:c.update(selected=False,sourceAdoptionApproved=False,finalCueUiApproved=False,startSeconds=c['startFrame']/60,endSeconds=c['endFrameExclusive']/60)
s=(P/'review-extra-native-actions-v4.py').read_text('utf-8')
s=s.replace("extra-native-action-execution-v4.json","extra-native-targets-execution-v5.json").replace("preflight/extra-native-actions-v4","preflight/extra-native-targets-v5")
a=s.index("editorial = read(P/'additional-action-editorial-review-v3.json')")
b=s.index('protected_paths =',a)
s=s[:a]+"assert read(P/'extra-native-action-direct-review-v4.json')['all27BoardsAnd134SamplesDirectlyRead']\ncuts = "+repr(cuts)+"\nassert sum(c['candidateSeconds'] for c in cuts) == 14.75\n"+s[b:]
s=s.replace('candidateSeconds=37,planCuts=cuts','candidateSeconds=14.75,planCuts=cuts')
s=s.replace("trimmed = read(P/'chicory-trimmed-framing-execution-v2.json')","trimmed = read(P/'chicory-trimmed-framing-execution-v2.json')\n    extra = read(P/'extra-native-action-execution-v4.json')\n    assert extra['actualExitObserved'] and extra['actualOuterExitCode']==0")
s=s.replace('for d in [prior,trimmed]:','for d in [prior,trimmed,extra]:')
s=s.replace('wanted.update(range(a,b,30)); wanted.update([a-1,a,a+1,b-1,b,b+1])',"wanted.update([] if c.get('endpointsOnly') else range(a,b,30)); wanted.update([a-1,a,a+1,b-1,b,b+1])")
s=s.replace('indices=sorted(set(range(a,b,30))|{a-1,a,a+1,b-1,b,b+1});samples=[]',"indices=sorted(set([] if c.get('endpointsOnly') else range(a,b,30))|{a-1,a,a+1,b-1,b,b+1});samples=[]")
# Avoid rewriting the exact v4 placeholder at a previously reviewed frame.
s=s.replace("fp=sub/f'f{n:06d}-caption-test.png';framed.save(fp)","old_caption=next((x for oldc in extra['cuts'] if oldc['source']==c['source'] and oldc['framingUpPixels']==up for x in oldc['samples'] if x['nativeFrame']==n),None)\n            if old_caption:\n                fp=ROOT/old_caption['captionTestPath'];assert sha(fp)==old_caption['captionTestSha256']\n            else:\n                fp=sub/f'f{n:06d}-caption-test.png';framed.save(fp)")
s=s.replace("'new-extra-native-actions-'","'new-extra-native-targets-'")
s=s.replace('Observe actual exit; directly read all new candidate/boundary/caption samples. Original8 PCM and completed ASR remain sealed. Adopt only useful source actions, then measure additive causal bridges and exact body60:40; no menu/loop/slowdown filler.', 'Observe actual v5 exit and read only revised endpoints/new plant-action pixels. Reuse v4 interiors. Preserve original8PCM/32ASR and foreign lease. Measure3bridges after sufficient unique matched footage is secured; final gates remain false.')
out.write_text(s,'utf-8')
compile(s,str(out),'exec')
print(json.dumps(dict(prepared=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),candidateSeconds=14.75,newActionCandidateSeconds=9.25,running=False)))
