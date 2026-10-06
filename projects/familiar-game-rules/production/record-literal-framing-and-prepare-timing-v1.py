"""Direct candidate pixel review and measured frame budget, still no final adoption."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

reviewpath=PROOF/'literal-caption-framing-direct-review-v1.json';assert not reviewpath.exists()
evidencepath=PROOF/'literal-caption-framing-candidates-v1.json';e=read(evidencepath);assert e['boardCount']==6 and e['imageCount']==36
notes=[
 'additional16: one-line full frame leaves the firing character and wire-transition body visible. Central floor debris may lie under the box. bottom150 clips the airborne character at the last sample and removes wider market context; reject that uniform crop.',
 'additional22: short one-line full frame preserves rail-side firing, market character and right-edge wall traversal. bottom150 changes which surrounding platform/targets are visible; no need to adopt it from these samples. Verify exact per-cue words and motion later.',
 'action13: full frame keeps airborne umbrella and the upper-platform aim, then lower-platform firing visible. The bottom-central lower opponent still requires literal cue/motion review at the middle sample. bottom150 removes upper context and can cover the lower opponent; reject blanket crop.',
 'action23: full frame shows airborne character and upper/right shooter; some bottom-ground opponents/debris remain beneath the box. Detailed1920x1080 middle sample was also read. A crop cannot be approved globally; reserve critical-target cue timing for full segment review.',
 'action35: one-line full frame keeps the yellow player and main upper traversal/split-aim visible. A lower-floor opponent is partially behind the middle caption; require per-cue timing or reassignment if that opponent is the stated focus. bottom150 excludes surrounding floor/targets and does not fix every lower overlap.',
 'hype05: full frame retains the airborne player, crate/roof and lower targets. bottom150 excludes the airborne character at the last sample and removes upper opponents. Reject it. The downward-aim phrase must be assigned to its actual later action, not assumed from every framing-test sample.'
]
boards=[]
for b,n in zip(e['boards'],notes):
    assert sha(ROOT/b['path'])==b['sha256']
    for t in b['tiles']:assert sha(ROOT/t['path'])==t['sha256'] and sha(ROOT/t['sourcePixelPath'])==t['sourcePixelSha256']
    boards.append(dict(path=b['path'],sha256=b['sha256'],allSixCandidateTilesDirectlyRead=True,observation=n))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),candidateEvidence=rel(evidencepath),candidateEvidenceSha256=sha(evidencepath),
    boards=boards,all6BoardsAnd36CandidatePixelsDirectlyRead=True,oneAdditionalFullResolutionMiddleSampleRead='action23 native full frame middle',
    captionCenter=[960,970],captionFontPx=48,captionAnchorChanged=False,preferredCandidate='native-full-frame-with-short-literal-one-line-cues',
    rejectedBlanketCrop=[320,360,1280,720],sourceNativeExtractionRepeated=False,
    unresolvedCriticalTargetCases=['action13 middle lower opponent','action23 bottom targets if stated focus','action35 middle lower-floor opponent'],
    allFinalCaptionPixelsReviewed=False,fullScreenFramingApproved=False,finalTimingApproved=False,newGitImages=0,
    scope='Framing candidate comparison only. Actual full cue/cut/motion pixels and final encoded pixels remain separate gates.')
save(reviewpath,review)
audit=read(BASE/'byte-exact-original-guide-insertion-audit-v1.json')
assert read(BASE/'guide-joins-direct-review-v1.json')['structuralContentReviewComplete']
guides=read(BASE/'observation-guide-tts-execution-v1.json')['results']
originalScenes=read(BASE.parent/'script/narration.ko.json')['scenes']
actual={'02','04','06','08','10'}
observations={'12':6,'13':6,'14':12,'15':12,'16':22,'17':22,'18':22,'19':23}
pieces=[]
for scene in originalScenes:
    id=scene['id'];parts=[f for f in audit['originalFragments'] if f['scene']==id]
    previousGuide=None
    for part in parts:
        start=part['startSample'];end=part['endSample'];samples=part['samples']
        before=15 if id in actual and part['part']==1 else 0
        if previousGuide:before+=8+observations[previousGuide]
        following=next((c for c in audit['cuts'] if c['scene']==id and c['splitSample']==end),None)
        after=8 if following else (15 if id in actual and part['part']==len(parts) else 0)
        voiceframes=math.ceil(samples*60/24000)
        role='actual-existing-game' if id in actual else 'explanation'
        pieces.append(dict(id=id+f'-part{part["part"]}',logicalScene=id,kind='original-fragment',audioPath=part['path'],audioSha256=part['sha256'],
            sourceStartSample=start,sourceEndSample=end,samples=samples,sourceSeconds=samples/24000,
            beforeVoiceFrames=before,voiceContainerFrames=voiceframes,afterVoiceFrames=after,durationFrames=before+voiceframes+after,
            roleSegments=[dict(role=role,frames=before+voiceframes+after)],
            paddingPurpose='Short lead into related visible action / review-requested observation and normal chapter transition' if before+after else None,
            selectedSourceCuts=[],sourcePixelsReviewed=False,captionPixelsReviewed=False))
        if following:
            gid=following['guide'];g=next(x for x in guides if x['id']==gid);frames=math.ceil(g['samples']*60/24000)
            roles=[dict(role='actual-existing-game',frames=frames)]
            if gid in ['14','17']:
                cut=504 if gid=='14' else 440
                roles=[dict(role='actual-existing-game',frames=cut),dict(role='explanation',frames=frames-cut)]
            pieces.append(dict(id=gid,logicalScene=gid,parentScene=id,kind='new-guide',audioPath=g['path'],audioSha256=g['sha256'],samples=g['samples'],
                sourceSeconds=g['seconds'],beforeVoiceFrames=0,voiceContainerFrames=frames,afterVoiceFrames=0,durationFrames=frames,roleSegments=roles,
                roleBoundaryBasis='Directly read whole/independent word context plus quiet intersentence interval; explanatory design implication only' if len(roles)>1 else None,
                selectedSourceCuts=[],sourcePixelsReviewed=False,captionPixelsReviewed=False,diagramPixelsReviewed=False if len(roles)>1 else None))
            previousGuide=gid
        else:previousGuide=None
cursor=120
for p in pieces:
    assert sha(ROOT/p['audioPath'])==p['audioSha256']
    p.update(startFrame=cursor,endFrame=cursor+p['durationFrames'],voiceStartFrame=cursor+p['beforeVoiceFrames'])
    cursor=p['endFrame']
    off=p['startFrame']
    for r in p['roleSegments']:r.update(startFrame=off,endFrame=off+r['frames']);off=r['endFrame']
white=sum(r['frames'] for p in pieces for r in p['roleSegments'] if r['role']=='explanation')
game=sum(r['frames'] for p in pieces for r in p['roleSegments'] if r['role']=='actual-existing-game')
assert len(pieces)==27 and white==9140 and game==13710 and game/(game+white)==.6
originalWhite=sum(p['durationFrames'] for p in pieces if p['kind']=='original-fragment' and p['logicalScene'] not in actual)
assert originalWhite==8835 and originalWhite/60>=147.2
timingpath=BASE/'measured-word-timing-candidate-v1.json';assert not timingpath.exists()
timing=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),status='measured-audio-frame-budget-candidate; source-action/cue alignment not adopted',
    fps=60,pieces=pieces,originalSceneCount=11,newGuideCount=8,logicalSceneCount=19,originalFragments=19,originalParagraphCount=46,newParagraphCount=24,
    originalPcmSecondsPreserved=296.72,newGuidePcmSecondsPreserved=77.20004166666667,allSpeechSeconds=373.9200416666667,
    originalWhiteFrameBudget=8835,originalWhiteSecondsPreserved=147.2,newExplanationFrameBudget=305,
    explanationFrameBudget=white,actualFrameBudget=game,bodyFrameBudget=game+white,finalFrameBudget=cursor+600,
    plannedBodyRatio=.6,plannedRoundingErrorFrames=0,sourceBankCandidateSeconds=233.467,
    membershipStartFrame=cursor,membershipFrames=600,catIntroFrames=120,
    noNarrationSamplesCutOrRepeated=True,sourceAudioUsed=False,selfCreatedGameExamples=0,loop=0,editorSlowdown=0,
    finalTimingApproved=False,bodyRatioApproved=False,finalTimelineAdopted=False,finalWordActionAlignment=False,
    allSourceSegmentPixelsReviewed=False,allDiagramPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,finalMixedAsrApproved=False,
    scope='Integer frame candidate based on actual PCM. Source selection, literal cues, movement and encoded pixels must pass before adoption or rendering.',newGitImages=0)
save(timingpath,timing)
qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='all-audio-joins-reviewed-literal-framing-candidate-read-source-cue-alignment-pending',updatedAt=now(),
    literalCaptionFramingDirectReview=rel(reviewpath),measuredTimingCandidate=rel(timingpath),
    nextAction='Adopt neither candidate ratio nor blanket crop yet. Align all70paragraphs/currentwords to unique related source cuts and literal fixed-center cues; verify every cue/cut/motion pixel including flagged lower targets. Preserve all original/new PCM and originalsixwhite. Final mix/render/ASR/QA/collection/private false.')
q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','literalCaptionFramingDirectReview','measuredTimingCandidate']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(candidatePieces=27,bodyFrames=game+white,finalFrames=cursor+600,actualFrames=game,whiteFrames=white,
    seconds=(cursor+600)/60,bodyRatioApproved=False,allFinalPixelsApproved=False)))
