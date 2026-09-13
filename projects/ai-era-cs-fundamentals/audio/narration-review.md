# 전체 나레이션 v5 — 생성·검수 기록

보존된 구버전 기록입니다. 현재 기준은 [v6 제작·재현](v6-production.md)과 [v6 받아쓰기 확인](v6-asr-notes.md)입니다. 아래의 v5 예시 무음·54문단·M4A 연결 설정을 현재 v6에 다시 적용하지 않습니다.

요청일: 2026-09-10. 현재 대본에 전체 TTS를 적용하라는 요청에 따라 기존 균형형 복제 화자를 재사용합니다. 전체 결과의 주관적인 청취 승인은 별도입니다.

## 화자와 생성

- 한국어 대본 v5, 12챕터 / 54문단. 텍스트를 축약하거나 예전 샘플을 반복하지 않습니다.
- 로컬 Qwen3-TTS 12Hz 1.7B Base. 기존 15~35초 기준 음성과 기준 발화문으로 화자 프롬프트 생성.
- 장면 단위 연속 합성, batch 1, 최대 1536 audio tokens. 긴 챕터가 이전 1024 제한에서 조기에 끝나지 않도록 여유 확보.
- 챕터 간 0.72초, 각 챕터 앞 실제 예시 19.5초. 앞 2초 자체 밈은 설명과 겹치므로 시간을 더하지 않습니다.
- 말끝 에너지·감쇠 자동 검사, 최대 3회 합성에서 가장 나은 테이크 선택. 이것만으로 자연스러움이나 완전한 발화를 보장하지 않습니다.
- 생성은 로컬 GPU, 받아쓰기는 로컬 Whisper. 기준 목소리를 외부 TTS 서비스로 전송하지 않습니다.

## 검수와 동기화

1. 각 WAV의 SHA-256과 받아쓰기 캐시를 연결합니다. 테이크가 바뀌면 기존 받아쓰기를 재사용하지 않습니다.
2. 생성과 동시에 CPU 받아쓰기를 진행할 수 있으나, 전체 합성이 끝난 뒤 다시 실행해 최종 테이크를 확인합니다.
3. 한국어 자막은 승인 대본을 보존하고 Whisper 단어 시점과 대조합니다. ASR의 숫자 표기·동음 오인으로 대본을 바꾸지 않습니다.
4. 영어는 한국어 54문단에 대응하는 번역입니다. 양 언어의 가독성을 고려해 동일한 수의 짧은 자막으로 나누고 한국어의 자막 번호·시작·종료 시간을 그대로 사용합니다. 영어 음성을 별도로 합성한 것은 아닙니다.
5. 원래의 장면 음성 시작점을 유지한 채 자막 내부 시점만 정렬합니다. 씬 경계는 같은 30fps 반올림으로 계산하며 렌더는 60fps입니다.
6. TTS WAV에는 예시 구간이 무음으로 들어 있습니다. 편집기에는 WAV 단독이 아닌 **TTS + 예시 원음 M4A**를 연결합니다.
7. 전체 청취와 음악 확정 전에는 게시용 완료 상태로 표시하지 않습니다.

## 재현 명령

저장소 루트에서 실행합니다. 이미 검수한 최종 테이크를 보존하려면 생성 단계는 필요할 때만 다시 실행하세요. 대본을 바꿀 때는 출력 버전을 올려 과거 결과를 덮어쓰지 않습니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/render_narration.py --project ai-era-cs-fundamentals --batch-size 1
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/review_project_narration.py --project ai-era-cs-fundamentals --device cpu
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project ai-era-cs-fundamentals
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/build_project_timing.py --project ai-era-cs-fundamentals
node scripts/build-ai-cs-narration-audio.cjs
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project ai-era-cs-fundamentals -Stage narration
node motion-canvas/scripts/check-ai-cs-narration.cjs
node motion-canvas/scripts/check-ai-cs-visuals.cjs
npm run build
```

`build-ai-cs-narration-audio.cjs`는 **음악 대기 중인 TTS·원음 검토용 믹서**입니다. 음악 파일이 지정되면 멈추도록 되어 있습니다. Blue Dream 확보 후에는 연속 BGM·덕킹을 포함한 최종 믹서를 사용하고 MP4까지 검수해야 합니다. 옛 `build-ai-cs-preview-audio.cjs`는 임시 시간과 첫 샘플만 사용하므로 현재 음성본을 만드는 명령이 아닙니다.

## 자동 검수 산출물

기준 폴더: `shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v5/`

- `chunks/01-scene.wav`~`12-scene.wav`: 예시 무음 없는 챕터별 음성.
- `*.wav`: 영상 시간과 맞춘 전체 음성 트랙. 예시 19.5초 구간은 무음.
- `*.srt`, `*.en.srt`: 한국어 / 영어 분리 자막.
- `*.asr-review.json` / `.txt`: 최종 파일 해시, 받아쓰기 차이, 말끝·피크 검사.
- `*.alignment-review.json`: 자막 정렬의 문자 일치 범위와 실제 발화 끝.
- `audio/narration-source-report.json`: 씬별 원음과 음성의 실제 LUFS 및 전체 true peak.
- `audio/editor-playback-check.json`: 12챕터 × 원음/음성의 브라우저 재생 확인. 사람의 전체 청취 승인과 구분.

## 비용 정보 확인

OpenAI Docs의 공식 출처 확인 절차에 따라 2026-09-10 기본 API 요금 표기를 재확인했습니다. 기존 $10 입력 / $50 출력(각 100만 토큰) 카드와 대본을 유지했습니다. [프로젝트 출처 및 조건](../sources/SOURCES.md#v5-전체-tts-직전-재확인--2026-09-10).

## 현재 결과

2026-09-10 전체 합성, 2026-09-11 편집기 연결·검수.

- 12/12 WAV 말끝 검사 통과. 04·06·11은 자동 재시도로 종료 부분이 더 나은 테이크를 선택했습니다.
- 받아쓰기 대조: 장면별 문자 유사도 97.77~100%. 문장 누락·반복은 발견하지 못했습니다. 숫자(다섯/5, 2026년 등), 조사 의/에, 큐/Q와 안/않 차이는 원문을 유지했습니다. 09의 ‘구독료/구동료’, ‘글을/그를’은 연음·비음화와 구별이 어려운 ASR 표기 차이로 기록하고 청취 검토 대상으로 남깁니다.
- 원본 전체 WAV 906.720초, 편집 타임라인/M4A 906.733초, 54,404프레임@60fps. 예시 19.5초 × 12 유지.
- 한국어·영어 각각156개 자막, 모든 번호·타임코드 동일. 마지막 자막 15:06.480. 54개 긴 원문 문단을 자막으로 그대로 띄우지 않는 프로젝트 예외를 README에 기록했습니다.
- Motion Canvas의 장면 종료 한 프레임을 현재 FPS에 맞춰 보정해 누적0.4초 오차를 제거했습니다.
- 자동 재생 검사: 30fps와60fps에서 각12개의 예시/나레이션 구간 확인. 영상 대표60프레임 렌더 오류 없음. 실제 사람의 전체 청취 승인을 대신하지 않습니다.
- 전체 믹스 -16.73 LUFS / -1.95 dBTP. 나레이션 -16 LUFS 목표에 맞추기 위해 1차 믹스 실측 후 +1.8dB 보정, 최종 리미터 유지. 상세 씬별 측정은 narration-source-report.json.
- Blue Dream의 보관함 파일·라이선스와 게시용 MP4는 아직 준비되지 않았습니다. 현재 결과는 전체 음성이 연결된 검토본입니다.
