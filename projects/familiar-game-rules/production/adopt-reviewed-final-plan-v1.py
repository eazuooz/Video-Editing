import copy, math, subprocess
from final_cpu_common import *
from PIL import ImageFont
assert not (FINAL/'plan.json').exists()
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],cwd=ROOT,check=True)
sp=BASE/'word-action-source-candidate-v6.json';cp=BASE/'word-caption-candidate-v4/captions.json'
s,c=read(sp),read(cp);motion=read(PROOF/'moving-source-direct-review-v6.json')
g=read(PROOF/'guide13-encoded-input-direct-review-v7.json');white=read(PROOF/'timed-white-input-verification-v1.json')
assert motion['sourceCandidateSha256']==sha(sp) and motion['directlyReviewedCuts']==85 and motion['allSourceMotionReviewed'] and motion['allWordActionAligned']
assert g['captionCandidateSha256']==sha(cp) and g['allDirectlyRead'] and g['all89NewFramesDirectlyRead']
assert white['allEncodedDiagramPixelsReviewed'] and sha(ROOT/white['output'])==white['sha256'] and white['frames']==9140
proofs=['moving-source-direct-review-v6.json','guide13-encoded-input-direct-review-v7.json','word-cue-input-direct-progress-v1.json','targeted-input-direct-review-v3.json','white-boss-pedro-input-direct-progress-v4.json','timed-white-input-verification-v1.json','native-guide12-boundary-reassignment-v5.json','native-guide13-aim-reassignment-v6.json','guide13-six-frame-caption-boundary-correction-v4.json','current-geometry-projects-distinct-review-v4.json']
for f in proofs:assert (PROOF/f).exists()
pieces=copy.deepcopy(s['pieces']);cuts=[t for p in pieces for t in p['selectedSourceCuts']]
assert len(pieces)==27 and len(cuts)==85 and len(c['paragraphs'])==70 and len(c['ko'])==253 and len(c['en'])==118
observations={x['cutId']:x for x in motion['cuts']}
for t in cuts:
    o=observations[t['id']];assert o['decision']=='aligned'
    assert o['sourceSha256']==t['sourceSha256'] and o['inFrameInclusive']==t['inFrameInclusive'] and o['outFrameExclusive']==t['outFrameExclusive']
    t.update(completeMotionReviewed=True,wordActionAlignmentApproved=True,directObservation=o['notes'],sourceInputReview=rel(PROOF/'moving-source-direct-review-v6.json'),finalPixelApproved=False)
    if t['id']=='10-part3-cut01':
        t['historicalCandidateConnection']=t['visibleActionConnection'];t['visibleActionConnection']='Room-to-vertical-shaft wall jumps and aim toward upper-left/right red opponents, then cage approach. Not a train/crate sequence. Conditional design question, not implementation or exact-button proof.'
actual=sum(t['durationFrames'] for t in cuts);expl=sum(x['frames'] for x in white['independentRows'])
assert actual==13710 and expl==9140 and actual+expl==22850 and actual==.6*(actual+expl)
pos=120
for p in pieces:
    assert p['startFrame']==pos and p['endFrame']-p['startFrame']==p['durationFrames'];pos=p['endFrame']
    assert sha(ROOT/p['audioPath'])==p['audioSha256'];assert p['samples']<=p['voiceContainerFrames']*400
assert pos==22970 and sum(p['samples'] for p in pieces)==8968322
plan=dict(schemaVersion=1,slug='familiar-game-rules',createdAt=now(),status='reviewed-input-timing-adopted-final-media-pending',fps=60,width=1920,height=1080,introFrames=120,outroFrames=600,actualFrames=actual,explanationFrames=expl,bodyFrames=22850,finalFrames=23570,finalSeconds=23570/60,body60_40ErrorFrames=0,ratioRoundingErrorFrames=0,allCurrentPcmSamples=8968322,allCurrentPcmSeconds=8968322/24000,overviewSeconds=24.32,original11PcmSamplesPreserved=True,originalSixWhiteFrames=8835,extraWhiteFrames=305,logicalSceneCount=19,pieces=pieces,nativeCuts=cuts,whiteSegments=white['independentRows'],whiteInput=white['output'],whiteInputSha256=white['sha256'],captionCandidate=rel(cp),captionCandidateSha256=sha(cp),sourceCandidate=rel(sp),sourceCandidateSha256=sha(sp),timingCandidate=s['timingCandidate'],timingCandidateSha256=s['timingCandidateSha256'],inputReviewEvidence=[dict(path=rel(PROOF/f),sha256=sha(PROOF/f)) for f in proofs],finalTimingApproved=True,bodyRatioApproved=True,allSourceMotionReviewed=True,allInputSegmentCaptionPixelsReviewed=True,inputPixelScope='Raw/PIL caption cue and source boundary trials plus decoded white inputs and guide13 ASS input; final composite pixels always separate',allFinalPixelsApproved=False,allFinalCaptionPixelsReviewed=False,finalMixBuilt=False,finalMixAsrApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False,humanWholeListening='pending',humanPronunciation='pending',originalNimbusFileVerified=False,sourceAudioStreams=0,selfCreatedGames=0,loops=0,slowdown=0,newGitImages=0)
for name,frames,start,expected in [('branding',120,0,'706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'),('membership',600,22970,'181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123')]:
    path=ROOT/f'projects/game-reward-planning/production/final-v1/white-segments/{name}.mp4';assert sha(path)==expected
    plan[name]=dict(path=rel(path),sha256=expected,frames=frames,startFrame=start)
