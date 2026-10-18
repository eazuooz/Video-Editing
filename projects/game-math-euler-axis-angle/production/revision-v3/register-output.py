"""Register verified selected Nintendo revision without changing prior deliveries."""
from pathlib import Path
import json,hashlib,datetime,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';HERE=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def tc(t):
 n=int(t);m,s=divmod(n,60);h,m=divmod(m,60);return f'{h}:{m:02}:{s:02}' if h else f'{m:02}:{s:02}'
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();t=read(HERE/'timeline.json');integrity=read(O/'qa/integrity.json');pair=read(O/'pair-source.json');audio=read(O/'audio-build.json')
 for v in integrity['outputs']:
  assert v['fullDecodePassed'] and v['ptsMonotonicAndUniform']
  assert sha(O/f'euler-{v["kind"]}.mp4')==v['sha256']==pair['outputs'][v['kind']]['sha256']
 assert t['actualFrames']*3==t['explanationFrames']*2 and integrity['ratioErrorFrames']==0
 narration=read(HERE/'narration-review.json');final=read(HERE/'final-audio-review.json');visual=read(HERE/'visual-review.json')
 assert narration['directlyComparedCurrentScenes']==26 and narration['fullTextReviewComplete']
 assert final['directWholeTextReviewed'] and final['narrationLevelContinuityStatus'] in ['pass','pass-with-natural-prosody-evidence','technical-transfer-pass-context-listening-pending']
 if final['narrationLevelContinuityStatus']=='technical-transfer-pass-context-listening-pending':
  assert final['humanWholeListening']=='pending' and final['contextualDropReview']['sourceOriginOnly'] is True
  assert final['contextualDropReview']['reviewedCandidates']==111 and final['unresolvedConfirmedContentErrors']==0
 assert final['captionedVideoSha256']==visual['captionedVideoSha256']==pair['outputs']['captioned']['sha256']
 assert all(visual[k] for k in ['currentCaptionAndCutPixelsReviewed','movingExplanationsAndAnnotationsReviewed','nativeAndMobileReviewed'])
 assert not read(O/'qa/audio-continuity.json')['flaggedVoiceTransferWindows']
 assert audio['music']['addedBgm'] is False and audio['sourceAudioUsed'] is True
 p=read(P/'project.json');manifest=read(HERE/'tts-manifest.json');baseline=read(P/'publishing/drive-review.json')
 p['revision']['previousDriveVersion']=baseline
 p['revision'].update(id='nintendo-annotated-no-bgm-v3',revisionScope='Selected M04 only: preserve17 explanation scenes and PCM; replace gameplay with three Nintendo games, meaningful source-tracked guides and quiet native sound; remove added BGM.')
 p.update(status='complete-local-revision-awaiting-drive-review',publishReady=False)
 p['video'].update(width=1920,height=1080,fps=60,durationSeconds=t['seconds'])
 p['editing'].update(timingStatus='revision-v3-measured-and-verified',actualGameplaySeconds=t['actualFrames']/60,actualExplanationSeconds=t['explanationFrames']/60,actualGameplayShare=.4,actualCommercialGameplaySeconds=t['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,finalBodyFrames=dict(total=t['bodyFrames'],actual=t['actualFrames'],explanation=t['explanationFrames'],ratioErrorFrames=0))
 p['editing']['openingOverview']['narrationSeconds']=t['scenes'][0]['voiceSeconds']
 p['editing']['exampleInterleaving']['reviewStatus']='three Nintendo games; source/caption/annotated composite reviewed'
 p['tts'].update(outputDir=manifest['tts']['outputDir'],filenameStem=manifest['tts']['filenameStem'],sceneGapSeconds=.3,maxNewTokens=2048)
 p['audio'].update(mixStatus='current-source-and-encoded-ASR-level-reviewed-user-whole-listening-pending',backgroundMusic=dict(enabled=False,required=False,policy='lecture-no-bgm-quiet-game-audio-v2'),bgmTargetLufs=None,bgmPlacement='none',musicFallbackScenes=[],narrationTargetLufs=-16,gameAudioTargetLufs=-32,sourceAudioPolicy='Quiet synchronized original game mix with voice-driven ducking; mixed game music/effects were not separated. No added music stem.')
 paths=dict(videoClean=O/'euler-clean.mp4',videoBurnedCaptions=O/'euler-captioned.mp4',captionsKo=O/'captions.ko.srt',captionsEn=O/'captions.en.srt',audioMix=O/'final-mix.m4a',editorAudioMix=O/'final-mix.wav',timeline=HERE/'timeline.json',productionBuilder=HERE/'render-edit.py',footageCuts=HERE/'timeline.json',manimProject=HERE/'math_visuals.py',renderReport=P/'production/qa.json',audioReport=P/'audio/mix-report.md',publishingKo=P/'publishing/revision-v3-description.ko.txt',publishingEn=P/'publishing/revision-v3-description.en.txt')
 p['paths'].update({k:rel(v) for k,v in paths.items()});p['paths']['narration']=manifest['tts']['outputDir']+'/'+manifest['tts']['filenameStem']+'.wav'
 for key in ['script','scriptEn']:
  p['paths'][key]=manifest['paths'][key]
 p['publishing'].update(currentRevision='nintendo-annotated-no-bgm-v3',driveFinalReviewRequired=True,youtubeReplacementAuthorized=False,privateUploadComplete=False,fullPublishingSettingsComplete=False,videoId=None,url=None,receipt=None)
 p['approvals'].update(humanListening='pending current complete Drive review',visualPixelReview='changed captions/cuts/annotations reviewed;17 identical explanation sources and local caption timings retain prior evidence',privateUpload='Await user review of this exact version')
 p['finalRender']=dict(status='current-local-revision-internal-QA-complete',currentRevisionComplete=True,durationSeconds=t['seconds'],fps=60,backgroundMusic=False,distinctActualGames=3,retainedExplanationScenes=17,qa=rel(P/'production/qa.json'),openItems=['완성본 Drive 사용자 검수 및 전체 청취·발음 확인 대기','기존 비공개 YouTube 업로드 유지'])
 p['membershipOutro']['appliedToFinal']=True;save(P/'project.json',p)
 design=read(P/'planning/production-plan.json');gameplay=read(HERE/'gameplay-script.json')['scenes']
 design.update(revision='nintendo-annotated-no-bgm-v3',updatedAt=now,status='internal-QA-complete-awaiting-complete-Drive-user-review')
 design['selectedRevision'].update(stage='internal-QA-complete-awaiting-Drive-review',candidatesFinalized=True,annotationPlan='sources/annotation-plan-v3.json',timeline='production/revision-v3/timeline.json',distinctGames=['Mario Kart 8 Deluxe','The Legend of Zelda: Tears of the Kingdom','Super Mario Odyssey'])
 for scene in design['scenes']:
  sid=scene['id'];scene['currentScript']='script/revision-v3/narration.ko.json#'+sid
  if sid in gameplay:
   current=gameplay[sid];scene.update(title=current['title'],retainedContent='Core lesson retained; gameplay observations independently rewritten for inspected Nintendo sources',currentOutputReviewed=True)
   scene['learningSteps']=[dict(beat=i+1,explanation=beat) for i,beat in enumerate(current['beats'])]
   scene['transitionToNext']['link']=current['boundaryLink']
   if sid!='01':scene['visualEvidence']=dict(source='sources/media-revision-v3.json',annotationPlan='sources/annotation-plan-v3.json',measuredCutlist='production/revision-v3/timeline.json#cuts',currentMovingReview='current encoded captions/cuts and moving annotation evidence in production/revision-v3/visual-review.json')
  else:
   current=next(s for s in t['scenes'] if s['id']==sid);scene['retainedExplanationEvidence']=current['retainedRender'];scene['currentOutputReviewed']='identical saved explanation and caption local timing; prior review retained'
 design['currentProduction']=dict(measuredTimeline=dict(timeline='production/revision-v3/timeline.json',sha256=sha(HERE/'timeline.json'),fps=60,totalFrames=t['totalFrames'],totalSeconds=t['seconds'],bodyFrames=t['bodyFrames'],actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],ratioErrorFrames=0),sourceVoiceReview='production/revision-v3/narration-review.json',finalAudioReview='production/revision-v3/final-audio-review.json',visualReview='production/revision-v3/visual-review.json',retainedExplanationCount=17,priorVersionEvidence='production/revision-v2/timeline.json',humanWholeListening='pending complete Drive review')
 design['audio']=dict(addedBackgroundMusic=False,gameAudioTargetLufs=-32,narrationTargetLufs=-16,source='quiet synchronized original mixed gameplay track',review='production/revision-v3/final-audio-review.json',humanWholeListening='pending')
 save(P/'planning/production-plan.json',design)
 chapters=[('00:00','같은 각도와 다른 회전 순서')]+[(tc(s['start']),s['title']) for s in t['scenes'] if s['kind']=='explanation' and s['id']!='01']+[(tc((t['totalFrames']-600)/60),'멤버십 감사와 프로그래밍 코칭 안내')]
 old=(P/'publishing/upload-description.ko.txt').read_text(encoding='utf8');footer=old[old.index('🎮 게임 개발은'):]
 credits='게임 화면 출처 / Gameplay recordings\nMario Kart 8 Deluxe — mrlateforschool\nhttps://www.youtube.com/watch?v=dbA2StfJhqw\nThe Legend of Zelda: Tears of the Kingdom — Royalty Free Game Clips\nhttps://www.youtube.com/watch?v=YNQ20CKbY8U\nSuper Mario Odyssey Free To Use Gameplay No Copyright No Commentary #1 — Fox - No Copyright Gameplay (CC BY 4.0)\nhttps://www.youtube.com/watch?v=_wH_-1saHnw\nhttps://creativecommons.org/licenses/by/4.0/\n원본을 발췌·편집하고 설명 표식과 내레이션을 추가했습니다. / Excerpted and edited with instructional annotations and narration.\n게임 IP: Nintendo 및 각 권리자. Nintendo의 후원·공식 제작물이 아닙니다.\n'
 ko='같은 각도인데 왜 회전 순서를 바꾸면 다른 자세가 나올까요? 닌텐도 게임 세 편에서 방향·기울기·중간 자세를 관찰하고, 월드·몸체 좌표계, 짐벌락, 각도 보간과 축–각 표현을 계산까지 연결합니다.\n\n1080p60fps · 실제 게임40% / 설명60%. 추가 배경음악 없이 작은 게임 소리와 내레이션으로 구성했습니다.\n\n챕터\n'+'\n'.join(a+' '+b for a,b in chapters)+'\n\n'+footer+'\n\n'+credits
 en='Why do the same angles give a different orientation when their order changes? Observe direction, tilt and intermediate poses in three Nintendo games, then work through body/world frames, gimbal lock, interpolation and axis–angle.\n\n1920x1080 /60fps. Body:40% independent gameplay and60% authored explanation. No added background music; quiet synchronous game audio beneath Korean narration. Manual Korean and English captions provided.\n\n'+credits+'\nProgramming coaching\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\nCommunity\nhttps://discord.gg/wZuqe7fqkR\nMembership\nhttps://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join\n'
 (P/'publishing/revision-v3-description.ko.txt').write_text(ko,encoding='utf8');(P/'publishing/revision-v3-description.en.txt').write_text(en,encoding='utf8')
 report=dict(schemaVersion=3,slug=P.name,revision='nintendo-annotated-no-bgm-v3',updatedAt=now,status='internal-QA-complete-human-review-pending',integrity=rel(O/'qa/integrity.json'),narrationReview=rel(HERE/'narration-review.json'),finalAudioReview=rel(HERE/'final-audio-review.json'),visualReview=rel(HERE/'visual-review.json'),narrationLevelContinuity=rel(O/'qa/audio-continuity.json'),outputs=integrity['outputs'],frames=t['totalFrames'],actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],humanWholeListening='pending',drive='pending',baselinePreserved=True)
 save(P/'production/qa.json',report)
 (P/'audio/mix-report.md').write_text('# M04 Nintendo revision audio\n\nNo added background music. Narration receives constant scene and global gains; only the quiet native game mix is ducked. The original mixed gameplay track retains its own sounds; effects-only isolation is not claimed.\n\nCurrent complete source/encoded ASR reviews: '+rel(HERE/'final-audio-review.json')+'\n\nLocal source → stem → encoded speech levels and joins: '+rel(O/'qa/audio-continuity.json')+'\n\nExact processing and hashes: '+rel(O/'audio-build.json')+'\n\nHuman whole listening and pronunciation remain pending the complete Drive review.\n',encoding='utf8')
 ledger=read(P/'production/review-ledger.json');ledger.setdefault('previousOutputs',[]).append(ledger.get('currentOutput'));ledger.update(updatedAt=now,currentOutput=report);save(P/'production/review-ledger.json',ledger)
 checkpoint=read(P/'production/checkpoint.json');checkpoint.update(updatedAt=now,stage='internal-QA-complete-four-output-collection',runningJob=None,nextAction='Collect four outputs, upload new complete captioned master to restricted Drive and verify playback; wait for user review');checkpoint.setdefault('delivery',{}).update(newFinalVideoExists=True,driveUploaded=False,youtubeBaselinePreserved=True);save(P/'production/checkpoint.json',checkpoint)
 work=read(R/'shared/publishing/video-worklist.json');row=next(v for v in work['rows'] if v['slug']==P.name);row.update(productionStatus='닌텐도3게임·무BGM 수정본 내부검수 완료',reviewStatus='1080p60·한영자막·표식·음성 기술검수 완료',humanApproval='완성본Drive검수 대기',platformStatus='이전Drive·YouTube비공개 유지 · 새검수본 업로드 준비',executionStatus='선택본 납품 중',localMasterAvailable=True);work['updatedAt']=now;save(R/'shared/publishing/video-worklist.json',work)
 subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'scripts/render-video-worklist.py'],cwd=R,check=True)
 print('Current verified revision registered; prior Drive/YouTube retained.')
if __name__=='__main__':main()
