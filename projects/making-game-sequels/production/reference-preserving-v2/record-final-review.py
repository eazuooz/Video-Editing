"""Record completed direct review; do not treat technical QA as human approval."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]; P=R/'projects/making-game-sequels'; O=P/'production/local/reference-preserving-v2/edit'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
qa=read(O/'qa/integrity.json'); compare=read(O/'final-mix-text-comparison.json'); levels=read(O/'qa/level-candidate-review.json')
assert compare['reviewStatus']=='complete-full-text-reviewed', 'Read full current recognition before recording approval'
assert levels['technicalGainFlagsResolved'] and all(x['fullDecodePassed'] and x['ptsMonotonicAndUniform'] for x in qa['outputs'])
for x in qa['outputs']:
 assert x['sha256']==sha(O/f"making-game-sequels-v2-{x['kind']}.mp4")
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); p=P/'production/review-ledger.json'; d=read(p)
d.update(updatedAt=now,voiceReview='Current9-scene PCM and encoded mix complete-text reviewed; human listening pending',renderReview='complete-current-output-internal-QA',driveFinalReview='pending upload and human review')
d['visualQA'].update(completeFinalPixels='passed-direct-review',movingExplanationsAndAnnotations='passed-direct-review',firstRepairChangedPixels='All63 samples across6 sheets directly read; retained cut13/14/16/28 and joins passed; first cut superseded by final repair',finalChangedPixels={'evidence':'production/local/reference-preserving-v2/edit/qa/changed-final/contact-00.jpg','samples':12,'allDirectlyRead':True,'result':'no blank/loading frame or caption collision'},motionReview={'method':'Native-speed playback with observed progression/start/end frames; complete encoded-frame coverage separately recorded','explanations':9,'annotations':5,'chapterJoins':8,'mobileWidth':375,'desktopWidth':900,'firstCutCurrentMasterReviewed':True,'scope':'Direct visual review; not human whole audiovisual listening approval'},integrity='production/local/reference-preserving-v2/edit/qa/integrity.json',gameplayBlackoutScan='production/local/reference-preserving-v2/edit/qa/gameplay-blackouts.json',currentMasterSha256=qa['outputs'][1]['sha256'],retainedEvidenceBasis='Unchanged cut hashes, caption ASS, timing and settings in active-inpoint-repair.json; all new files decoded completely')
d['audioQA'].update(wholeEncodedMixAsr='complete-full-text-reviewed',unresolvedTechnicalFlags=[],finalMixTextReview='production/local/reference-preserving-v2/edit/final-mix-text-comparison.json',encodedAudioSha256=read(O/'final-mix-asr.json')['audioSha256'],continuityReport='production/local/reference-preserving-v2/edit/qa/audio-continuity.json',candidateResolution='production/local/reference-preserving-v2/edit/qa/level-candidate-review.json',candidatePhraseContextsRead=27,activeWindowCount=levels['activeWindowCount'],minimumActiveVoiceTransferDb=levels['minimumActiveVoiceTransferDb'],humanWholeListening='pending',humanPronunciation='pending')
d['visualDesign']['actualCaptionedSample']='passed current16 samples at375px plus all cues in final output';d['visualDesign']['changes']=[x for x in d['visualDesign']['changes'] if 'excavation' not in x]+['Corrected concurrent HUD confusion: Oatchi Rush breaks pots and exposes items']
d['visualDesign']['newSystemGate']='Complete current layouts, actual captions and final moving explanations reviewed'
d['actionMatchCorrection']['newAudioReview']='Complete current scene07 text reviewed; human pronunciation pending'
d['preparedEdit'].update(actualMeasuredRatio='14498 actual /9665 explanation frames;60:40 within0.2 frame',finalCurrentASR='complete-full-text-reviewed')
d['preparedEdit']['captionTextFit'].update(currentSpeechTiming='ASR aligned',currentEncodedPixels='passed-direct-review');d['preparedEdit']['actualCaptionEvidence']['movingFinalOutput']='passed-direct-review'
d['preparedEdit']['measuredTiming']['planSha256']=sha(P/'production/reference-preserving-v2/edit-plan.json');write(p,d)
qa['changedPixels']='passed-direct-review; changed-final/contact-00.jpg and retained first-repair/qa/changed coverage';write(O/'qa/integrity.json',qa)
p=P/'production/latest-checkpoint.json';c=read(p);c.update(updatedAt=now,stage='internal-QA-complete-collect-and-drive',nextAction='Collect four current outputs and upload captioned master to Google Drive for user final review',newRevisionRendered=True,newRevisionHumanReviewed=False);c['currentMaster']={'sha256':qa['outputs'][1]['sha256'],'frames':24883,'fps':60,'width':1920,'height':1080,'internalQaComplete':True,'humanWholeListening':'pending','humanPronunciation':'pending'};write(p,c)
print('Recorded current-output internal review; human review remains pending.')
