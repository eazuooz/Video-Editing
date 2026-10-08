"""Plan visible roles for preserved PCM; source intervals and approval stay pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
path=BASE.parent/'planning/current16-paragraph-roles-v2.json'
assert not path.exists(), 'Preserve existing role candidate.'
tp=BASE/'current16-voice-timing-candidate-v1.json';t=read(tp)
kp=BASE.parent/'script/narration.ko.v3.json';ep=BASE.parent/'script/narration.en.v2.json'
k,e=read(kp)['scenes'],read(ep)['scenes'];assert len(k)==len(e)==len(t['rows'])==16
white_ranges={
 '01-overview':[(0,1325)], '02-visible-effects':[(782,1608)],
 '03-readable-outcome':[(731,1796)], '04-situations':[(705,1680)],
 '05-manageable-choice':[(0,1676)],'06-quick-trial':[(454,1834)],
 '07-expression':[(0,1748)],'08-conclusion':[(0,1772)],
 '11-jade-ground-and-height-guide':[(439,682),(1340,2717)],
 '15-task-and-result-guide':[(270,658)],
 '16-action-versus-expression-guide':[(1383,2736)]}
named={
 ('02-visible-effects',1):'Gauss path and visible enemy reaction',
 ('02-visible-effects',2):'Gauss ground-circle/caster relation',
 ('09-path-and-projectile-guide',1):'Gauss dash starting position/path/target reaction',
 ('09-path-and-projectile-guide',2):'Gauss attack/ground spread; generic choice question at the end',
 ('09-path-and-projectile-guide',3):'Dante aimed forward projectile and visible target',
 ('03-readable-outcome',1):'Jade ground effect, overhead mark and target reaction',
 ('03-readable-outcome',2):'Jade origin/affected-target connection; may interleave ground and aerial target views',
 ('11-jade-ground-and-height-guide',1):'Jade first7.316667seconds ground caster/light/nearby foes; projected relation follows',
 ('11-jade-ground-and-height-guide',2):'Jade above the ground, aiming downward at visible targets',
 ('04-situations',2):'Yareli moving caster-centred rotating effect and nearby targets',
 ('12-nearby-space-guide',1):'Yareli ring/caster/nearby targets',
 ('12-nearby-space-guide',2):'Yareli passing/turning beside visible targets',
 ('12-nearby-space-guide',3):'Dante round effect and forward targets; not world orb or triangle',
 ('13-doorway-comparison-guide',1):'Dante door, visible targets and effect direction',
 ('13-doorway-comparison-guide',2):'Dante different caster/target/camera angles',
 ('14-purpose-before-options-guide',1):'Dante near-space versus forward-target actions',
 ('14-purpose-before-options-guide',2):'Dante arm raise then forward projectile',
 ('14-purpose-before-options-guide',3):'Dante first actual-target clause; generic caveat can use matching other actions',
 ('06-quick-trial',1):'Jade unique approach/progress/completion/ally moving sequence',
 ('15-task-and-result-guide',1):'Jade unused approach4.5seconds; projected recovery/task relation follows',
 ('15-task-and-result-guide',2):'Dante forward attack origin and target',
 ('16-action-versus-expression-guide',2):'Yareli near space, then Jade airborne aiming downward; general comparison tail may use other matching actions'}
paras=[];white=actual=0
for sc,eng,row in zip(k,e,t['rows']):
    assert sc['id']==eng['id']==row['id'] and len(sc['lines'])==len(eng['lines'])==4
    starts=[round(n/400) for n in row['paragraphStartSamples']]+[row['frames']]
    for ix,(ko,en,a,b) in enumerate(zip(sc['lines'],eng['lines'],starts,starts[1:]),1):
        boundaries=sorted({a,b,*[max(a,min(b,n)) for pair in white_ranges.get(row['id'],[]) for n in pair]})
        spans=[]
        for left,right in zip(boundaries,boundaries[1:]):
            is_white=any(x<=left and right<=y for x,y in white_ranges.get(row['id'],[]))
            role='explanation' if is_white else 'actual-game-candidate'
            white+=right-left if is_white else 0;actual+=0 if is_white else right-left
            spans.append(dict(startFrame=left,endFrame=right,frames=right-left,role=role,sourceInterval=None,sourceMatched=False))
        paras.append(dict(scene=row['id'],paragraph=ix,ko=ko,en=en,sceneLocalStartFrame=a,sceneLocalEndFrame=b,
            pcmSourceStartSample=row['paragraphStartSamples'][ix-1],pcmSourceEndSample=row['paragraphStartSamples'][ix] if ix<4 else row['samples'],
            allPcmSamplesRetained=True,spans=spans,sourceRequirement=named.get((row['id'],ix),'Relevant visible action/position/target relation; no claim of unseen configuration effects') if any(s['role']=='actual-game-candidate' for s in spans) else 'Retained narration-timed projected white explanation',
            sourceActionAligned=False,cropAndCaptionPixelsReviewed=False))
assert white==14128 and actual==21193 and white+actual==t['bodyFrames']==35321
assert sum(p['pcmSourceEndSample']-p['pcmSourceStartSample'] for p in paras)==t['wholePcmSamples']==14125441
record=dict(schemaVersion=2,slug='player-customization',preparedAt=datetime.now(timezone.utc).isoformat(),
    status='paragraph-role-candidate-only-unique-source-allocation-pending',
    inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [tp,kp,ep]],
    paragraphs=paras,paragraphCount=64,bodyFrames=35321,actualFramesCandidate=actual,explanationFramesCandidate=white,
    finalFramesCandidate=36041,bodyRatioRoundingErrorFrames=.4,
    originalWhiteFramesPreserved=10767,additionalGuideWhiteFrames=3361,
    bridgeReasons=[
        '11p3 and p4 retain projected height, aiming and the performance-inference caveat together; never substitute below-to-above Yareli aiming for airborne Jade.',
        '11p1 switches after actual caster/ground/nearby-target observation to its projected relationship. Cut439 is a visible-role candidate and needs final cue/motion review.',
        '15p1 changes at its complete second-sentence onset4.5seconds into a task/recovery diagram; earlier revival source seconds are not repeated.',
        '16p3/4 keep the entire action-versus-expression explanation, preview and trial transition.16p2 remains an actual-role candidate needing a genuinely overhead Jade shot.'],
    capacityConstraints=[
        'Jade ground and aerial capacity must be allocated separately; the combined50.8second upper pool alone is insufficient proof of matching.',
        'Allocate03p2 across ground/aerial target views if needed, without consuming the longer11p2 downward-aim demonstration.',
        'New Gauss129 source is still acquiring; no acquired or source-matched duration is assumed.',
        'All source seconds unique; no loops, slowdown, repeated action, empty movement, presenter, menus, static callouts or notification filling.'],
    direct64KoEnTextReread=True,allCurrentPcmPreserved=True,newMedia=0,newGitImages=0,
    sourceAllocationApproved=False,finalTimingApproved=False,bodyRatioApproved=False,finalTimelineAdopted=False,allFinalPixels=False)
path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(paragraphs=64,bodyFrames=35321,actualCandidate=actual,whiteCandidate=white,currentPcmSamples=14125441,finalApproved=False)))
