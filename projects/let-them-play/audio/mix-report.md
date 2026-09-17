# let-them-play v4 — 오디오 믹스 보고서

## 최신 변경: 음성만 ×1.1

2026-09-14 사용자 요청에 따라 정규화된 내레이션에1.1배(+0.82785dB)를 적용했다.
재생 속도는 그대로다. 게임+BGM 배경 스템과 덕킹 기준은 변경하지 않았다.
리미터 이후 최신 AAC 실측은 **-15.83LUFS / -2.06dBTP**. 최종 합산 전체를1.1배 올린 것이 아니다.
MP4 영상 패킷 및 한영 SRT 해시는 동일하고, 전체 디코드와 AAC 패킷 일치 검사를 통과했다.
본편 MP4·편집기PCM에 적용했으며, 기존 버전은 보존했다.
측정/백업: `shared/output/let-them-play/voice-gain-1p1/`의 `report.json`, `before-voice-gain.*`.
새 음량의 최종 청취는 사용자 확인 대기. 아래 표는 변경 전 기본 믹스의 이력이다.

## 변경 전 기본 믹스

2026-09-14 · 전체481.8초 믹스와 MP4 렌더·디코드·AAC 패킷 일치 검사 완료. 사람의 전체 청취 승인은 남아 있다.
기준: `docs/NARRATION_AUDIO_STANDARD.md`, 프로젝트의 승인된 균형형 Qwen3-TTS1.7B 목소리와 Discovery.

## 구성과 실측

| 레이어 | 정규화 목표 | 실제 정규화 결과 |
|---|---:|---:|
| 내레이션 | -16 LUFS | -16.18 LUFS |
| 게임 원음8개 | -23 LUFS | -22.97~-23.18 LUFS |
| Discovery | -28 LUFS | -27.99 LUFS |
| 전체 AAC 믹스 | 피크 -1.5dBTP 이하 | **-16.36 LUFS / -2.15dBTP**, LRA5.3LU |

합산 전 목표와 최종 파일 측정값은 다르다.
채널 변환 뒤 음량이 달라지지 않도록 정규화 측정·처리 모두 스테레오 형식으로 맞췄다.
2패스 loudnorm의 실측 offset을 반영하고, 잔여 오차는 측정 기반 게인 보정과 피크 제한으로 처리했다.
최종 리미터0.75는 AAC 변환 뒤 오버슈트 여유를 확보하기 위한 값이다. TTS 원본의 내용·속도는 바꾸지 않았다.

- 음성은 야숨 영상·설명·2.5D 비교에서 계속 이어진다.
- 각 챕터 끝에 약0.72초의 자연스러운 휴지만 두며, 앞에 예시 길이만큼 무음을 추가하지 않는다.
- Discovery는 처음부터 끝까지 연속. 곡235.30263초, 반복 연결1초 크로스페이드.
- 게임 원음이 있는 동안 BGM만 추가3dB 낮추며 전환0.45초. 음악을 끄지 않는다.
- 게임 원음 페이드: 시작0.12초/끝0.3초.
- 덕킹: threshold0.08, ratio2.2, attack15ms, release280ms.
- 합산은 `amix normalize=0`. 원음 대체 씬 없음.
- 모든8씬의 게임 구간과 설명 구간에서 내레이션·BGM 표본이 존재하며, 게임 구간에는 원음도 확인됐다.
- 편집기 개별 Video 요소만 음소거. 원본 클립 AAC는 보존하며 전체 믹스에서 한 번만 재생한다.

## 결과와 검수 근거

- [전체 측정 JSON](../../../shared/output/let-them-play/final-audio-v4/mix-report.json)
- 원본TTS: `shared/output/narration/let-them-play/qwen3-1.7b-balanced-v1/let-them-play-qwen3-1.7b-balanced-v1.wav`
- AAC마스터: `motion-canvas/src/projects/let-them-play/assets/final-mix.m4a`
- 편집기PCM: `motion-canvas/src/projects/let-them-play/assets/final-mix.wav` — 위 AAC를 디코딩한 같은 믹스.
- 배경 단독: `shared/output/let-them-play/final-audio-v4/background-only.wav`
- 음악 단독: 같은 폴더 `bgm-only-before-narration-ducking.wav`
- 원음 단독: 같은 폴더 `game-only.wav`
- 영상·오디오 재생 검사: `shared/output/let-them-play/final-visual-qa/report.json`
- MP4 패킷/디코드 검사: 같은 폴더의 `render-report.json` 통과. 영상/자막/화면 최종 검토는 `planning/final-review.md`에 기록.

한국어/영어 SRT는 각각120개, 모든 번호·시작·끝 시간을 동일하게 유지한다.
ASR 검토와 남은 청취 항목은 [asr-decisions.md](asr-decisions.md)에 기록했다.
특히08번 끝 문장은 인식됐지만 종결음 감쇠44ms가 자동 기준70ms에 못 미친다.
07번 `컷신`, 08번 종결음 등을 포함해 사람이 전체를 듣고 승인하기 전에는 프로젝트를 complete로 표시하지 않는다.

## 출처

Discovery — Scott Buckley, CC BY4.0, 사용자 선택 승인2026-09-14.
정확한 크레딧·원곡·라이선스·편집 고지는 한글·영문 YouTube 설명란에 넣었다.
Archive64 게임 녹화본의 사용 허용은 `sources/archive64-rights.md`.
**영상 안의 출처·상태 꼬리말과 마지막 크레딧 카드는 없다.**

이전 도입부21.5초 검토 MP4와 World of Longplays 기반 자료는 보존하지만 이 전체 믹스의 입력으로 쓰지 않는다.
