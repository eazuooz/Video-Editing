from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];N=Path(__file__).parent;P=ROOT/'projects/hierarchical-game-outlines'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ko=load(N/'narration.ko.json');en=load(N/'narration.en.json')
ko['scenes'][1]['lines'][2]='지금은 보관함 안에 소리와 리플레이, 기록처럼 관련 항목들이 모여 있습니다. 큰 제목이 먼저 범위를 정하고, 하위 항목이 그 범위를 자세히 나누는 것이죠.'
en['scenes'][1]['lines'][2]='The Vault groups related items such as Sounds, Replays, and Records. The parent sets the scope, while its children divide that scope into more specific parts.'
ko['scenes'][3]['lines'][0]='메뉴를 이해했다면, 이제 캐릭터의 기술 설명에 같은 방법을 적용해 보죠. 화면의 도움말에는 기술 목록이라는 항목도 있습니다. 이를 문서의 구조로 옮겨 보겠습니다.'
en['scenes'][3]['lines'][0]='Now apply the same approach to a fighter’s moves. The Help menu includes a Move List. Let us use that subject to build a document structure.'
for lang,obj in [('ko',ko),('en',en)]:save(N/f'narration.{lang}.json',obj)
m=load(N/'voice-manifest.json')
# This alternate manifest describes only this revision. Baseline receipts remain in project.json.
m['status']='selected-revision-script-ready-for-measured-voice'
for k in ['finalRender','visualDepthRevision','publishingHistory']:m.pop(k,None)
m['publishing']={'privacyStatus':'private','uploaded':False,'actualVideoId':None,'scheduled':False,'baselineVideoId':'jBRt3xatdPk','baselineUnchanged':True}
m['approvals']={'voiceSample':'reuse-approved-Qwen3-TTS-1.7B-reference','script':'source-aligned-paired-review','final':'pending','humanListening':False,'publicRights':False}
m['editing']['actualGameplaySeconds']=None;m['editing']['actualExplanationSeconds']=None
m['editing']['timingStatus']='pending-measured-current-voice'
music=load(P/'production/manual-preflight-v1/music-rights.json')
m['audio']['backgroundMusic']={'title':music['track'],'artist':music['artist'],'file':music['file'],'license':music['license'],'licenseRecord':(P/'production/manual-preflight-v1/music-rights.json').relative_to(ROOT).as_posix(),'attribution':music['attribution'],'selection':'within-user-approved-low-lofi-style; existing 46.683s comparison retained; new mix listening pending'}
m['audio']['bgmTargetLufs']=-31
m['audio']['sourceAudioPolicy']='Preserve quiet mixed native menu UI/music on selected game cuts; do not claim isolated sound effects. Lower lo-fi during native audio. Private editorial review; third-party capture/public music rights remain explicitly pending.'
save(N/'voice-manifest.json',m)
p=load(P/'planning/production-plan.json');p['scripts']['status']='source-aligned-paired-text-reviewed; normal source playback completion pending';p['reference']['modernFootageSelected']=True
p['reference']['versionSelection']='Retain Smash Ultimate, the same reference game. Independently recorded menu capture visibly shows 1.1.0; neither latest patch nor new mechanics are claimed.'
p['audio'].update(policy='lecture-lofi-game-audio-v1 applied to this selected revision',selectedTrack=music['track'],sourceSfxAvailability=m['audio']['sourceAudioPolicy'])
p['nextAction']='Finish bounded normal menu playback, internal caption preflight and current duplicate check; then synthesize the eight new scene texts once.'
save(P/'planning/production-plan.json',p)
print('Updated only observed Vault/Help claims, aligned KO/EN, and cleared stale baseline completion fields from alternate voice manifest.')
