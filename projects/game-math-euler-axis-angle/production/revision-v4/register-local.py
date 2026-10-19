"""Register current audio-only masters after direct ASR and technical review."""
from pathlib import Path
import json,datetime,subprocess,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v4-clarity'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
integrity=read(O/'qa/integrity.json');proof=read(H/'video-reuse-proof.json');audio=read(O/'audio-build.json');review=read(H/'audio-review.json');pair=read(O/'pair-source.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert all(x['fullDecodePassed'] and x['ptsMonotonicAndUniform'] for x in integrity['outputs'])
assert all(x['exactCompressedVideoStreamEqual'] for x in proof['streams'])
assert review['directWholeEncodedTextCompared'] and review['unresolvedConfirmedContentErrors']==0
assert review['captionedSha256']==pair['outputs']['captioned']['sha256'] and review['narrationStemUnchanged']
project=read(P/'project.json');previous=project['revision']['id'];project['revision']['id']='standard-game-audio-v4'
project['revision']['revisionScope']='Only game-sound gain and ordinary ducking restored; no added BGM. Exact narration PCM, video packets, captions and scene timing preserved.'
project['revision']['nextRevision']=dict(id='standard-game-audio-v4',stage='local-QA-complete-awaiting-Drive')
project['audio'].update(mixStatus='standard-game-audio-restored-technical-reviewed-human-listening-pending',gameAudioTargetLufs=-23,sourceAudioPolicy='Normal production game sound; synchronized native mixed audio with ordinary speech-driven ducking. Mario Kart supplied capture is silent. No synthetic effects or added BGM.',backgroundMusic=dict(enabled=False,required=False,policy='lecture-no-added-bgm-standard-game-audio-v3'))
project['audio']['duckingThreshold']=.08;project['audio']['duckingRatio']=2.2
for key,name in [('videoClean','euler-clean.mp4'),('videoBurnedCaptions','euler-captioned.mp4'),('audioMix','final-mix.m4a'),('editorAudioMix','final-mix.wav'),('captionsKo','captions.ko.srt'),('captionsEn','captions.en.srt')]:project['paths'][key]=rel(O/name)
project['paths']['productionBuilder']=rel(H/'remix.py');project['status']='local-audio-revision-complete-awaiting-Drive';project['publishReady']=False
project['publishing'].update(currentRevision='standard-game-audio-v4',youtubeReplacementAuthorized=False)
project['finalRender'].update(status='audio-only-revision-internal-QA-complete',currentRevisionComplete=True,openItems=['현재 v4 Drive 최종 검수본 업로드와 사용자 전체 청취 대기','기존 모든 Drive·비공개 YouTube 버전 유지'])
for lang in ['ko','en']:
 text=(P/f'publishing/revision-v3-description.{lang}.txt').read_text(encoding='utf8')
 if lang=='ko':text=text.replace('추가 배경음악 없이 작은 게임 소리와 내레이션으로 구성했습니다.','추가 배경음악 없이 원래 게임 소리와 내레이션으로 구성했습니다.')
 else:
  text=text.replace('quiet synchronous game audio','synchronized original game audio')
  begin=text.index('게임 화면 출처 / Gameplay recordings');footer=text.index('Programming coaching',begin)
  text=text[:begin]+text[footer:].rstrip()+'\n\n'+text[begin:footer].strip()+'\n'
 target=P/f'publishing/revision-v4-description.{lang}.txt';target.write_text(text,encoding='utf8');project['paths']['publishing'+('Ko' if lang=='ko' else 'En')]=rel(target)
save(P/'project.json',project)
qa=dict(schemaVersion=4,slug=P.name,revision='standard-game-audio-v4',updatedAt=now,status='technical-and-reused-visual-checks-complete-human-listening-pending',integrity=rel(O/'qa/integrity.json'),audioReview=rel(H/'audio-review.json'),visualReuse=rel(H/'video-reuse-proof.json'),outputs=integrity['outputs'],humanWholeListening='pending',drive='pending v4 upload',baselinePreserved=True)
save(P/'production/qa.json',qa)
ledger=read(P/'production/review-ledger.json')
if ledger.get('currentOutput',{}).get('revision')!='standard-game-audio-v4':ledger.setdefault('previousOutputs',[]).append(ledger.get('currentOutput'))
ledger.update(updatedAt=now,currentOutput=qa);save(P/'production/review-ledger.json',ledger)
plan=read(P/'planning/production-plan.json');plan.update(revision='standard-game-audio-v4',updatedAt=now,status='local-audio-only-QA-complete-awaiting-Drive')
plan['audio']=dict(addedBackgroundMusic=False,gameAudioTargetLufs=-23,narrationTargetLufs=-16,narrationUnchanged=audio['narrationUnchanged'],gameSourceLimit='Mario Kart independent capture is silent; Zelda and Odyssey original mixed game sound retained. No effects-only isolation claim.',review='production/revision-v4/audio-review.json',humanWholeListening='pending')
plan['selectedRevision']['stage']='audio-only revision; existing scene design retained'
plan['currentProduction'].update(finalAudioReview='production/revision-v4/audio-review.json',visualReuse='production/revision-v4/video-reuse-proof.json',humanWholeListening='pending complete v4 Drive review');save(P/'planning/production-plan.json',plan)
(P/'audio/mix-report.md').write_text('# M04 game sound correction\n\nOnly separately added BGM is disabled. Standard game-sound target-23LUFS and ordinary speech-driven ducking restored. Narration PCM and compressed video streams are identical to v3. The Mario Kart capture is silent from its original source; other games retain their synchronous original mixed sound.\n\nCurrent measurements and direct encoded ASR review: production/revision-v4/audio-review.json. Full pair integrity: production/local/revision-v4/qa/integrity.json.\n\nHuman whole listening and subjective pronunciation remain pending.\n',encoding='utf8')
checkpoint=read(P/'production/checkpoint.json');checkpoint.update(updatedAt=now,revision='standard-game-audio-v4',stage='local-audio-only-QA-complete-awaiting-Drive',runningJob=None,nextAction='Collect four outputs and upload current captioned master to restricted Drive; no YouTube or next video.',lastCompletedCommit='5ec3f95cf4b217e0afcd26093388ff78c8b72ceb')
checkpoint['currentMaster']['outputs']=pair['outputs'];checkpoint['currentMaster']['status']='audio-only revision; exact reviewed video streams and narration retained'
checkpoint['delivery']['driveUploaded']=False;checkpoint['delivery']['pendingRevision']='standard-game-audio-v4';save(P/'production/checkpoint.json',checkpoint)
print('Current v4 local masters registered; previous Drive review preserved until new upload verified.')
