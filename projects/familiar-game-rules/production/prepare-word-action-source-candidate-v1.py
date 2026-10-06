"""Unique natural-speed source intervals for the measured70paragraph candidate.

This is an editable proposal. New internal boundaries, every literal caption,
motion and the final encoded pixels are separate approval gates.
"""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
plan_path=BASE/'measured-word-timing-candidate-v2.json';plan=read(plan_path)
caption_path=BASE/'word-caption-candidate-v2/captions.json';captions=read(caption_path)
assert captions['planSha256']==sha(plan_path)
bank_path=PROOF/'source-action-bank-v4.json';bank=read(bank_path)
sources={c['sourceVideoId']:dict(path=c['sourcePath'],sha256=c['sourceSha256'],fps=c['sourceFrameRate']) for c in bank['clips']}
A='7kJo0miz08g';F='FVkDc6u_4GQ';X='XbW4873OPZo';Q='q8iWixSvfsI';Z='zdq39c6G9GY';B='BWjN5ZX27kg';C='zxzPcsI8l2o';P='YIVtT7SJrMM';H='q-AsYZCdpts'
# IDs for the two original Gunbrella sources are obtained from the current
# bank instead of guessing a remembered YouTube identifier.
Z=next(c['sourceVideoId'] for c in bank['clips'] if c['id']=='action-12')
B=next(c['sourceVideoId'] for c in bank['clips'] if c['id']=='action-20')
specs={
 '02-part1':[(F,330,480,150),(A,2430,2550,120),(F,562,690,128),(A,3120,3270,150),(A,2864,3000,136)],
 '12':[(A,2300,2356,56),(F,480,562,82),(F,1164,1362,198),(F,960,1152,192)],
 '02-part2':[(A,2730,2864,134),(A,3000,3090,90),(A,3360,3600,240),(A,3600,3821,221),(F,870,960,90)],
 '04-part1':[(A,3821,3900,79),(A,4110,4170,60),(A,4200,4410,210),(F,1410,1591,181),(X,1320,1471,151),(F,1680,1740,60)],
 '13':[(F,180,270,90),(F,690,870,180),(F,1830,2055,225)],
 '04-part2':[(X,1650,1891,241),(X,2070,2244,174),(X,2640,2791,151),(A,3930,4080,150),(F,2055,2100,45),(F,1362,1410,48),(A,2356,2400,44)],
 '06-part1':[(B,1950,2100,150),(Q,1110,1170,60),(Z,1581,1726,145)],
 '14':[(Q,1170,1290,120),(Q,1290,1440,150),(Z,270,504,234)],
 '06-part2':[(Z,1860,1980,120),(Z,2010,2100,90),(B,1470,1620,150),(Z,2670,2761,91)],
 '15':[(C,240,266,52),(C,300,320,40),(C,1740,1752,24),(C,1770,1830,120),
       (C,266,300,68),(C,320,360,80),(C,1752,1770,36),(Z,1410,1581,171)],
 '06-part3':[(Z,1726,1830,104),(Z,2130,2250,120),(Z,2400,2670,270),(B,2130,2550,420),
             (Z,2761,2850,89),(Z,3000,3118,118),(B,3480,3570,90)],
 '08-part1':[(P,660,810,150),(P,1500,1680,180),(H,1160,1229,69)],
 '16':[(H,540,1160,620)],
 '08-part2':[(P,930,1002,72),(P,1170,1500,330),(P,3060,3300,240),(P,1002,1140,138),(H,1980,2083,103)],
 '17':[(H,1350,1790,440)],
 '08-part3':[(P,1980,2190,210),(P,2220,2400,180),(P,2490,2760,270),(P,2790,2926,136),(H,2808,2940,132)],
 '10-part1':[(P,4380,5580,1200)],
 '18':[(H,2256,2808,552)],
 '10-part2':[(P,5580,6011,431)],
 '19':[(H,2940,3270,330),(H,1790,1980,190),(H,1260,1340,80)],
 '10-part3':[(P,6011,6372,361),(H,2083,2191,108)],
}
notes={
 '02-part1':'Kick/window aim first, then corridor firing; ceiling and stair targets coincide with the second paragraph’s higher-direction focus.',
 '12':'Two separate pink-room excerpts, then a separate dark stairway shot and an escalator/height comparison. Verify the old trailer’s internal pink/sewer boundary before adoption.',
 '02-part2':'Separate close attacks and crossbow/kick actions illustrate the action grammar. They prove no exact key sequence or optimal strategy.',
 '04-part1':'Bathroom/pizza/plunger/red-room and door kicks show approaching/close action while facing targets; separate trailer shots remain identified.',
 '13':'One door-kick excerpt3–4.5s (follow-through included), then a separate purple-room aim and furniture/high target excerpt.4.5–5.5s unengaged corridor walking is excluded.',
 '04-part2':'Air/roof, flaming hallway/lobby and disco/upper-room targets illustrate new-action combination, followed by explicitly separate trailer cuts.',
 '06-part1':'Launcher jump first, then street firing and airborne umbrella/direction. These visible actions establish functions without asserting keys.',
 '14':'Market firing/jump at19.5195–21.5215, wire/umbrella at21.5215–24.024, then moving umbrella; the final sentence belongs to the independent tool/function explanation.',
 '06-part2':'Vertical rise, upward aim and ceiling turret provide the airborne/high-target comparison. A distinct boss-air dodge supports multiple tool functions.',
 '15':'Rail→market→swamp→container settings are cut at their spoken list anchors, followed by unused distinct rail/wall/swamp samples and airborne umbrella. The brief setting labels require motion/readability review.',
 '06-part3':'Separate lower firing/umbrella approach, boss/room route, junkyard travel, beast projectiles and turret traverse support functions/combination limitations. Lower targets are not approved under captions.',
 '08-part1':'Descending/sideways travel with separate gun direction, wall jump and a distinct train/crate shot; no supported-device inference.',
 '16':'Train9–19.333333: spoken floor-target anchors coincide with12–14s; crate-height anchors coincide with14–16s. Preserve literal low-target pixels.',
 '08-part2':'Barrel first until1.2s, then zipline/hanging excerpt during줄에매달리는. Two-level aim begins before두총이서로다른쪽, then unused barrel/crate action. Every aim anchor needs native review.',
 '17':'Train22.5–29.833333: the spoken opposite-guns1.68–2.54s reaches source24.18–25.04s. Last design sentence is white explanation.',
 '08-part3':'Inverted hang, swing/upward aim, glass fall and train/boss/spin preserve move-versus-target functions without asserting device support.',
 '10-part1':'Original same-source73–93s continuous multi-floor traversal retains the first3original paragraphs. Keep central lower opponents clear of the fixed box.',
 '18':'Train37.6–46.8s: spoken총은아래1.34–2.96s reaches38.94–40.56s actual downward guns.33–36s upward crate aim was rejected for this sentence.',
 '10-part2':'Resume the original source cursor93–100.183333s after an explicitly different train observation; original PCM stays byte exact.',
 '19':'Train49–54.5s spin→roof→car first, followed by distinct unused train sections during the new-route implication.51s rooftop walking alone is not called downward aim.',
 '10-part3':'Resume100.183333–106.2s, stopping before lift/logo; a distinct active crate sequence accompanies the new-route design implication. No repeated source interval.',
}
all_cuts=[]
for piece in plan['pieces']:
    actual=next((r for r in piece['roleSegments'] if r['role']=='actual-existing-game'),None)
    if not actual:
        piece['explanationPreserved']=True;continue
    cursor=actual['startFrame'];cuts=[]
    for i,(vid,a,z,frames) in enumerate(specs[piece['id']],1):
        meta=sources[vid];fps=Fraction(meta['fps'])
        source_seconds=float(Fraction(z-a,1)/fps)
        assert abs(source_seconds*60-frames)<=1, (piece['id'],vid,a,z,frames,source_seconds)
        covered=[c for c in bank['clips'] if c['sourceVideoId']==vid and c['inFrameInclusive']<z and c['outFrameExclusive']>a]
        intervals=sorted((max(a,c['inFrameInclusive']),min(z,c['outFrameExclusive'])) for c in covered)
        bank_frames=set(n for aa,zz in intervals for n in range(aa,zz))
        uncovered=[n for n in range(a,z) if n not in bank_frames]
        cut=dict(id=piece['id']+f'-cut{i:02}',pieceId=piece['id'],logicalScene=piece['logicalScene'],sourceVideoId=vid,
            sourcePath=meta['path'],sourceSha256=meta['sha256'],sourceFrameRate=meta['fps'],inFrameInclusive=a,outFrameExclusive=z,
            inSeconds=float(Fraction(a,1)/fps),outSeconds=float(Fraction(z,1)/fps),sourceIntervalSeconds=source_seconds,
            startFrame=cursor,endFrame=cursor+frames,durationFrames=frames,classification='actual-existing-game',
            sourceCrop=[0,0,1920,1080],framingMode='native-full-frame-candidate',sourceAudio=False,loop=False,editorSlowdown=False,
            naturalRateResampling='Normal source speed into60fps; fractional native-frame rounding bounded to1timeline frame per excerpt.',
            bankCutIds=[c['id'] for c in covered],previouslyBankedSourceFrames=z-a-len(uncovered),newSourceBoundaryFrames=len(uncovered),
            sourceAndCaptionPixelsReviewed=False,completeMotionReviewed=False,exactNewEdgesApproved=False,
            wordActionAlignmentApproved=False,visibleActionConnection=notes[piece['id']])
        cuts.append(cut);all_cuts.append(cut);cursor+=frames
    assert cursor==actual['endFrame'], (piece['id'],cursor,actual['endFrame'])
    piece.update(selectedSourceCuts=cuts,sourcePixelsReviewed=False,captionPixelsReviewed=False)
