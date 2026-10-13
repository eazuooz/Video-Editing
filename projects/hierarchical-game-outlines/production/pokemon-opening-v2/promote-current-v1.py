"""Promote the reviewed requested revision locally; preserve all prior platform IDs."""
from pathlib import Path
import json,hashlib,datetime,copy
P=Path(__file__).resolve().parent;R=P.parents[3];H=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'main-promotion-v1.json').exists()
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['privateUploadAuthorized']
assert read(P/'qa-execution-v1.json')['exitCode']==0 and read(P/'final-direct-review-v1.json')['approvedForPrivateUpload']
main=H/'project.json';old=main.read_bytes();backup=P/'delivered-main-backup-local.json'
assert sha(main)==sha(backup)=='45bae8b008d8f34e562bd868e3a71f1220a61338b18e433d19be6c1adb1c8c5b'
plan=read(P/'final-timeline-v1.json');mix=read(P/'mix-final-inputs-v1.json');measurement=read(P/'mix-duck-existing-verification-v2.json')['decodedAAC']
assert read(P/'mix-duck-existing-verification-v2.json')['currentMixSha256']==mix['sha256']
j=json.loads(old);j.setdefault('publishingHistory',[]).append(dict(reason='Requested Pokémon opening and removal of reference names from spoken/captioned explanations; previous private video retained unchanged',publishing=copy.deepcopy(j['publishing']),finalRender=copy.deepcopy(j['finalRender']),paths=copy.deepcopy(j['paths']),audio=copy.deepcopy(j['audio'])))
j.update(status='pokemon-opening-revision-reviewed-ready-private-upload',titles=read(P/'publishing/titles.json'))
j['video']['durationSeconds']=plan['totalFrames']/60
j['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualCommercialGameplaySeconds=plan['actualFrames']/60,timingStatus=f'current-{plan["totalFrames"]}-frames-exact-60:40',exampleInterleaving=dict(planningPath=rel(P/'final-timeline-v1.json'),reviewStatus='final-direct-review-v1.json'),explanationStyle='readable document diagrams and timed indentation, existing white palette; dimensionality selected by teaching need')
j['editing']['footageClassification']['explanation']='Self-authored diagrams, text, mathematical/3D demonstrations or comparisons; dimensionality selected by teaching need'
j['editing']['exampleExpansion']=dict(method='User-selected Pokémon illustrative planning document before the retained lesson progression; independently obtained footage and original narration',previousDeliveryAndPCMHistoryPreserved=True,currentPlan=rel(P/'final-timeline-v1.json'))
j['audio'].update(selectedAudio=mix,measuredIntegratedLufs=float(measurement['input_i']),measuredTruePeakDbtp=float(measurement['input_tp']))
j['paths'].update(script=rel(P/'narration.ko.json'),sources=rel(P/'source-direct-review.json'),publishingKo=rel(P/'publishing/description.ko.txt'),publishingEn=rel(P/'publishing/description.en.txt'),audioReport=rel(P/'mix-direct-review-v1.json'),audioMix=mix['audio'],editorAudioMix=mix['audio'],narration=rel(P/'narration-stem-local.wav'),timelineNarration=rel(P/'narration-stem-local.wav'),captionsKo=rel(P/'captions.ko.srt'),captionsEn=rel(P/'captions.en.srt'),captionAlignmentReview=rel(P/'caption-alignment-review-v1.json'),videoClean=rel(P/'hierarchical-game-outlines.clean.review.mp4'),videoBurnedCaptions=rel(P/'hierarchical-game-outlines.captioned.review.mp4'),timeline=rel(P/'final-timeline-v1.json'),motionCanvasProject='motion-canvas/src/projects/hierarchical-game-outlines/pokemon-opening-v2.tsx')
j['tts'].update(outputDir=rel(P/'current-narration'),currentExecution=rel(P/'voice-current-inputs.json'),currentVoiceReview=rel(P/'voice-direct-review.json'),maxRenderAttempts=1)
j['approvals'].update(script='27 paired independently authored paragraphs; reference names and attributed personal experience removed',voiceReadback=rel(P/'mix-direct-review-v1.json'))
j['finalRender'].update(revision='pokemon-opening-v2',status='current-reviewed-pair',frames=plan['totalFrames'],durationSeconds=plan['totalFrames']/60,videoClean=j['paths']['videoClean'],videoBurnedCaptions=j['paths']['videoBurnedCaptions'],technicalQa=rel(P/'qa-execution-v1.json'),pixelReview=rel(P/'final-direct-review-v1.json'),allFinalPixelsReviewed=False,allPlannedFinalSamplesReviewed=True)
j['publishing']=dict(defaults='shared/publishing/youtube-defaults.json',privacyStatus='private',scheduled=False,uploaded=False,actualVideoId=None,receipt=rel(P/'publishing/youtube-upload-v1.json'),baselineVideoId='jBRt3xatdPk',previousPrivateVideoId='JoHXz7YtEPw',baselineReservationPreserved=True,previousPrivatePreserved=True,thumbnail=rel(H/'publishing/thumbnail-depth-v1.png'),fullSettingsVerified=False,coachingEndingLinkRequired=True,pinnedCoachingCommentRequired=True,pinnedCommentStatus='prepared-pending-private-comments-unavailable')
j['publishReady']=False
for k in ['script','sources','audioMix','captionsKo','captionsEn','captionAlignmentReview','videoClean','videoBurnedCaptions','timeline']:assert (R/j['paths'][k]).exists(),k
write(main,j);write(P/'main-promotion-v1.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline=dict(path=rel(backup),sha256=sha(backup)),current=dict(path=rel(main),sha256=sha(main)),purpose='Local delivery pointer promotion only',priorPrivateVideo='JoHXz7YtEPw',baselineVideo='jBRt3xatdPk',platformMutation=False))
print('Reviewed revision promoted locally; previous private and scheduled platform uploads unchanged.')
