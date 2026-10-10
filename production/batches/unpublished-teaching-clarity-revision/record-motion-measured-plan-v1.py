"""Record directly reviewed additive timing; keep encoded/mixed delivery gates open."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, subprocess, wave

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p, value):
    temp = p.with_name(p.name + '.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)

request = read(R/'narration-tts-request-v1.json')
for x in request['protectedInputs']:
    assert sha(ROOT/x['path']) == x['sha256'], x['path']
inventory_path = ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
inventory = read(inventory_path)
for x in inventory['inputFiles']:
    assert sha(ROOT/x['path']) == x['sha256'], 'Changed inventory: '+x['path']
assert len(inventory['existingProjects']) == 72

review = R/'current-content-studio-review-v2.json'
assert not review.exists()
related = {
    'game-math-camera-frustum': 'FOV/zoom/frustum, apparent screen size and projection calculations; camera comfort, player settings and reset choices are a different viewer question.',
    'game-math-camera-projection': 'Local/world/view/clip/NDC/viewport numerical pipeline and clipping before division, rather than interpreting motion comfort and input control.',
    'game-math-orientation-matrices': 'Direction versus full pose, basis columns, orthonormality, inverse/composition and matrix validity. Screen observation supports numerical rotation, not camera comfort choices.',
    'game-math-rotation-interpolation': 'SLERP/NLERP, shortest arc, unit values, physical time, turn history and representation conversion. No duplicated comfort/settings/reset lesson.',
    'game-math-interpolation-teaching-additions-v2': 'All28 KOEN additions read: projected red body/blue board observations lead into declared numerical rotation/representation examples; no internal game values or clinical outcomes inferred.',
    'game-math-interpolation-paths-v2': 'Full current lines mapped to directly read original and additions; all changed IP07 KOEN paragraphs directly read. Same arc versus time mapping remains the viewer question.',
    'game-math-rotation-conversions-v2': 'Full current lines mapped to directly read original and additions; changed IP04 and IP08 KOEN directly read. Atan2/hypot/trace/round trips verify a declared pose.',
    'familiar-game-rules': 'Familiar input roles and function across devices. Aim/view vocabulary overlaps, but the problem and conclusions concern learned controls, not motion comfort.',
    'limited-color-world': 'Essential meaning without hue alone, brightness/shape/boundary/pattern and visibility previews, not camera-motion/player-control design.',
    'game-math-bounds-transform-v2': 'Current full KOEN bodies read: sphere distance, component extrema, AABB overlap, transformed-box versus point-set bounds and abs(A)e. Its screen-space observations lead to declared affine calculations; no duplicated comfort/options lesson.',
    'game-math-lines-opening-retake-v4': 'All20 current KOEN retake scenes and manifest read. Connection endpoints, parameter units, perpendicular-bisector dot equation and sphere/box prerequisites differ from camera comfort/player choice.',
}
rows = []
for slug, reason in related.items():
    project = next(x for x in inventory['existingProjects'] if x['slug'] == slug)
    files = [dict(path=p, sha256=sha(ROOT/p)) for p in project['scriptPaths']+project['englishScriptPaths']]
    rows.append(dict(slug=slug, fullKoEnContentCompared=True, comparison=reason, files=files))
prior = read(ROOT/'production/batches/sakurai-planning-game-design/proof-limited-color-world/content-studio-direct-review-v2.json')
carry = []
for x in prior['relevantFullBodyReviews']:
    matched=[v for v in x['files'] if (ROOT/v['path']).exists() and sha(ROOT/v['path'])==v['sha256']]
    carry.append(dict(slug=x['slug'], unchangedReviewedFiles=matched,
                      allListedPriorFilesUnchanged=len(matched)==len(x['files']),
                      priorReview='production/batches/sakurai-planning-game-design/proof-limited-color-world/content-studio-direct-review-v2.json'))
studio=[]
for tag, video_id in [('frustum','CbX6KQ-_zsc'),('projection','c96qTnlHBVU'),('orientation','6-kP65hrZcI'),('interpolation','_SzbJR4R6OI'),('conversion','n-k7zwaSum0')]:
    p=R/f'studio-neighbor-{tag}-current-v1.ax.txt'
    assert p.exists()
    text=p.read_text('utf-8'); assert video_id in text and '저장" [disabled]' in text
    studio.append(dict(videoId=video_id,evidence=rel(p),sha256=sha(p),
                       titleAndFullDescriptionDirectlyRead=True,saveDisabled=True,publishingMutations=0,
                       observedStatus='비공개' if tag in ['interpolation','conversion'] else '예약됨'))
save(review, dict(schemaVersion=2,recordedAt=now(),inputsDigest=inventory['inputsDigest'],
    projectCount=72,inputCount=len(inventory['inputFiles']),allInputHashesMatched=True,
    changedCurrentInputBodiesReview=rel(R/'inventory-change-direct-review-v3.json'),
    fullInventoryKoEnTitlesDirectlyRead=True,allInputBodiesDirectlyRead=False,
    original24FullContentReview='projects/motion-sickness-games/production/revision-teaching-clarity-v1/duplicate-review-history-v1.json',
    unchangedRelatedPriorReviews=carry,relevantCurrentFullScriptComparisons=rows,currentStudio=studio,
    candidateViewerQuestion='How can players follow a game objective while choosing how the camera and aiming motion behave?',
    independentClaims=['Separate visible tool/aim motion from background/camera motion.',
        'Provide goal/orientation cues after a direction change.',
        'Offer player camera choices and a reversible reset; do not claim observed footage proves clinical comfort.'],
    decision='distinct',basedOnlyOnTitlesOrIdsOrEmptyExactMatches=False,
    foreignFileOrPublishingMutations=0,humanListeningApproved=False))
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason='Current72 inventory and related full KOEN claims compared. Motion comfort/player control differs from FOV/projection math, pose/interpolation/conversion, sphere/AABB/affine bounds and learned input roles. Changed input bodies and new20 KOEN retake scenes read. Full current Studio camera/pose/interpolation/conversion titles/descriptions observed. Exact scope and unchanged prior reviews: '+rel(review)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',rel(review)],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)

playback=R/'opening-overlay-pilot-playback-observation-v3.json'
assert not playback.exists()
save(playback,dict(schemaVersion=1,recordedAt=now(),tabId='55',
    url='http://127.0.0.1:9250/motion-opening-annotated-review-v3.html',
    source='shared/output/unpublished-teaching-clarity-revision/motion/opening-overlay-pilot-v3/opening.annotated.silent-pilot.mp4',
    sourceSha256='2c8cc9f51f2f9e9d9d4ee38dfdfd864087ab8f1b24e879f32a31dbacb768f637',
    actualStartObserved=dict(currentTime=0,paused=False,muted=True,playbackRate=1),
    actualEndObserved=dict(currentTime=11,paused=True,ended=True,muted=True,playbackRate=1),
    seekObservation=dict(currentTime=6.25,paused=True,readyState=4,
        pixels='Same front timber blue bracket, red nozzle/aim line and gold floor focus; source HUD remains readable.'),
    firstSeekSnapshotWasStaleEnd=True,freshSeekStateObserved=True,
    normalSpeedPlaybackStartAndEndObserved=True,everyBetweenFrameDirectlyRead=False,
    wholeContinuousListeningApproved=False,finalCuePixelsApproved=False,newImageGitAdded=0))

baseline=read(ROOT/'projects/motion-sickness-games/production/final-v1/plan.json')
ko=read(R/'script/additions.ko.json');en=read(R/'script/additions.en.json')
bank=read(R/'sources/source-action-bank-v1.json')
additions={}
for scene_id, frames, bounds in [('00a',1507,[0,89040,248160,373560,537600]),('06b',701,[0,119160,263040])]:
    q=next(x for x in request['scenes'] if x['id']==scene_id)
    path=ROOT/q['path']
    with wave.open(str(path),'rb') as w:
        count,rate,channels=w.getnframes(),w.getframerate(),w.getnchannels()
    assert rate==24000 and channels==1 and count==bounds[-1]
    paragraphs=[dict(paragraph=i+1,start=a/rate,end=b/rate) for i,(a,b) in enumerate(zip(bounds,bounds[1:]))]
    additions[scene_id]=dict(id=scene_id,title=q['title'],classification='interleaved-actual-and-explanation',
        voice=q['path'],audioSha256=sha(path),voiceSamples=count,voiceSampleRate=rate,
        voiceSeconds=count/rate,voiceFrames=round(count/rate*60),frames=frames,seconds=frames/60,
        paragraphs=paragraphs,originalPcmRegenerated=False,finalMixedVoiceApproved=False)

def source_segment(scene_id,action_id,local,frames):
    a=copy.deepcopy(next(x for x in bank['actions'] if x['id']==action_id));assert frames<=a['frames']
    a.update(id=f'{scene_id}-{action_id}',scene=scene_id,file=bank['source'],sourceSha256=bank['sourceSha256'],
        frames=frames,seconds=frames/60,sourceEndExclusiveFrame=a['sourceFirstFrame']+frames,
        sourceOut=(a['sourceFirstFrame']+frames)/60,sourceEndExclusivePts=(a['sourceFirstFrame']+frames)*256,
        localStartFrame=local,localEndFrame=local+frames,classification='actual-existing-game-action',
        continuity='Independent WIP developer excerpts; no controlled or uninterrupted comparison claimed.',
        sourceAudioUsed=False,allFinalCueAndUiPixelsApproved=False)
    return a

additions['00a']['segments']=[
    dict(id='00a-overview',classification='explanation',localStartFrame=0,localEndFrame=480,frames=480,
         purpose='Projected tool/camera/floor relationship plus actual ordered viewer question and steps; independent8s Motion Canvas scene.'),
    source_segment('00a','roundabout-tail',480,189),
    source_segment('00a','tower-unused',669,178),
    source_segment('00a','early-cleaning',847,660)]
additions['00a']['segments'][-1].update(reuseReviewedAnnotationPilot=playback.name,
    annotationPilot='shared/output/unpublished-teaching-clarity-revision/motion/opening-overlay-pilot-v3/opening.annotated.silent-pilot.mp4')
additions['00a'].update(overviewSeconds=1507/60,rawNarrationSeconds=22.4,
    observationTailFrames=163,observationTailPurpose='Continue normal-speed cleaning and compare the two marked motions after the last spoken instruction; no looping or freeze.',
    instructionStartsAtSeconds=373560/24000,markedEarlyActionStartsAtSeconds=847/60,
    sourceExcerptChangesExplicitlyLabelled=True)
additions['06b']['segments']=[source_segment('06b','continuing-cleaning',0,298),
    dict(id='06b-goal-cues',classification='explanation',localStartFrame=298,localEndFrame=701,frames=403,
         purpose='Projected walls/floor/goal introduce the immediately following Talos trailer; distinguish independent excerpts and illustrative diagram.')]
order=['00a']+[f'{i:02}' for i in range(1,7)]+['06b']+[f'{i:02}' for i in range(7,13)]
scenes=[];paragraphs=[];cuts=[];start=120
for sid in order:
    new=sid in additions
    s=copy.deepcopy(additions[sid] if new else next(x for x in baseline['scenes'] if x['id']==sid))
    old_start=s.get('startFrame');s.update(startFrame=start,start=start/60)
    if not new:
        s['baselineStartFrame']=old_start;s['retainedFramesUnchanged']=True
        for c in s.get('cuts',[]):
            c['timelineStart']=(start+c['localStartFrame'])/60;c['timelineEnd']=(start+c['localEndFrame'])/60
            c['allFinalCueAndUiPixelsApproved']=False;cuts.append(c)
    else:
        for seg in s['segments']:
            seg.update(timelineStart=(start+seg['localStartFrame'])/60,timelineEnd=(start+seg['localEndFrame'])/60)
            if seg['classification']=='actual-existing-game-action':cuts.append(seg)
    for p in s['paragraphs']:
        if new:
            idx=p['paragraph']-1
            k=next(x for x in ko['scenes'] if x['id']==sid)['lines'][idx]
            e=next(x for x in en['scenes'] if x['id']==sid)['lines'][idx]
            row=dict(scene=sid,paragraph=p['paragraph'],localStart=p['start'],localEnd=p['end'],ko=k,en=e)
        else:
            row=copy.deepcopy(next(x for x in baseline['paragraphs'] if x['scene']==sid and x['paragraph']==p['paragraph']))
        row.update(start=start/60+row['localStart'],end=start/60+row['localEnd']);paragraphs.append(row)
    scenes.append(s);start+=s['frames']
actual=baseline['actualFrames']+1325;explanation=baseline['explanationFrames']+883;body=start-120
assert actual+explanation==body==39473 and abs(actual-.6*body)<=1
assert len(paragraphs)==66 and [s['id'] for s in scenes if s['id'] not in additions]==[s['id'] for s in baseline['scenes']]
for c in cuts: assert c.get('sourceOut',0)<=c.get('sourceIn',c.get('sourceFirstFrame',0)/60)+c['frames']/60+0.000001
plan=R/'measured-additive-plan-v1.json';assert not plan.exists()
save(plan,dict(schemaVersion=1,revision='teaching-clarity-v1',recordedAt=now(),fps=60,
    baselinePlan='projects/motion-sickness-games/production/final-v1/plan.json',baselinePlanSha256=sha(ROOT/'projects/motion-sickness-games/production/final-v1/plan.json'),
    introFrames=120,outroFrames=600,bodyFrames=body,bodySeconds=body/60,bodyEnd=start/60,
    totalFrames=start+600,seconds=(start+600)/60,actualFrames=actual,explanationFrames=explanation,
    ratioErrorFrames=actual-.6*body,gameplayShare=actual/body,retainedExplanationMinimumFrames=14906,
    addedActualFrames=1325,addedExplanationFrames=883,scenes=scenes,paragraphs=paragraphs,cuts=cuts,
    classificationByVisibleContent=True,all12OriginalPcmPreserved=True,allOriginalParagraphsAndOrderPreserved=True,
    measuredPcmAndEditorialTimingPrepared=True,encodedFinalTimingApproved=False,finalRatioApproved=False,
    currentMixedAudioApproved=False,allFinalPixelsApproved=False,qaApproved=False,humanListeningApproved=False,publicRightsApproved=False))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='measured-additive-plan-prepared-independent-mc-pending',
    additiveContextReview=rel(R/'additions-contexts-asr-direct-review-v1.json'),currentDuplicateReview=rel(review),
    currentDuplicateCheckExitCode=0,measuredPlan=rel(plan),measuredTimingApproved=False,
    openingPilotPlaybackObservation=rel(playback),next='Create and directly review the two new projected Motion Canvas explanations; retain original12 scenes/PCM and annotate retained actual action where narration refers to it. Final mix/pair/pixels remain pending.')
save(R/'latest-checkpoint.json',cp)
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qpath)
q['execution'].update(stage=cp['stage'],next=cp['next'],ownedJob=None)
for x in q['items']:
    if x['slug']=='motion-sickness-games':x.update(status=cp['stage'],measuredPlan=rel(plan),currentDuplicateReview=rel(review))
save(qpath,q)
print(json.dumps(dict(totalFrames=start+600,bodyFrames=body,actualFrames=actual,explanationFrames=explanation,
    retained12Pcm=True,overviewSeconds=1507/60,currentDuplicateCheckExitCode=0,finalGates=False),ensure_ascii=False))
