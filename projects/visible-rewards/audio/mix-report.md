# 왜 조금만 더 하게 될까? | 보상이 보이는 게임 디자인 — 오디오 믹스 보고서

- 프로젝트: `visible-rewards`
- 검수일: 2026-09-16 (기술 검사)
- 현재 상태: A 내레이션 + 게임 원음 + 연속 Wanderlust 전체 믹스와 MP4 생성, 편집기 재생 확인. 전체 사람 청취 승인 대기.
- 기준: 저장소의 `docs/NARRATION_AUDIO_STANDARD.md`

## 설정

### 2026-09-16 전체 믹스 v1 (현재 사용)

- 믹서: `qwen3-tts/mix_visible_rewards_final.py`.
- 길이: 375.766667초, 60fps 22,546프레임. 기존 TTS는 변경하지 않고 끝의 6.6ms만 영상 길이에 맞게 패딩.
- 입력: 승인된 A 내레이션 전용 WAV, Wanderlust 공식 MP3, 실제 게임 클립 8개. 기존 BGM 검토본을 다시 더하지 않음.
- 게임 원음: -23 LUFS 시작점. 외국어 해설이 있는 Khittisun 녹화 컷은 -31 LUFS로 낮춰 우리 대사와 경쟁을 줄임.
- BGM: 전체 연속 -28 LUFS 시작점, 게임 소리가 있는 19.5초 구간에는 0.45초 램프로 추가 -3dB. 끄지 않음.
- 원음·BGM을 합친 배경에 내레이션 사이드체인. 모든 amix normalize=0. 원본 클립 오디오는 유지하고 편집기의 개별 Video만 muted.
- WAV 실측: **-15.68 LUFS / -3.10 dBTP**.
- AAC 실측: **-15.73 LUFS / -3.11 dBTP**. 48kHz stereo, 목표 192kbps VBR.
- 배경/음악/게임 단독 × 8씬 × 예시·설명 = 48개 표본 검사. 음악과 전체 배경은 전 구간 비무음, 게임 원음은 예시에만 존재.
- 편집기 `final-mix.wav`: 375.766667초, muted=false, volume=1, 재생 시간 증가 확인.
- Motion Canvas 8개 독립 씬 시작/끝, 총 22,546프레임이 실측 타이밍과 일치. 24개 화면 캡처 확인.
- 모든 합산 피크는 -1.5dBTP 이하. 사람이 전체를 들어본 승인과는 별개이며 `finalListening=pending` 유지.

현재 산출물:

- 편집기 WAV/M4A: `motion-canvas/src/projects/visible-rewards/assets/final-mix.wav`, `final-mix.m4a`.
- 전체/원음/음악/배경 단독과 측정 JSON: `shared/output/visible-rewards/audio-final-v1/`.
- 화면 QA: `shared/output/visible-rewards/visual-qa-v1/report.json`, `contact.png`.
- 최종 렌더 검사는 같은 디렉터리의 `render-report.json`을 확인. 없으면 MP4 완료로 판단하지 않음.
- 한영 SRT 각 94개 타임코드 불변, 마지막 종료 375.740초.
- 최종 MP4: 1920×1080 / 60fps / H.264 + AAC / 375.766667초 / 22,546프레임 / 138,772,995 bytes.
- 전체 디코딩 오류 없음. MP4와 마스터 M4A의 AAC 패킷 SHA-256 일치. 원본 TTS와 한영 SRT 해시 불변.
- 원본들의 색상 매트릭스 차이로 필터가 재초기화되는 문제를 공통 BT.709 변환으로 해결. 예시 8개 모두 1,170프레임. 의도적 색감 변경이나 화면 왜곡은 하지 않음.
- 수정 후 게임 원음과 기존 게임 단독 믹스의 01장 차분 피크 약 -96.24dBFS: PCM 양자화 수준. 내레이션·BGM 재합성 없음.

## 이전 오디오 단독 검토본 (보존 기록, 현재 연결 아님)

