"""Record measured local delivery facts; never turn unresolved review into pass."""
from pathlib import Path
import json,datetime,hashlib
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
PROJECT=ROOT/f'projects/{SLUG}';OUT=ROOT/f'shared/output/{SLUG}'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
m=read(PROJECT/'project.json');data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
media=read(ROOT/f'motion-canvas/src/projects/{SLUG}/media.json');assembly=read(OUT/'assembly.json')
integrity=read(OUT/'encoded-integrity.json');captions=read(OUT/'caption-pixel-qa/report.json')
audio=read(OUT/'audio/mix-report.json');levels=read(OUT/'audio/level-continuity.json')
asr=read(OUT/'audio/final-asr/complete-readback.json');motion=read(OUT/'encoded-motion-review/review.json')
assert integrity['identicalAAC'] and captions['status']=='pass'
assert all(x['fullVideoDecode']=='pass' and x['fullAudioDecode']=='pass' and x['pts']=='pass' for x in integrity['outputs'])
assert asr['sourceSha256']==audio['mixSha256']
assert asr['fullTextReview']!='pending','Read current complete encoded narration before delivery'
assert motion['status']!='pending-direct-visual-review','Review actual current motion/contact evidence'
body=assembly['frames']-720;commercial=0;development=0;craft=0;roles=[]
plan=read(PROJECT/'planning/actual-footage-plan.json')
for s in data['scenes']:
 frames=round(s['duration']*60);cuts=[c for c in plan['cuts'] if c['scene']==s['id']]
 game=sum(c['frames'] for c in cuts if c['source']=='wow');dev=sum(c['frames'] for c in cuts if c['source'] in ('ue','ai','godot','krita','mix1','mix2'));other=sum(c['frames'] for c in cuts if c['source'] in ('wood','wood2','robot','road'))
 commercial+=game;development+=dev;craft+=other
 roles.append({'scene':s['id'],'frames':frames,'commercialGameplayFrames':game,'externalDevelopmentDemoFrames':dev,'independentCraftHistoryFrames':other,'explanationFrames':frames-game-dev-other})
actual=commercial+development+craft;assert actual==plan['actualFrames'] and abs(actual-body*.6)<=1
ratio={'status':'pass','requiredActualShare':.6,'bodyFrames':body,'actualFrames':actual,'actualShare':actual/body,'commercialGameplayFrames':commercial,'externalDevelopmentDemoFrames':development,'independentCraftHistoryFrames':craft,'selfAuthoredUnityClassifiedAs':'explanation','paddingAdded':False,'latestUserSteering':'actual footage60%; no Unity majority requirement; agent chooses quality','scenes':roles}
write(OUT/'screen-role-measurement.json',ratio)
m['status']='drive-review-candidate';m['publishReady']=False;m['video']['durationSeconds']=assembly['duration']
m['paths'].update(captionsKo=f'shared/output/{SLUG}/final.ko.srt',captionsEn=f'shared/output/{SLUG}/final.en.srt',editorAudioMix=f'motion-canvas/src/projects/{SLUG}/assets/final-mix.wav')
m['membershipOutro'].update(appliedToFinal=True,renderStatus='rendered-original-identities-10s')
m['editing'].update(timingStatus='measured-and-asr-aligned',actualGameplaySeconds=commercial/60,actualCommercialGameplaySeconds=commercial/60,actualDevelopmentFootageSeconds=development/60,actualCraftHistorySeconds=craft/60,actualExplanationSeconds=(body-actual)/60,actualFootageShare=actual/body,actualGameplayShare=commercial/body,ratioVerification=ratio)
m['audio'].update(mixStatus='encoded-and-technically-reviewed',mixEvidence=f'shared/output/{SLUG}/audio/mix-report.json',levelContinuityEvidence=f'shared/output/{SLUG}/audio/level-continuity.json',humanListening='pending',bgmTargetLufs=-31)
issues=['사람의 전편 청취·발음 검수와 해당 Drive 버전 승인은 대기 중입니다.','03장 첫 단어 지금까지는의 ASR 차이 등 고유명사·발음은 실제 청취 확인이 필요합니다.']
if levels['sourceLowLevelFlags']:issues.append(f"원본 음성의 국소 레벨 의심 구간{len(levels['sourceLowLevelFlags'])}곳은 실제 청취 확인이 필요합니다.")
if levels['processingAttenuationStatus']!='pass':issues.append('믹스 처리에 따른 음량 차이 의심 구간은 추가 확인이 필요합니다.')
m['finalRender']={'completedAt':now,'frames':assembly['frames'],'width':1920,'height':1080,'fps':60,'technicalIntegrity':'pass','captionPixelIntegrity':'pass','completeEncodedAsrReview':asr['fullTextReview'],'motionReview':motion['status'],'knownIssues':[],'openItems':issues,'reviewBoundary':'Google Drive; YouTube upload waits for user review'}
write(PROJECT/'project.json',m)
report=['# 현재 검수본의 오디오','',f"최종 길이: {assembly['duration']:.3f}초. 인코딩 믹스: {audio['encodedMix']['input_i']} LUFS / {audio['encodedMix']['input_tp']} dBTP.",'','원본 Qwen PCM을 보존하고 문단별 발화 게인과 짧은 피크 보호를 적용해 테이크 내부의 점진적 음량 감소를 보정했습니다. 음악만 음성에 따라 낮추고 목소리는 덕킹하지 않았습니다. Wholesome의 시작 레벨은−31 LUFS, 발화 중 추가감쇠는6dB입니다.','',f"전체 발화의400ms창/100ms간격 비교: 믹스 감쇠검사 {levels['processingAttenuationStatus']}, 원본 국소레벨 의심 {len(levels['sourceLowLevelFlags'])}곳. 실제 사람 청취는 pending입니다.",'','증거는 아래 기존 작업 폴더에 있습니다.','',f'- `shared/output/{SLUG}/audio/mix-report.json`',f'- `shared/output/{SLUG}/audio/level-continuity.json`',f'- `shared/output/{SLUG}/audio/final-asr/complete-readback.json`','','원본 개발·게임 소스의 별도 음악/해설은 제외했습니다. 상점 보상음은 동작 시각에 맞춘 자체 제작 효과음이며 원본 게임 음향 보존으로 표시하지 않습니다.']
(PROJECT/'audio/mix-report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
print(json.dumps({'duration':assembly['duration'],'actualShare':actual/body,'commercialShare':commercial/body,'developmentShare':development/body,'ratio':'pass','publishReady':False}))