FINAL.mkdir();write(FINAL/'plan.json',plan)
def stamp(t,sep):
    n=round(t*(100 if sep=='.' else 1000));u=100 if sep=='.' else 1000
    return f'{n//(3600*u):02}:{n//(60*u)%60:02}:{n//u%60:02}{sep}{n%u:0{2 if sep=="." else 3}d}'
for lang in ['ko','en']:
    text='\n\n'.join(f'{q["index"]}\n{stamp(q["startSeconds"],",")} --> {stamp(q["endSeconds"],",")}\n{q[lang]}' for q in c[lang])+'\n'
    (FINAL/f'captions.{lang}.srt').write_text(text,'utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
header=(ROOT/'projects/making-game-sequels/production/final-v1/captions.ko.ass').read_text('utf-8-sig').split('Dialogue:')[0];lines=[]
for q in c['ko']:
    a,z=stamp(q['startSeconds'],'.'),stamp(q['endSeconds'],'.');w=round(font.getlength(q['ko'])+44);left=round(960-w/2)
    for layer,color,x,y,bord in [(0,'323C07',left+14,942,0),(1,'FFFFFF',left,928,3)]:
        tags=f'{{\\an7\\pos({x},{y})\\p1\\bord{bord}\\shad0\\1c&H{color}&\\3c&H181B16&}}';lines.append(f'Dialogue: {layer},{a},{z},Default,,0,0,0,,{tags}m 0 0 l {w} 0 {w} 84 0 84')
    lines.append(f'Dialogue: 2,{a},{z},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0}}{q["ko"]}')
(FINAL/'captions.ko.ass').write_text(header+'\n'.join(lines)+'\n','utf-8')
adopt=dict(path=rel(FINAL/'plan.json'),sha256=sha(FINAL/'plan.json'),frames=23570,actualFrames=13710,explanationFrames=9140,bodyRatioErrorFrames=0,koCues=253,enCues=118,pcmSeconds=8968322/24000,sourceCuts=85,whiteSegments=8,scope='Input timing adoption only. Final mix/full ASR/pair/encoded pixels/QA/private settings pending.')
manifest=read(BASE.parent/'project.json');manifest['status']='current-reviewed-inputs-final-production'
manifest['editing'].update(actualGameplaySeconds=actual/60,actualExplanationSeconds=expl/60,actualGameplayShare=.6,actualCommercialGameplaySeconds=actual/60,actualDevelopmentFootageSeconds=0,timingStatus='current-final-input-timing-approved',finalBodyFrames=dict(total=22850,actual=actual,explanation=expl,ratioErrorFrames=0),finalPlan=adopt)
manifest['editing']['openingOverview']['measuredSeconds']=24.32
manifest['editing']['exampleInterleaving']['reviewStatus']='85 current whole-motion cuts reviewed; all input caption/white trials read; final encoded pixels pending'
manifest['video']['durationSeconds']=23570/60
manifest['paths'].update(captionsKo=rel(FINAL/'captions.ko.srt'),captionsEn=rel(FINAL/'captions.en.srt'))
manifest['publishReady']=False;write(BASE.parent/'project.json',manifest)
update_checkpoint('current-reviewed-final-input-timing-adopted','Build one CPU2 final Nimbus mix preserving all27piece PCM samples; current mixed ASR and final pair/pixels/QA/private/Git then pause automation24. No next queued item.',finalPlan=adopt,finalTimelineAdopted=True,finalTimingApproved=True,finalRatioApproved=True,allSourceMotionReviewed=True,sourceMotionDirectReview=dict(path=rel(PROOF/'moving-source-direct-review-v6.json'),sha256=sha(PROOF/'moving-source-direct-review-v6.json'),directlyReviewedCuts=85,expectedCuts=85,allSourceMotionReviewed=True,allWordActionAligned=True),guide13EncodedInputDirectReview=rel(PROOF/'guide13-encoded-input-direct-review-v7.json'),wordCaptionCandidate=rel(cp),wordCaptionCandidateSha256=sha(cp),allFinalCaptionPixelsReviewed=False,render=False,qa=False,collected=False,uploaded=False)
print(json.dumps(adopt))
