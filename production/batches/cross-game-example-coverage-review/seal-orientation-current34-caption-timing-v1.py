"""Bind the directly read44 added cue timings to current AAC and retained200 cues."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'current34-caption-timing-direct-review-v1.json'
ap=O/'current34-caption-alignment-v1.json'
assert not out.exists()
raw=ap.read_bytes(); alignment=read(ap)
review=read(O/'current34-mixed-complete-direct-review-v1.json')
mix=read(O/'current34-mix-execution-v2.json')
plan=read(O/'current34-measured-timing-plan-v1.json')
base=read(ROOT/plan['sourceBaselineTimeline'])
groups=read(O/'current34-caption-editorial-groups-v1.json')['groups']
contexts={x['id']:x for x in read(O/'current34-mixed-independent-context-plan-v1.json')['contexts']}
assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared']
assert review['currentMixedPlacementAndContentReviewPassed']
assert alignment['mixAacSha256']==mix['mixAacSha256']==sha(ROOT/mix['mixAac'])
assert alignment['planSha256']==sha(O/'current34-measured-timing-plan-v1.json')
assert not alignment['allNewCueTimingDirectlyReviewed']
scenes={s['id']:s for s in plan['scenes']}
oldscenes={s['id']:s for s in base['scenes']}
new=[]; retained=0
for row in alignment['entries']:
    if not row.get('newCue'):
        i=row['retainedCue']-1;k=base['koCaptions'][i];e=base['enCaptions'][i]
        shift=scenes[k['scene']]['frameIn']/60-oldscenes[k['scene']]['start']
        assert row['lines']==k['text'].split('\n') and row['ko']==k['text'].replace('\n',' ')
        assert row['en']==e['text']
        assert abs(row['start']-k['start']-shift)<1e-7 and abs(row['end']-k['end']-shift)<1e-7
        retained+=1;continue
    match=[g for g in groups if g['scene']==row['scene'] and g['paragraph']==row['paragraph'] and g['ko']==row['ko']]
    assert len(match)==1 and row['en']==match[0]['en'] and row['lines']==match[0]['lines']
    result_path=ROOT/row['currentContextResult'];result=read(result_path)
    context=contexts[result['id']]
    assert sha(result_path)==row['currentContextResultSha256']
    assert result['sourceSha256']==mix['decodedAacSha256'] and result['exactSourceStereoPcmBytesMatched']
    assert not context['expectedWasRecognizerPrompt']
    assert context['coreStartSample']/48000<=row['start']<row['end']<=context['coreEndSample']/48000
    windows=sorted((x['destinationStartSample']/24000,x['destinationEndSample']/24000)
        for x in mix['placements'] if x['scene']==row['scene'])
    gaps=[(left,right) for (_,left),(right,_) in zip(windows,windows[1:]) if right-left>=.5]
    for left,right in gaps:
        assert not left+1/60<row['start']<right-1/60, (row['id'],'caption starts inside observation silence')
    for gap in row['knownObservationQuietGapsExcluded']:
        assert any(abs(gap['start']-left)<1e-7 and abs(gap['end']-right)<1e-7 for left,right in gaps)
        assert abs(row['start']-gap['end'])<1e-7
    row['finalCueTimingDirectlyReviewed']=True
    new.append(dict(cue=row['id'],scene=row['scene'],paragraph=row['paragraph'],ko=row['ko'],en=row['en'],
        start=row['start'],end=row['end'],contextResultSha256=sha(result_path),
        observationGapsExcluded=row['knownObservationQuietGapsExcluded'],
        completeTextAndTimingDirectlyRead=True,readEvidence='f4bbcd;15e35f(first37);79018e(last7)',
        finalPixelsReviewed=False))
assert retained==200 and len(new)==44
assert len({(x['scene'],x['paragraph']) for x in new})==40
alignment['allNewCueTimingDirectlyReviewed']=True
alignment['timingDirectReview']=out.relative_to(ROOT).as_posix()
alignment['timingReviewScope']='Current independent AAC word boundaries constrained by exact original PCM placement and observation quiet gaps; human pronunciation and final caption pixels remain pending.'
assert ap.read_bytes()==raw
tmp=ap.with_name(ap.name+'.timing-review-writing')
tmp.write_text(json.dumps(alignment,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,ap)
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    preparedAlignmentSha256=hashlib.sha256(raw).hexdigest(),reviewedAlignmentSha256=sha(ap),
    currentMixedReviewSha256=sha(O/'current34-mixed-complete-direct-review-v1.json'),
    mixAacSha256=mix['mixAacSha256'],retained200TextWrapRelativeTimingPreserved=True,
    all44NewCueTimingDirectlyReviewed=True,rows=new,
    quietGapCorrection={'cue':75,'scene':'07b','proposedStart':343.22166666666664,'actualStart':346.18833333333333,
        'basis':'Exact next voice placement after5.933333second observation silence; recognizer first word spans that silence.'},
    humanListeningApproved=False,humanPronunciationApproved=False,allFinalCuePixelsReviewed=False,
    newTts=0,newAsr=0,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(retained=200,added=44,timingDirectlyReviewed=True,finalPixels=False)))
