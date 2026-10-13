"""Promote only the reviewed local delivery manifest, preserving the scheduled baseline."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[3];H=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rel=lambda p:p.relative_to(ROOT).as_posix()
proof=P/'main-promotion-v1.json';assert not proof.exists()
c=read(ROOT/'shared/publishing/video-production-control.json')
assert c['selectedVideo']=='hierarchical-game-outlines' and c['newProductionAuthorization']['privateUploadAuthorized']
assert read(P/'final-repair-execution-v2.json')['exitCode']==0
assert read(P/'final-direct-review-v2.json')['approvedForPrivateUpload']
plan=read(P/'final-timeline-v1.json');mix=read(P/'mix-final-inputs-v1.json');main=H/'project.json'
before=main.read_bytes();assert hashlib.sha256(before).hexdigest()=='575c807611d8c60040db51764cd805cf712fae48fd0037525f8591c753f50070'
backup=P/'baseline-main-local.json';assert not backup.exists();backup.write_bytes(before)
j=json.loads(before);prior={'reason':'2026-10-13 selected independent-source private revision; baseline reservation preserved','publishing':j['publishing'],'finalRender':j['finalRender'],'paths':j['paths'],'audio':j['audio'],'approvals':j['approvals']}
j.setdefault('publishingHistory',[]).append(prior)
j['status']='current-independent-source-render-reviewed-ready-private-upload'
j['titles']={k:(P/f'publishing/title.{k}.txt').read_text(encoding='utf-8').strip() for k in ['ko','en']}
j['video'].update(durationSeconds=plan['totalFrames']/60)
j['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualCommercialGameplaySeconds=plan['actualFrames']/60,sourceBankSeconds=None,timingStatus='current-17140-frames-exact-60:40',exampleInterleaving={'planningPath':rel(P/'final-timeline-v1.json'),'reviewStatus':'final-direct-review-v2.json'})
j['audio']={'mixStatus':'current-AAC-reviewed-private-human-listening-pending','selectedAudio':mix,'narrationTargetLufs':-16,'gameAudioTargetLufs':-29,'bgmTargetLufs':-31,'bgmDuringGameplayDb':-3,'finalGainDb':-1.05,'measuredIntegratedLufs':-18.49,'measuredTruePeakDbtp':-2.56,'backgroundMusic':{'title':'Late Night Radio','artist':'Kevin MacLeod','license':'CC BY 4.0','licenseRecord':rel(H/'production/manual-preflight-v1/music-rights.json'),'file':rel(H/'production/manual-preflight-v1/Late-Night-Radio.mp3')},'sourceAudioPolicy':'Quiet original mixed gameplay audio; not isolated SFX. Original branding/member audio retained.'}
j['paths'].update(script=rel(P/'narration.ko.json'),sources=rel(P/'independent-menu-source-review.json'),publishingKo=rel(P/'publishing/description.ko.txt'),publishingEn=rel(P/'publishing/description.en.txt'),audioReport=rel(P/'mix-direct-review-v1.json'),audioMix=mix['audio'],editorAudioMix=mix['audio'],narration=rel(P/'narration-stem-local.wav'),timelineNarration=rel(P/'narration-stem-local.wav'),captionsKo=rel(P/'captions.ko.srt'),captionsEn=rel(P/'captions.en.srt'),captionAlignmentReview=rel(P/'caption-alignment-review-v1.json'),videoClean=rel(P/'hierarchical-game-outlines.clean.review.mp4'),videoBurnedCaptions=rel(P/'hierarchical-game-outlines.captioned.review.mp4'),timeline=rel(P/'final-timeline-v1.json'),motionCanvasProject='motion-canvas/src/projects/hierarchical-game-outlines/reference-explanations-v1.tsx')
j['paths']['videoClean']=rel(P/'hierarchical-game-outlines.clean.v2.review.mp4')
j['paths']['videoBurnedCaptions']=rel(P/'hierarchical-game-outlines.captioned.v2.review.mp4')
j['paths'].pop('manimProject',None)
j['engines']=['motion-canvas-scene-tree-cpu-adapter','ffmpeg']
j['editing']['exampleExpansion']={'method':'user-selected Sakurai reference progression, independently worded script, independent game recordings and detailed inline explanations','previousDeliveryAndPCMHistoryPreserved':True,'currentPlan':rel(P/'final-timeline-v1.json')}
j['tts'].update(outputDir=rel(P/'narration'),renderMode='scene',currentExecution=rel(P/'voice-execution-v1.json'),currentVoiceReview=rel(P/'voice-direct-review-v1.json'))
j['approvals']={'script':'current-eight-scenes-independent-KOEN-reference-flow-reviewed','voiceSample':'existing-approved-Qwen3-TTS1.7B-reference','bgm':'quiet-licensed-Late-Night-Radio','final':'current-technical-and-bounded-pixel-review-complete; human-listening-pronunciation-pending','publication':'private editorial review only; public rights unresolved','voiceReadback':rel(P/'mix-direct-review-v1.json')}
j['finalRender']={'revision':'reference-preserving-v1','status':'current-reviewed-pair','frames':plan['totalFrames'],'durationSeconds':plan['totalFrames']/60,'videoClean':j['paths']['videoClean'],'videoBurnedCaptions':j['paths']['videoBurnedCaptions'],'technicalQa':rel(P/'qa-execution-v1.json'),'pixelReview':rel(P/'final-direct-review-v1.json'),'allFinalPixelsReviewed':False,'allPlannedFinalSamplesReviewed':True,'openItems':['Human full listening/pronunciation, including scene06 Word and scene07 wording','Menu recording uploader reuse permission/public rights','External media backup','Previously pending original Nimbus branding/member source and truncated handles']}
j['finalRender']['technicalQa']=rel(P/'final-repair-execution-v2.json')
j['finalRender']['pixelReview']=rel(P/'final-direct-review-v2.json')
j['publishReady']=False
j['publishing']={'defaults':'shared/publishing/youtube-defaults.json','privacyStatus':'private','scheduled':False,'uploaded':False,'actualVideoId':None,'receipt':rel(P/'publishing/youtube-upload-v1.json'),'baselineVideoId':'jBRt3xatdPk','baselineReservationPreserved':True,'thumbnail':rel(H/'publishing/thumbnail-depth-v1.png'),'fullSettingsVerified':False,'coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True,'pinnedCommentStatus':'prepared-pending-private-comments-unavailable'}
for key in ['script','publishingKo','publishingEn','audioMix','captionsKo','captionsEn','captionAlignmentReview','videoClean','videoBurnedCaptions','timeline']:
 assert (ROOT/j['paths'][key]).is_file(),key
write(main,j)
write(proof,{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':{'path':rel(backup),'sha256':sha(backup)},'current':{'path':rel(main),'sha256':sha(main)},'purpose':'Intentional local delivery path/metadata promotion only; no Studio baseline change','baselineYouTubeId':'jBRt3xatdPk','baselineChanged':False})
print('Reviewed current local manifest promoted; original manifest exact backup; Studio baseline unchanged')