# Exact source-frame intervals are never repeated, including adjacent split
# excerpts used in separate logical scenes.
for vid in sources:
    rows=sorted((c for c in all_cuts if c['sourceVideoId']==vid),key=lambda c:c['inFrameInclusive'])
    for a,z in zip(rows,rows[1:]):assert a['outFrameExclusive']<=z['inFrameInclusive'],(a['id'],z['id'])
for p in captions['paragraphs']:
    a=math.floor(p['startSeconds']*60);z=math.ceil(p['endSeconds']*60)
    p['proposedSourceCutIds']=[c['id'] for c in all_cuts if c['startFrame']<z and c['endFrame']>a]
    p['visibleActionConnection']=notes.get(p['pieceId'],'Independent original white2.5D explanation; preserve every claim/PCM and duration.')
    p['meaningActionAligned']=False
for c in captions['ko']:
    a=math.floor(c['startSeconds']*60);z=math.ceil(c['endSeconds']*60)
    c.update(proposedSourceCutIds=[s['id'] for s in all_cuts if s['startFrame']<z and s['endFrame']>a],
        cutBoundaryInsideCue=[s['startFrame'] for s in all_cuts if a<s['startFrame']<z],timingApproved=False,pixelsApproved=False)
dest=BASE/'word-action-source-candidate-v1.json';assert not dest.exists()
plan.update(preparedAt=datetime.now(timezone.utc).isoformat(),status='all21actual-pieces-proposed-with-unique-word-related-cuts; native/literal/motion pending',
    timingCandidate=rel(plan_path),timingCandidateSha256=sha(plan_path),captionCandidate=rel(caption_path),captionCandidateSha256=sha(caption_path),
    sourceBank=rel(bank_path),sourceBankSha256=sha(bank_path),sourceCutCount=len(all_cuts),allUniqueSourceFrameIntervals=True,
    paragraphs=sorted(captions['paragraphs'],key=lambda p:p['startSeconds']),ko= captions['ko'],en=captions['en'],
    all70LiteralParagraphsPreserved=True,original11PcmPreserved=True,originalSixWhiteSecondsPreserved=147.2,
    captionCenter=[960,970],captionFontPx=48,allKoSingleLine=True,maxKoTextWidthPx=620,
    excludedSourceIntervals=[dict(sourceVideoId=F,inFrameInclusive=270,outFrameExclusive=330,reason='4.5–5.5s unengaged corridor walking is excluded. Door-kick3–4.5 includes only brief visible follow-through.')],
    unresolved=['Guide12 old trailer pink/sewer internal boundary','Guide15 brief setting-label readability',
     'Original06 lower enemies at action13/action23','Original10 central lower-floor enemies',
     'All new internalcut edges, all250literal cues and meaningful motion','Every independent white scene and final mix/encoded pixels'],
    allSourceSegmentPixelsReviewed=False,allDiagramPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,
    finalWordActionAlignment=False,finalTimingApproved=False,bodyRatioApproved=False,finalTimelineAdopted=False,newGitImages=0,
    scope='Editable source/cue proposal only. Natural-speed actual related actions, no duplicated interval/loop/slowdown/sourceaudio; complete input and final QA still required.')
dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualPieces=len(specs),uniqueCuts=len(all_cuts),paragraphs=70,koCues=250,enCues=118,
    currentSpeechSeconds=plan['allSpeechSeconds'],candidateFinalFrames=plan['finalFrameBudget'],allApprovals=False)))