내레이션 -16 LUFS, 게임 원음 -23 LUFS, 전체 연속 BGM -28 LUFS를 기본값으로 합니다.
BGM은 게임 원음과 함께 재생하고 겹칠 때만 3dB 낮춥니다. 곡 반복에는 1초
크로스페이드를 적용하며, 씬마다 음악을 끊거나 다시 시작하지 않습니다.
사이드체인은 threshold 0.08, ratio 2.2, attack 15ms, release 280ms이며 약 3dB
덕킹을 의도합니다. 실제 설정의 기준은 `project.json`이고 예외가 있으면 아래에 기록합니다.

- 승인곡·출처: Wanderlust — Scott Buckley / https://www.scottbuckley.com.au/library/wanderlust/ / CC BY 4.0. 2026-09-16 사용자 선택.
- 믹서: qwen3-tts/mix_visible_rewards_review.py --version 1. 출력이 있으면 버전 증가.
- 씬 수·게임 예시 길이·타이밍: 8개 / 19.5초 / 실측 timing JSON. 375.760042초.
- 원음: 아직 클립 미확보이므로 8개 장 모두 미포함. 원음 포함 최종 믹스로 부르지 않음.
- 내레이션: 장별 고정 게인·안전 피크 리미터 후 MP3 -16.00 LUFS. 속도·피치 처리 없음.
- 연속 BGM: 168.186576초 원본을 3회 입력, 1초 크로스페이드 2회 후 영상 길이에 맞게 끝냄. 첫·끝 0.45초 페이드.
- 이번 검토본은 실제 게임 원음이 없으므로 원음 동시 구간용 추가 -3dB는 아직 적용하지 않음. 내레이션 사이드체인은 적용.
- 내레이션 mono→stereo는 채널당 0.70710678 배분으로 통합 음량이 3dB 증가하지 않게 처리.

## 결과 경로

- 원본 TTS: `project.json`의 `paths.narration`
- 편집기 검토 믹스: `motion-canvas/src/projects/visible-rewards/assets/audio-review.wav`
- 실제 생성물: `shared/output/narration/visible-rewards/qwen3-1.7b-balanced-v1/visible-rewards-narration-wanderlust-review-v1` + `.wav`, `.mp3`, `.m4a`, `.json`
- 배경 단독: 같은 경로의 `visible-rewards-narration-wanderlust-review-v1-bgm-only.wav` (내레이션 덕킹 전).
- 최종 전체 믹스 `final-mix.m4a`, 최종 MP4는 **미생성**. `project.json.paths.audioReview`와 최종 `audioMix` 경로를 혼동하지 않음.

## 검수 결과

목표값을 측정값으로 복사하지 말고 실제 파일 검사 결과를 작성합니다.

- 검토 WAV: -15.72 LUFS / -3.66 dBTP. 48kHz stereo PCM.
- 검토 MP3: -15.99 LUFS / -3.91 dBTP. 192kbps.
- 검토 M4A: -15.76 LUFS / -3.70 dBTP. AAC 192kbps / 48kHz stereo.
- BGM 단독: -28.20 LUFS / -14.10 dBTP (실측, 덕킹 전).
- 원본·검토 오디오 375.760042초. 압축 인코더 패딩 차이 80ms 이내 검증.
- 8개 장 × 예시/설명 각 2초 표본 = 16개 BGM 비무음 검사 통과. 이것은 전체 청취 승인이나 게임 원음 존재 확인이 아님.
- 편집기 project.ts는 audio-review.wav 연결, 검토 WAV와 SHA-256 동일. 실제 브라우저 스피커 재생·전체 청취는 별도 확인 필요.
- TypeScript 검사, narration 단계 프로젝트 검사 통과. 최종 publish 단계 검사 대상 아님.
- MP4와 M4A의 일치: 최종 MP4 미생성으로 해당 없음.
- 한국어·영어 SRT: 각 94개, 번호·타임코드 동일, 중복·역전 없음. 마지막 종료 375.740초.
- 전체 청취 승인 미완료. 실제 클립·원음·최종 도식·영상 렌더 작업이 남아 있음. publishReady=false 유지.
