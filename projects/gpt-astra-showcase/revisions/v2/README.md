# GPT 아스트라 제작 사례 8선

상태: **전체 음성·Discovery·작은 원음이 포함된 영상 제작 및 기술 검수 완료. 외부 영상 재사용 권리와 사람의 전체 시청 확인은 아직 남아 있습니다.**

사용자가 지정한 X 게시물 8개에서 동영상 11개를 확인했습니다. 다른 제작자의 발화나 목소리를 복제하지 않습니다. 새 프로젝트이며 기존 완성작에는 손대지 않았습니다.

- [한국어 대본 검토](script/review.ko.md)
- [전체 음성 영상 MP4](review/astra-simple-showcase-v2-narrated-review.mp4): **1920×1080 / 60fps / 4:22.5 / 약72MB**
- [한국어 SRT](review/astra-simple-showcase-v2-narrated-review.ko.srt) · [English SRT](review/astra-simple-showcase-v2-narrated-review.en.srt): 같은 타임코드의 40개 자막, 영상에 고정하지 않음
- [편집 계획](planning/edit-plan.json): 10개 독립 씬, 확정 262.5초(4:22.5). 기술 설명 대신 무엇을 만들었는지만 짧게 소개
- [원본·관찰·권리 기록](sources/SOURCES.md)
- [사실 확인 노트](planning/fact-check.md)
- [BGM 선택 기록](audio/bgm-candidates.md): Discovery — Scott Buckley, CC BY 4.0
- [31초 기차 장면 음성·음악 샘플](review/astra-v2-voice-sample.mp4): 목소리·속도 승인 완료. 기차 음성은 전체본에 그대로 재사용
- [v2 전체 화면 검토 MP4](review/astra-picture-review-v2.mp4): 1920×1080 / 60fps / 4:22.5 / 약69MB. 이 파일은 원음만 포함하며 아직 전체 TTS·BGM 없음
- v1 6:12 화면본과 대본은 `review/`와 `revisions/v1/`에 보존
- [검토·렌더 확인 결과](planning/review-status.md)

## 열기

저장소 루트에서:

```powershell
npm --prefix motion-canvas run start -- --host 127.0.0.1 --port 9101 --strictPort
```

- 검토 플레이어: http://localhost:9101/astra-review.html
- Motion Canvas 편집기: http://localhost:9101/src/projects/gpt-astra-showcase/project

편집기도 전체 믹스 PCM WAV를 사용합니다. 소리가 안 나면 새로고침 후 스피커를 켜고 재생하세요. Render는 Video (FFmpeg), include audio가 켜져 있습니다.

다운로드 및 컷은 이 프로젝트의 Git 제외 캐시에만 둡니다. 공개 게시 권한이 확인되기 전 미디어를 Git/YouTube에 업로드하지 않습니다. 프로젝트별 사용 구간은 planning/cuts.generated.json에서 추적합니다.

## 재제작 순서

대본·목소리·곡 승인 후 아래 순서로 처리했습니다. 기존 전체 영상은 덮어쓰지 않으므로 재믹스 시 먼저 매니페스트의 `paths.videoClean`을 새 버전 경로로 바꿉니다. 승인된 대본/음성을 변경할 때는 TTS 출력도 새 버전으로 분리합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/render_narration.py --project gpt-astra-showcase
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/review_project_narration.py --project gpt-astra-showcase --device cpu
node scripts/build-astra-narrated-review.cjs --prepare-narration
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project gpt-astra-showcase
node scripts/build-astra-narrated-review.cjs --mix
npm --prefix motion-canvas run build
node motion-canvas/scripts/render-astra-review.cjs --qa-only
node scripts/check-astra-narrated-review.cjs
```

실제 발화는 약132초이며, 각 씬의 남는 시간은 작품을 구경하는 여백으로 둡니다. 262.5초 타임라인에 음성을 억지로 배속하지 않았습니다. 음성 원본 `.wav`와 영상 배치용 `.timeline.wav`를 분리하고, 한영 자막은 Whisper 단어 시각에 맞췄습니다.

일반 `build-project-narration.ps1`은 발화 길이만으로 Motion Canvas 씬 타이밍을 덮어쓸 수 있으므로 이 고정 편집본에는 바로 실행하지 않습니다. 자료 컷을 새로 준비하는 `prepare-astra-review.cjs`는 화면 검토 단계용이며, 이후 반드시 위 음성·자막·믹스 단계를 다시 수행합니다.

## 검수 및 게시 전 남은 일

- 10개 장면 ASR 대조: 숫자 표기 외 내용 차이 없음. 05 발음·10 종결부 재생성 후 재검사
- 전체 AAC -17.41 LUFS / true peak -1.55 dBTP. 20개 장면/구간 레이어 표본 확인
- 편집기 AAC와 MP4 음성 패킷 동일, 편집기는 그 AAC를 PCM으로 변환해 연결
- 원본 음성이 없는/사실상 무음인 06·07·08은 BGM 유지, 가짜 효과음 추가 없음
- 기존 공통 publish 검사는 파일/기술 조건 검사이며 사용 권리 승인이나 실제 게시를 의미하지 않음
- `publishReady: false` 유지. 외부 영상·원음의 사용 허용 확인 및 사람의 전체 시청이 남아 있음

원본 화질·비율을 유지하며, 울트라와이드/세로에 가까운 영상은 잘라내지 않고 흰 여백 안에 맞춥니다. 기존 영상에 들어 있는 글씨·워터마크는 지우지 않습니다. 우리 출처 크레딧은 게시 설명란에 모읍니다.
