"""Register only the current verified revision; retain the private baseline."""
from pathlib import Path
import json,datetime,hashlib,subprocess
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def timecode(s):
 n=int(s);h,n=divmod(n,3600);m,n=divmod(n,60);return f'{h}:{m:02}:{n:02}' if h else f'{m:02}:{n:02}'
def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
 timeline=read(P/'production/revision-v2/timeline.json');integrity=read(O/'qa/integrity.json');pair=read(O/'pair-source.json')
 for result in integrity['outputs']:
  kind=result['kind'];assert result['fullDecodePassed'] and result['ptsMonotonicAndUniform'];assert sha(O/f'euler-{kind}.mp4')==result['sha256']==pair['outputs'][kind]['sha256']
 assert integrity['ratioErrorFrames']==0 and timeline['actualFrames']*3==timeline['explanationFrames']*2
 source_review=read(P/'production/revision-v2/narration-review.json');final_review=read(P/'production/revision-v2/final-audio-review.json');visual=read(P/'production/revision-v2/visual-review.json')
 assert source_review['directWholeTextReviewed'] and final_review['directWholeTextReviewed']
 assert visual['currentCaptionAndCutPixelsReviewed'] and visual['movingExplanationsAndAnnotationsReviewed'] and visual['nativeAndMobileReviewed']
 assert final_review['captionedVideoSha256']==pair['outputs']['captioned']['sha256'] and visual['captionedVideoSha256']==pair['outputs']['captioned']['sha256']
 audio=read(O/'audio-build.json');levels=read(O/'qa/audio-continuity.json')
 assert not levels['flaggedVoiceTransferWindows'],'Resolve voice attenuation before registering final output'
 assert final_review['narrationLevelContinuityStatus'] in ['pass','pass-with-natural-prosody-evidence'],'Unresolved local level candidates'
 p=read(P/'project.json');preferred=next(t['title'] for t in read(P/'publishing/revision-v2-plan.json')['titleCandidates'] if t['preferred'])
 p['revision']['baselineTitle']=p['revision'].get('baselineTitle',p['titles']['ko']);p['titles']=dict(ko=preferred,en='Why Does Rotation Order Change the Result? | Euler Angles and Axis–Angle')
 p.update(status='complete-local-revision-awaiting-drive-review',publishReady=False)
 p['video'].update(width=1920,height=1080,fps=60,durationSeconds=timeline['totalFrames']/60)
 p['editing'].update(timingStatus='revision-v2-measured-and-verified',actualGameplaySeconds=timeline['actualFrames']/60,actualExplanationSeconds=timeline['explanationFrames']/60,actualGameplayShare=.4,actualCommercialGameplaySeconds=timeline['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,finalBodyFrames=dict(total=timeline['bodyFrames'],actual=timeline['actualFrames'],explanation=timeline['explanationFrames'],ratioErrorFrames=0))
 p['editing']['openingOverview']['narrationSeconds']=timeline['scenes'][0]['voiceSeconds'];p['editing']['exampleInterleaving']['reviewStatus']='revision-v2-reviewed-current-native-footage-and-moving-composite'
 p['tts'].update(outputDir='shared/output/narration/game-math-euler-axis-angle/teaching-rules-v2',filenameStem='euler-teaching-v2',sceneGapSeconds=.3,maxNewTokens=2048)
 p['audio'].update(mixStatus='current-encoded-mix-ASR-and-level-reviewed-human-whole-listening-pending',narrationTargetLufs=-16,bgmTargetLufs=-31,bgmPlacement='continuous-body-voice-ducked',backgroundMusic=dict(enabled=True,required=True,policy='lecture-lofi-game-audio-v1',track=rel(R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'),actualFileSha256=audio['music']['sourceSha256'] if 'music' in audio and 'sourceSha256' in audio['music'] else sha(R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'),humanWholeListening='pending'),sourceAudioPolicy='Two native FHD60 independent gameplay sources contain no audio; narration plus rights-recorded instrumental only.')
 p['audio']['musicFallbackScenes']=[s['id'] for s in timeline['scenes'] if s['kind']=='actual']
 manifest=read(P/'production/revision-v2/tts-manifest.json')
 p['revision']['baselinePaths']=p['revision'].get('baselinePaths',dict(p['paths']))
 for key in ['motionCanvasProject','sharedLectureBuilder','sharedManimLesson']:p['paths'].pop(key,None)
 p['paths'].update(videoClean=rel(O/'euler-clean.mp4'),videoBurnedCaptions=rel(O/'euler-captioned.mp4'),captionsKo=rel(O/'captions.ko.srt'),captionsEn=rel(O/'captions.en.srt'),audioMix=rel(O/'final-mix.m4a'),editorAudioMix=rel(O/'final-mix.wav'),narration=manifest['tts']['outputDir']+'/'+manifest['tts']['filenameStem']+'.wav',timeline=rel(P/'production/revision-v2/timeline.json'),productionBuilder=rel(P/'production/revision-v2/render-edit.py'),audioReport=rel(P/'audio/mix-report.md'),renderReport=rel(P/'production/qa.json'),publishingKo=rel(P/'publishing/revision-v2-description.ko.txt'),publishingEn=rel(P/'publishing/revision-v2-description.en.txt'),footageCuts=rel(P/'production/revision-v2/timeline.json'))
 p['paths'].update(manimProject=rel(P/'production/revision-v2/math_visuals.py'),unityScenePlan='unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/scene-plan.json',productionReadme=rel(P/'production/revision-v2/README.md'))
 p['rendererDecision']=dict(selected='Unity spatial explanations + Manim mathematical diagrams + FFmpeg composition',unityEditor='6000.6.0f1',capturePipeline='isolated built-in renderer',sourcePipeline='URP17.6',manim='0.20.1/Cairo',reason='Detailed spatial body/world frames, mathematical calculation and code each use their suitable renderer. Self-authored Unity footage remains explanation.')
 p['publishing'].update(baseline=dict(videoId='iv9esV7vv_g',url='https://youtu.be/iv9esV7vv_g',visibility='private',receipt='publishing/youtube-upload.json',preserved=True),privateUploadComplete=False,fullPublishingSettingsComplete=False,videoId=None,url=None,receipt=None,verifiedAtUtc=None,driveFinalReviewRequired=True,youtubeReplacementAuthorized=False,currentRevision='teaching-rules-v2')
 p['approvals'].update(humanListening='pending full user review',visualPixelReview='current full caption/cut/diagram/annotation reviewed at native/mobile sizes',privateUpload='Await final user review of this exact Drive version; baseline replacement not authorized')
 p['finalRender']=dict(status='current-local-revision-internal-QA-complete',currentRevisionComplete=True,durationSeconds=timeline['totalFrames']/60,fps=60,backgroundMusic=True,qa=rel(P/'production/qa.json'),openItems=['완성본 Drive 사용자 검수와 전체 청취·발음 확인 대기','공개 전 게임 IP 권리 확인 상태 검토','기존 비공개 YouTube 본문 교체·삭제 미허가'])
 if p['membershipOutro'].get('truncatedHandlesReview')=='pending':p['finalRender']['openItems'].append('기존 원본 회원 목록의 잘린 표시명 확인 대기')
 p['membershipOutro']['appliedToFinal']=True;save(P/'project.json',p)
 chapters=[('00:00','같은 각도와 다른 회전 순서')]+[(timecode(s['start']),s['title']) for s in timeline['scenes'] if s['kind']=='explanation' and s['id']!='01']+[(timecode((timeline['totalFrames']-600)/60),'멤버십 감사와 프로그래밍 코칭 안내')]
 old=(P/'publishing/upload-description.ko.txt').read_text(encoding='utf8');footer=old[old.index('🎮 게임 개발은'):]
 ko='같은 각도를 넣어도 회전 순서가 바뀌면 자세가 달라지는 이유를 살펴봅니다. 실제 비행에서 몸통과 기울기를 관찰하고, 월드·몸체 좌표계, 짐벌락, 각도 보간과 축·각 표현을 계산까지 연결합니다.\n\n실제 게임40%·설명60%, 1080p60fps 강의입니다. 내레이션에 작은 기악 배경음악을 더했습니다.\n\n챕터\n'+'\n'.join(a+' '+b for a,b in chapters)+'\n\n'+footer+'\n\n게임 화면: Superflight / GrizzlyGames · 기록: Morkala\nhttps://www.youtube.com/watch?v=FvSgGn941U0\nhttps://www.youtube.com/watch?v=sjRiPTjCBYo\n음악: Nimbus — Eveningland / YouTube Audio Library\n'
 (P/'publishing/revision-v2-description.ko.txt').write_text(ko,encoding='utf8')
 en='Why can the same angles produce a different orientation when their order changes? Observe real flight, distinguish body and world frames, then work through gimbal lock, angle interpolation, axis–angle and rotation vectors.\n\n1920x1080 /60fps. Body:40% independent gameplay,60% authored explanation. Quiet instrumental background beneath Korean narration. Manual Korean and English captions accompany this version.\n\nGameplay: Superflight / GrizzlyGames; recording by Morkala\nhttps://www.youtube.com/watch?v=FvSgGn941U0\nhttps://www.youtube.com/watch?v=sjRiPTjCBYo\nMusic: Nimbus — Eveningland / YouTube Audio Library\n\nProgramming coaching\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\n'
 en+='\nYamYam Coding community\nhttps://discord.gg/wZuqe7fqkR\nMembership\nhttps://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join\n'
 (P/'publishing/revision-v2-description.en.txt').write_text(en,encoding='utf8')
 report=dict(schemaVersion=2,slug=P.name,revision='teaching-rules-v2',updatedAt=now,status='internal-QA-complete-human-review-pending',integrity='production/local/revision-v2/qa/integrity.json',narrationReview='production/revision-v2/narration-review.json',finalAudioReview='production/revision-v2/final-audio-review.json',visualReview='production/revision-v2/visual-review.json',narrationLevelContinuity='production/local/revision-v2/qa/audio-continuity.json',outputs=integrity['outputs'],frames=timeline['totalFrames'],actualFrames=timeline['actualFrames'],explanationFrames=timeline['explanationFrames'],humanWholeListening='pending',drive='pending',baselinePreserved=True)
 save(P/'production/qa.json',report)
 (P/'audio').mkdir(exist_ok=True);(P/'audio/mix-report.md').write_text('# M04 teaching-rules-v2 audio\n\nCurrent source and encoded-mix ASR direct whole-text reviews: '+rel(P/'production/revision-v2/final-audio-review.json')+'\n\nSame-speech400ms/100ms source → stem → encoded level analysis: '+rel(O/'qa/audio-continuity.json')+'\n\nVoice gain is constant per scene plus one global gain and a short peak limiter. Only the instrumental music is ducked; native source gameplay has no audio. Exact processing and hashes: '+rel(O/'audio-build.json')+'\n\nHuman whole listening and pronunciation remain pending the complete Drive review.\n',encoding='utf8')
 ledger=read(P/'production/review-ledger.json');ledger['updatedAt']=now;ledger['currentOutput']=report;save(P/'production/review-ledger.json',ledger)
 checkpoint=read(P/'production/checkpoint.json');checkpoint.update(updatedAt=now,stage='internal-QA-complete-four-output-collection',runningJob=None,nextAction='Collect four current outputs, upload exact captioned master to Google Drive and verify access/playback; stop for human review');checkpoint['delivery'].update(newFinalVideoExists=True,driveUploaded=False,youtubeBaselinePreserved=True);save(P/'production/checkpoint.json',checkpoint)
 work=read(R/'shared/publishing/video-worklist.json');row=next(v for v in work['rows'] if v['slug']==P.name);row.update(productionStatus='새규칙 수정본 내부검수 완료',reviewStatus='1080p60·한영자막·전체디코드·음성/화면 기술검수 완료',humanApproval='완성본Drive검수 대기',platformStatus='기존YouTube비공개 유지 · 수정본Drive 업로드 준비',executionStatus='선택본 납품 중',localMasterAvailable=True);work['updatedAt']=now;save(R/'shared/publishing/video-worklist.json',work)
 subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'scripts/render-video-worklist.py'],cwd=R,check=True)
 print(json.dumps(dict(status=p['status'],frames=timeline['totalFrames'],youtubeModified=False)))
if __name__=='__main__':main()
