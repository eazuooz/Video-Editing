"""Apply only the user's lecture audio correction; preserve unrelated edits."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[4]
POLICY='lecture-no-added-bgm-standard-game-audio-v3'
FILES=['AGENTS.md','docs/VIDEO_WORKFLOW.md','docs/NARRATION_AUDIO_STANDARD.md','templates/video-project/project.json','shared/publishing/video-production-control.json']
def transform(path,text):
 if path.endswith('.json'):
  d=json.loads(text)
  if path.startswith('templates/'):
   a=d['audio']['lectureDefaults'];a.update(policyId=POLICY,gameAudioTargetLufs=d['audio']['gameAudioTargetLufs'],gameAudioNarrationRelativeDb=None,gameAudioUnderNarrationDb=d['audio']['gameAudioUnderNarrationDb'],gameAudio='Preserve synchronized original game sound using the standard game-audio profile; no lecture-specific attenuation. Remove only separately added BGM.',ducking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1))
  else:
   a=d['lectureAudioPolicy'];a.update(id=POLICY,userEvidence='게임사운드는 원래 영상 제작규칙 처럼 살려줘. 강의영상은 배경음악만 제거하는거야',scope='Selected/new lectures remove only separately added BGM. Preserve synchronized original game audio using the normal production profile; no lecture-only extra attenuation. Unselected deliveries unchanged.',gameAudioInitialTargetLufs=-23,gameAudioNarrationRelativeDb=None,gameAudioUnderNarrationDb=-10,supersedes='lecture-no-bgm-quiet-game-audio-v2',standardDucking=dict(threshold=.08,ratio=2.2,attackMs=15,releaseMs=280,makeup=1))
  return json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 lines=text.splitlines()
 for i,line in enumerate(lines):
  if path=='AGENTS.md' and line.startswith('- Lecture audio, user-directed2026-10-19:'):
   lines[i]='- Lecture audio, clarified by the user2026-10-19: `'+POLICY+'` replaces the lecture-specific quiet-game profile. Remove only separately added background music; preserve synchronized original game sound using the ordinary production profile (game stem starts at-23LUFS; narration-16LUFS, usual speech-driven game ducking). Do not apply extra attenuation or mute the game merely because this is a lecture. Preserve useful effects/ambience and approved original mixed game audio; record silent sources and separation limits honestly, never invent missing source sound. Preserve approved PCM and praised explanations. Applies to the selected/new lectures only; unselected deliveries and game-design music unchanged. See `docs/NARRATION_AUDIO_STANDARD.md`.'
  if path=='docs/VIDEO_WORKFLOW.md':
   if line.startswith('| 음성·음악 |'):
    lines[i]=line.replace('강의는 배경음악 없이 내레이션 우선, 실제 게임 효과음·환경음은 작게 유지.','강의는 추가 배경음악만 제거하고 게임 원음은 일반 영상의 기존 믹스 기준으로 유지. 강의 전용 추가 감쇠·전체 원음 음소거 금지.')
   if line.startswith('강의 오디오는2026-10-19 사용자 지시'):
    lines[i]='강의 오디오는2026-10-19 사용자 정정 “게임사운드는 원래 영상 제작규칙 처럼 살려줘. 강의영상은 배경음악만 제거하는거야”에 따라 `'+POLICY+'`를 적용한다. **따로 추가한 배경음악만 제거하고 실제 게임 소리는 기존 일반 영상 제작 기준으로 살린다.** 내레이션-16LUFS·게임 원음-23LUFS를 시작값으로 삼고 기존 발화 기반 덕킹(threshold0.08/ratio2.2/attack15ms/release280ms)을 게임 트랙에만 적용한다. 강의라는 이유로-30/-32LUFS·추가14dB 감쇠를 별도로 강제하거나 원음을 통째로 지우지 않는다. 효과음·환경음과 사용 조건을 확인한 원래 게임 믹스를 동기화해 보존하고 원본부터 무음인 구간·음악 분리 한계는 기록한다. 없는 효과음을 임의로 만들지 않는다. 이전 강의용 저음량 프로필을 대체하고 미선택 납품·예약·게임디자인 음악은 변경하지 않는다. 기존30–60초 비교·음량 급락·최종 믹스 검수에 통합한다. 상세는 [오디오 규격](NARRATION_AUDIO_STANDARD.md)을 따른다.'
  if path=='docs/NARRATION_AUDIO_STANDARD.md':
   if line.startswith('강의 기본값은2026-10-19'):
    lines[i]='강의 기본값은2026-10-19 사용자 정정 “게임사운드는 원래 영상 제작규칙 처럼 살려줘. 강의영상은 배경음악만 제거하는거야”에 따라 `'+POLICY+'`다. **따로 추가한 BGM만 빼며 게임 원음은 기존 일반 영상 제작 기준으로 보존한다.** 내레이션-16LUFS·게임 원음-23LUFS를 초기값으로 삼아 효과음 식별성과 발화 명료성을 확인한다. 기존 덕킹은 게임 트랙에만 적용한다. 강의용-30/-32LUFS·발화 대비14dB 추가 감쇠 프로필은 폐기한다. 내레이션이나 게임 원음 전체를 무음으로 만드는 규칙이 아니다. 기존 미선택 납품·예약·게임디자인의 승인 음악 계약은 변경하지 않는다.'
   if line.startswith('게임 효과음·환경음은 원래 동작과 동기화해 유지한다.'):
    lines[i]='게임 효과음·환경음은 원래 동작과 동기화해 기존 일반 영상 수준으로 살린다. 중요한 조작/타격/UI 소리는 식별 가능하게 유지하고 실제 발화와 경쟁하는 순간에만 기존 덕킹으로 조절한다. 사용 조건을 확인한 원래 게임 믹스는 강의라는 이유로 통째로 삭제하거나 추가 감쇠하지 않는다. 원본 해설 등 경쟁 음성은 별도 검토하고, 효과음과 게임 자체 음악의 분리 여부를 정직하게 기록한다. 원본부터 무음인 자료에는 없는 소리를 합성해 원음 복원이라고 하지 않는다. 원본 파일은 보존한다.'
   if line.startswith('| 내레이션 / 비강의 게임 원음 |'):
    lines[i]='| 내레이션 / 게임 원음(강의 포함) | -16 / -23 LUFS; 기존 승인 계약과 실제 효과음에 맞춰 조정 |'
   if line.startswith('| 강의 배경음악 / 게임 원음 |'):
    lines[i]='| 강의 배경음악 / 게임 원음 | 추가 BGM만 없음 / 일반 영상과 동일한 게임 원음·덕킹 기준; 강의 전용 추가 감쇠 없음 |'
   if line.startswith('위 LUFS는 레이어 정규화 시작값'):
    lines[i]=line.replace('게임 자체 음악이 섞인 원음은 무음악 원본이나 검증된 분리를 우선하고 처리 한계를 기록한다.','게임 자체 음악이 섞인 원음은 사용 조건과 처리 한계를 기록하며, 강의 무BGM 요청을 원음 전체 삭제로 해석하지 않는다.')
 return '\n'.join(lines)+'\n'

if __name__=='__main__':
 for name in FILES:
  p=R/name;p.write_text(transform(name,p.read_text(encoding='utf8')),encoding='utf8')
 print('Updated lecture audio policy only; unrelated text retained.')
