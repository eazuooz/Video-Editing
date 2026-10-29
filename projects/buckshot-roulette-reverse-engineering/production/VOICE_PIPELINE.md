# 이 편의 음성·자막 실행 경로

작업 위치는 `D:/Github/VideoEditing`. 승인된 Qwen3 1.7B 자체 목소리를 유지한다. 무료/유료 외부 TTS 요청은 하지 않는다. 부모 작업이 현재 GPU 작업을 순서대로 맡으며, 이 문서는 다음 작업을 자동 실행하는 지시가 아니다.

## 준비된 입력

- `planning/narration-draft.md` → `script/narration.ko.json`, `script/narration.en.json`
- 8장면, 17문단, 한국어 2,829자. 시간은 실제 PCM 생성 뒤 확정한다.
- `production/tts-manifest.json`은 본래 프로젝트 manifest를 덮지 않는 음성용 입력이다.
- `displayLines`에는 `REA`, `GDScript`, `Godot` 표기를 유지하고 TTS 문장에만 발화 별칭을 쓴다.
- 원작 수갑·톱 시연의 정확한 시작/끝은 부모 작업의 촬영 감사에 따른다. 원작 톱 시연의 체력은 **4→2**, 피해는 2다. 대본에는 3→1이라는 표현이 없다.
- 규칙 374개 검사와 장면 통합 32개 검사를 분리해 설명한다. 원작 전체 동일성 검증이라고 표현하지 않는다.

## 음성 생성

GPU 작업 없이 입력을 점검한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/render-voice.py
```

선택한 이번 제작에 한해 부모 작업이 확인한 기존 편집기 창을 보존하고, 실제 리소스만 점검한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/render-voice.py --check-resources --allow-idle-editors
```

부모 작업이 현재 GPU 촬영·렌더링 종료를 확인한 뒤 생성한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/render-voice.py --synthesize --allow-idle-editors
```

기존 편집기·Unity import worker·검사된 Windows GUI 프로세스는 종료하지 않는다. 1초 간격 3회 여유 10GiB 이상, 사용률 40% 이하를 확인하고 TTS 할당 상한을 7.5GiB로 둔다. 실제 게임·Python/FFmpeg 작업·배경 렌더·미분류 GPU 프로세스는 막는다. 전역 규칙은 바꾸지 않았다.

생성 결과는 `production/local/audio-v1/`의 `narration.wav`, `narration.timing.json`, `line-levels.json`, `chunks/`, `scenes/`다. 입력 해시가 달라지면 이전 테이크를 그대로 남기고 새 오디오 버전을 사용한다. 기존 raw PCM은 자동 종료 감쇠 판정만으로 덮어쓰지 않는다. 초기 `.srt`는 문단 타이밍 자료이며 최종 자막이 아니다.

## 전체 원음 ASR

현재 음성 생성 프로세스가 종료하고 GPU 임대가 해제된 후 **부모 작업의 실행 신호로** 한 번만 진행한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/review-voice.py --kind source --run --allow-idle-editors
```

기존 `qwen3-tts/transcribe_reference.py`와 로컬 Whisper large-v3-turbo를 사용한다. 저장소 모델 폴더가 없으면 확인한 `C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9`를 읽는다. 한국어·단어 시각으로 전체 현재 WAV를 읽고, 동일 SHA256의 ASR은 재사용한다. 모델 다운로드·유료 호출은 하지 않는다.

`review/source-full-asr.timestamps.json`과 `source-text-comparison.json`에서 전체 대사·누락·반복·숫자·약어·접합을 확인한다. ASR 점수만으로 실제 청취·말속도·발음 검수가 완료된 것은 아니다.

## 절 단위 자막

