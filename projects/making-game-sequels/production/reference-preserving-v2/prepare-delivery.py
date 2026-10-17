"""Promote only the checked current masters; preserve baseline files and platform state."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2/edit'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rel(p):return p.relative_to(R).as_posix()
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
plan=read(V/'edit-plan.json');qa=read(L/'qa/integrity.json');ledger=read(P/'production/review-ledger.json')
assert plan['timing']=='measured-and-asr-aligned'
assert ledger['visualQA']['completeFinalPixels']=='passed-direct-review'
assert ledger['visualQA']['movingExplanationsAndAnnotations']=='passed-direct-review'
assert ledger['audioQA']['wholeEncodedMixAsr']=='complete-full-text-reviewed'
assert ledger['audioQA']['wholeNarrationAsr']=='complete-full-text-reviewed'
assert not ledger['audioQA']['unresolvedTechnicalFlags']
assert all(x['fullDecodePassed'] and x['ptsMonotonicAndUniform'] for x in qa['outputs'])
p=P/'project.json';m=read(p);m.setdefault('preservedDeliveryManifests',[])
if not any(x.get('id')=='before-reference-preserving-v2' for x in m['preservedDeliveryManifests']):
 m['preservedDeliveryManifests'].append({'id':'before-reference-preserving-v2','titles':m.get('titles'),'paths':m.get('paths'),'video':m.get('video'),'finalRender':m.get('finalRender'),'editing':m.get('editing'),'finalProduction':m.get('finalProduction'),'platformVideoId':'2-IyuwcP_vQ','preserved':True})
metadata=read(P/'publishing/reference-preserving-v2/metadata.json');m['titles']={'ko':metadata['title'],'en':metadata['titleEn']};m['status']='awaiting-drive-final-review';m['publishReady']=False;m['visualStyle']='research-black-v1';m['activeRevision']='reference-preserving-v2';m['video']={'width':1920,'height':1080,'fps':60,'durationSeconds':plan['totalFrames']/60}
m['paths'].update(script=rel(P/'script/reference-preserving-v2/narration.ko.json'),scriptEn=rel(P/'script/reference-preserving-v2/narration.en.json'),narration='shared/output/narration/making-game-sequels/reference-preserving-v2/game-sequels-reference-v2.wav',audioMix=rel(L/'final-mix.m4a'),editorAudioMix=rel(L/'final-mix.wav'),audioReport=rel(L/'audio-build.json'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt'),videoClean=rel(L/'making-game-sequels-v2-clean.mp4'),videoBurnedCaptions=rel(L/'making-game-sequels-v2-captioned.mp4'),timeline=rel(V/'edit-plan.json'),footageCuts=rel(V/'edit-plan.json'),sources=rel(P/'planning/chapter-plan.json'),sceneProductionPlan=rel(V/'edit-plan.json'),motionCanvasProject='motion-canvas/src/projects/making-game-sequels/revision-v2/production-project.ts',publishingKo=rel(P/'publishing/reference-preserving-v2/description.ko.txt'),publishingEn=rel(P/'publishing/reference-preserving-v2/description.en.txt'),qaReport=rel(L/'qa/integrity.json'))
for key in ['captionAlignmentReview','candidateTimeline']:m['paths'].pop(key,None)
m['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualGameplayShare=.6,actualCommercialGameplaySeconds=plan['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,explanationStyle='research-black-v1; progressive arrows and source-matched screenshots',sourceMinimum=[1920,1080])
m['editing'].setdefault('exampleInterleaving',{}).update(planningPath=rel(V/'edit-plan.json'),reviewStatus='Current measured cuts and caption cues directly reviewed; native-speed independent gameplay')
m['tts']=read(V/'tts-manifest.json')['tts'];m['audio'].update(narrationTargetLufs=-16,bgmTargetLufs=-31,gameWorkingRmsDbfs=-33,voiceGainMode='constant-global-gain-with-short-peak-limiter',voiceDucked=False,report=rel(L/'audio-build.json'),continuityReport=rel(L/'qa/audio-continuity.json'),sourceAudioPolicy='Useful Nintendo gameplay sound retained quietly; GT7 source audio excluded; approved Nimbus')
m['membershipOutro']['appliedToFinal']=True
m['finalRender']={'status':'complete-current-master-human-review-pending','frames':plan['totalFrames'],'durationSeconds':plan['totalFrames']/60,'resolution':[1920,1080],'fps':60,'technicalQa':rel(L/'qa/integrity.json'),'reviewLedger':rel(P/'production/review-ledger.json'),'allFinalPixelsReviewed':True,'humanListening':'pending user final review','technicalApproved':True,'videoClean':m['paths']['videoClean'],'videoBurnedCaptions':m['paths']['videoBurnedCaptions']}
m['currentRevision'].update(status='awaiting-drive-final-review',deliveryStatus='four-output-collection-next',baselinePreserved=True)
m['currentDelivery']={'revision':'reference-preserving-v2','boundary':'google-drive-final-review','driveRequired':True,'driveUploaded':False,'youtubeUploadAuthorized':False,'userReview':'pending this exact version','baselineVideoId':'2-IyuwcP_vQ','baselineUnchanged':True,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
m['finalProduction']={'revision':'reference-preserving-v2','technicalApproved':True,'collected':False,'driveUploaded':False,'privateUploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending','publishReady':False,'reviewLedger':rel(P/'production/review-ledger.json')}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Checked master paths promoted; prior delivery and YouTube upload preserved. Collect four outputs and upload the current captioned master to Drive.')
