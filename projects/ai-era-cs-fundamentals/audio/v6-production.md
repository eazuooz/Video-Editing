# v6 — 자료화면에서도 이어지는 우리 대사

2026-09-12 대본 승인. 동일한 균형형 화자·속도를 재사용합니다. 전체 청취 승인은 별도입니다.

- 12개 독립 씬, 86개 원문 문단. 처음 19.5초는 실제 개발 예시지만 우리 목소리는 0초부터 시작합니다.
- TTS 실측 최종 타임라인은 1056.567초(17:36.567), 60fps 63394프레임입니다. KO/EN 자막은 동일한 253개 번호·타임코드로 분할했습니다.
- 원음 -31 LUFS, 내레이션 -16 LUFS 후 기존 +1.8dB 유지, BGM -28 LUFS에서 시작합니다.
- 원음과 음악은 목소리에 따라 부드럽게 낮춥니다. 음악은 전체 연속, 반복 연결만 1초 크로스페이드입니다.
- 선택곡은 Blue Dream — Cheel입니다. 현재 공식 작곡가 채널 음원을 사용한 비공개 청취 검토 믹스에는 BGM이 실제 포함되어 있습니다. 오디오 보관함 파일·사용 조건은 아직 미확인입니다. BGM 포함 여부와 게시 권리 확인 여부를 따로 표시합니다.
- WAV와 MP4/SRT는 v6 새 이름으로 출력합니다. v5 원본 대본은 `script/narration.v5.*.json`, 당시 매니페스트는 `revisions/v5/project.json`에 보존했습니다.

## 재현 순서 (저장소 루트)

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/render_narration.py --project ai-era-cs-fundamentals --batch-size 1
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/review_project_narration.py --project ai-era-cs-fundamentals --device cuda
```

`*.asr-review.json`의 누락·반복·종결 어미를 확인합니다. ASR은 자동 청취 승인이 아닙니다.
TTS와 ASR은 GPU 메모리 때문에 순차 실행을 권장합니다. 장시간 CPU 감시 대신 합성 후 `--device cuda --scenes 01,02,03`처럼 작은 묶음으로 검사하면 메모리 사용을 줄일 수 있습니다. 변경되지 않은 WAV의 해시 일치 캐시는 재사용합니다.
음성 생성이 끝난 뒤 다음 단계를 진행합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project ai-era-cs-fundamentals
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/balance_subtitle_translation.py --project ai-era-cs-fundamentals --apply
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/build_project_timing.py --project ai-era-cs-fundamentals
node scripts/build-ai-cs-continuous-audio.cjs
node scripts/sync-ai-cs-delivery.cjs
```

음악이 아직 없을 때만 `node scripts/build-ai-cs-continuous-audio.cjs --allow-missing-bgm`으로 **명시적인 BGM 미포함 검토본**을 만듭니다. 임의의 다른 곡이나 테스트 신호를 대신 넣지 않습니다.
오디오 보관함 음원·사용 조건 확보 후 `project.json.audio.backgroundMusic.file`, `license`, `licenseStatus`를 실제 근거에 맞춰 갱신하고 기본 믹서를 다시 실행합니다.

현재 검토본 재현 명령은 `node scripts/build-ai-cs-continuous-audio.cjs --artist-review`입니다. 이 옵션은 승인된 곡의 공식 작곡가 출처와 증거 파일이 있을 때만 허용되며 `publishReady: false`, `full-mix-license-pending`을 유지합니다. [근거와 제한](blue-dream-creator-evidence.md). 게시 조건이 실제 확인되면 `previewUseOnly`도 함께 해제하되, 곡 선택 승인을 사용 허가 확인으로 대신하지 않습니다.

믹서는 정상 오디오와 음량을 확인한 뒤 `editor-audio.generated.ts`를 생성합니다.
편집기에는 PCM WAV를 연결해 VS Code AAC 재생 문제를 피하고, 최종 MP4에는 같은 믹스의 AAC 파일을 사용합니다.
개별 Video 노드의 음소거는 중복 재생 방지용입니다. 원본 클립 오디오는 삭제하지 않습니다.

```powershell
npm run build --prefix motion-canvas
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project ai-era-cs-fundamentals -Stage narration
node motion-canvas/scripts/check-ai-cs-narration.cjs 60
node motion-canvas/scripts/render-review.cjs ai-era-cs-fundamentals full 9100
# 출력된 전체 MP4 경로를 다음 명령에 전달합니다.
node motion-canvas/scripts/verify-ai-cs-render.cjs <전체-MP4-경로>
```

편집기: http://localhost:9100/src/projects/ai-era-cs-fundamentals/project

청취 페이지: http://localhost:9100/ai-cs-review.html → 챕터 처음부터 듣기.

## 검사

```powershell
qwen3-tts/.venv/Scripts/python.exe -m unittest discover -s qwen3-tts/tests -v
node scripts/test-ai-cs-continuous-audio.cjs
node scripts/check-ai-cs-delivery.cjs
```

두 번째 검사는 임시 폴더의 합성 신호로 원음·BGM 믹서와 누락 방지 장치를 시험합니다. 생성 신호는 실제 영상에 사용하지 않습니다.
실제 믹스 완료 후 12개 자료화면/설명 구간을 각각 측정하고, SRT 끝과 영상 길이·모든 씬의 화면을 확인합니다.

[v6 받아쓰기 검토 메모](v6-asr-notes.md). 9번 말미의 ASR 추가 문장은 0초짜리 타임스탬프 환각으로 확인되어 대본/자막에 넣지 않았습니다. 자동 점수와 실제 전체 청취 승인을 혼동하지 않습니다.

영어 문장 재배분은 렌더 시작 전에 적용합니다. 이미 렌더가 끝난 뒤 자막 **문구만** 개선했다면 `node scripts/sync-ai-cs-render-captions.cjs <전체-MP4-경로>`로 기존 자막을 보존하고 동기화할 수 있습니다. 이 명령은 번호/타임코드가 하나라도 다르면 거절하며 영상 해시를 유지합니다. 자막·음량·타이밍 변경을 몰래 같은 작업으로 표시하지 않습니다.
