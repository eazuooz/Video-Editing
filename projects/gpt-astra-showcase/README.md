# GPT 아스트라 제작 사례 8선

현재 편집: **중간 PPT 요약8개(총24초)를 없앤 v3. 도입·마무리와 승인된 목소리, Discovery, 작은 원음은 유지합니다. 외부 영상 재사용 권리와 사람의 전체 시청 확인은 별도입니다.**

사용자가 지정한 X 게시물 8개에서 동영상 11개를 확인했습니다. 다른 제작자의 발화나 목소리를 복제하지 않습니다. 새 프로젝트이며 기존 완성작에는 손대지 않았습니다.

- [한국어 대본 검토](script/review.ko.md)
- [중간 PPT 없는 v3 MP4](review/astra-no-middle-slides-v3.mp4): **1920×1080 / 60fps / 3:58.5**
- [한국어 SRT](review/astra-no-middle-slides-v3.ko.srt) · [English SRT](review/astra-no-middle-slides-v3.en.srt): 같은 타임코드의40개 자막, 영상에 고정하지 않음
- [편집 계획](planning/edit-plan.json): 10개 독립 씬, 확정238.5초. 도입8초 + 실제 사례221.5초 + 마무리9초
- [이전 v2 음성 영상](review/astra-simple-showcase-v2-narrated-review.mp4): 4:22.5, 덮어쓰지 않고 보존. 이전 설정은 `revisions/v2/`
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

편집기도 v3 전체 믹스 `final-mix-v3.wav`를 사용합니다. 소리가 안 나면 새로고침 후 스피커를 켜고 재생하세요. Render는 Video (FFmpeg), include audio가 켜져 있습니다.

다운로드 및 컷은 이 프로젝트의 Git 제외 캐시에만 둡니다. 공개 게시 권한이 확인되기 전 미디어를 Git/YouTube에 업로드하지 않습니다. 프로젝트별 사용 구간은 planning/cuts.generated.json에서 추적합니다.

## 재제작 순서

v3는 TTS를 재합성하지 않았습니다. 승인된10개 WAV 및 ASR을 `qwen3-1.7b-balanced-edit-v3`에 복사하고 시각만 조정했습니다. 기존 영상·음성은 덮어쓰지 않으므로 다음 재편집에서는 먼저 매니페스트/편집 계획의 버전과 출력 경로를 새로 분리합니다. 아래는 캐시 준비 후 실행 순서이며 기존 완성 MP4가 있으면 덮어쓰기 대신 중단합니다.

```powershell
node scripts/prepare-astra-review.cjs
node scripts/build-astra-narrated-review.cjs --assemble-picture
node scripts/build-astra-narrated-review.cjs --prepare-narration
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project gpt-astra-showcase
node scripts/build-astra-narrated-review.cjs --mix
npm --prefix motion-canvas run build
node motion-canvas/scripts/render-astra-review.cjs --qa-only
node scripts/check-astra-narrated-review.cjs
```

실제 발화는 약132초이며, 각 씬의 남는 시간은 작품을 구경하는 여백으로 둡니다. 238.5초 타임라인에 음성을 억지로 배속하지 않았습니다. 기존 음성10개는 해시로 원본 일치를 검사하며, 새 영상 배치용 `.timeline.wav`와 한영 자막은 별도 v3 경로에 저장합니다. 중간 요약을 대신하는 정지 화면·반복 영상은 추가하지 않습니다.

일반 `build-project-narration.ps1`은 발화 길이만으로 Motion Canvas 씬 타이밍을 덮어쓸 수 있으므로 이 고정 편집본에는 바로 실행하지 않습니다. 자료 컷을 새로 준비하는 `prepare-astra-review.cjs`는 화면 검토 단계용이며, 이후 반드시 위 음성·자막·믹스 단계를 다시 수행합니다.

## 검수 및 게시 전 남은 일

- 10개 장면 ASR 대조: 숫자 표기 외 내용 차이 없음. 05 발음·10 종결부 재생성 후 재검사
- v3 실측 결과: `review/audio-v3/mix-report.json`, `review/technical-check-v3.json`. 20개 장면/구간 레이어 표본 및 AAC true peak -1.5 dBTP 이하 검사
- 편집기 AAC와 MP4 음성 패킷 동일, 편집기는 그 AAC를 PCM으로 변환해 연결
- 원본 음성이 없는/사실상 무음인 06·07·08은 BGM 유지, 가짜 효과음 추가 없음
- 기존 공통 publish 검사는 파일/기술 조건 검사이며 사용 권리 승인이나 실제 게시를 의미하지 않음
- `publishReady: false` 유지. 외부 영상·원음의 사용 허용 확인 및 사람의 전체 시청이 남아 있음

원본 화질·비율을 유지하며, 울트라와이드/세로에 가까운 영상은 잘라내지 않고 흰 여백 안에 맞춥니다. 기존 영상에 들어 있는 글씨·워터마크는 지우지 않습니다. 우리 출처 크레딧은 게시 설명란에 모읍니다.