CPU에서 현재 ASR의 단어 시각을 기존 문자 정렬기로 연결한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/build-clause-subtitles.py
```

결과는 `narration.ko.clauses.srt`, `narration.en.clauses.srt`, `review/caption-alignment-review.json`, `review/clause-cues.json`이다. 한국어는 실제 단어 시각을 사용한다. 영어는 전 문단을 비례 배치하지 않고, 직접 대조한 65개 한영 의미 문장 그룹의 한국어 발화 구간에 맞춘다. 문장 수가 다른 세 문단은 여러 문장을 묶어 의미를 대응시킨다. `planning/caption-semantic-map.json`에 대응을 저장하며 한영 큐 수를 억지로 같게 만들지 않는다. 그룹 내부의 영어 절 경계는 추정임을 표시하고 실제 화면에서 확인한다. 의미 보존과 절 읽기·너무 짧은 큐를 직접 검수한 뒤 최종 렌더링에 연결한다. 숫자는 발화형을 유지하면서 화면에서3,572/195/374/32로 표시한다. PCM과 원래 문단 시각은 바꾸지 않는다.

## 최종 믹스

현재 인코딩본에서 실제로 디코딩한 WAV를 사용한다. 원음 ASR을 재활용해 믹스 검수로 기록하지 않는다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/buckshot-roulette-reverse-engineering/production/review-voice.py --kind mix --audio "실제 최종 인코딩본에서 디코딩한 WAV 절대경로" --run --allow-idle-editors
```

각 명령에서 `--run`을 빼면 GPU 없는 준비 점검만 한다. 최종 음량·true peak·접합·국소 음량·전체 대사와 실제 청취를 별도로 확인하고, 검수 기록은 수행한 범위만 표시한다.

## 현재 생성본과 검수 기록

- 현재 원음은 331.0800417초, SHA256 `cde1c69a5bf1f841f52f1195a288c563e258f53f21fc3b5528a9a7aeb2c8c520`이다. 전체 원음 ASR은 이 해시로 완료했으므로 같은 파일을 다시 인식하지 않는다.
- 모든 문장을 원고와 비교했으며 문장 누락·중복·불필요한 인사는 없었다. `건너뜁니다`, `새 장전으로`, `실탄의`, `프로젝트에` 네 곳은 ASR 표기가 달라 실제 청취 대상으로 남겼다. 자동 재생성 사유로 확정하지 않았다.
- 한국어 95큐, 영어 114큐의 절 단위 자막과 65개 의미 그룹을 저장했다. 역순·겹침·짧은 큐/읽기 속도 검사에는 남은 경고가 없다. 실제 영상과 375px 화면 검수는 별도다.
- `review/sentence-word-anchors.json`은 문단 및 문장별 실제 발화 시각과 원시 ASR 단어 시각을 담는다. 모든 시각은 원음의 0초 기준이다. 최종 편집이 2초 브랜딩을 붙이면 자막/앵커도 정확히 2초 이동한다.
- 원음 측정은 −19.5 LUFS, +6.4 dBTP, LRA 9.8 LU다. FLOAT PCM에 1을 넘는 값이 보존되어 있으며 저장 단계에서 정수 PCM으로 클리핑한 파일이 아니다. 문단 균형을 유지하는 +3.5dB 일정 이득으로 시작하고, FLOAT 중간 믹스와 최종 오버샘플링 리미터를 거쳐 실제 AAC를 다시 측정한다. 피크만 보고 전체 내레이션을 낮추지 않는다.
- `production/local/audio-v1/review/listening/index.html`에 도입부 10초와 네 발음 후보 각 8초를 모았다. 청취용 복사본에만 계획된 이득/리미터를 적용했으며 raw PCM은 그대로다. `listening-clips.json`에 원음 구간, 길이, 해시가 있다. 사람의 청취 완료를 대신하지 않는다.
- 이 컴퓨터의 WinGet FFmpeg 실행은 권한 검토가 필요한 실행 경로다. ASR을 실행할 때 FFmpeg의 `WinError 5`가 발생하면 같은 로컬 검사 명령을 도구의 권한 검토를 통해 실행한다. GPU 임대/리소스 기준을 생략하거나 다른 앱을 종료하는 방식으로 우회하지 않는다.
