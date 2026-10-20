# 스팀 데모 8,000개, 좋은 게임 찾기가 왜 복권이 됐을까?

프로젝트 `steam-next-fest-ai-flood` · 생성일 2026-10-20 · 사용자 영상 선택 근거를 기록한 뒤 한 편 자동 완료.

현재 기준은 `docs/VIDEO_WORKFLOW.md`, 운영 상태는 `shared/publishing/video-production-control.json`이다. 선택한 한 편만 진행하며 다음 편은 자동 착수하지 않는다.

1. 해당 Sakurai 원본의 전체 대사·관련 화면을 먼저 확인한다. `planning/outline.md`에 원본 주장/순서/예시/결론→우리 씬 대응, 원본 짜임새를 보존한 KOEN 대본과 해당 위치의 세부 PPT 보강, 원본 게임의 동등한 최신 버전 검토(추가 게임 기본0), 실제소스·인과 연결·모든 씬의 상세대상/2.5D/움직임/자막 공간·비중·오디오·썸네일을 설계한다. 대응 원본이 없는 수업은 실제 수업자료를 기준으로 하고 게임 수를 강제하지 않는다.
2. `planning/production-plan.json`에 기존 근거와 입력해시를 연결하고 대표 움직임·오디오 샘플로 내부 품질을 확인한다. 기존 승인 설정을 재사용하고 승인된 스타일 안의 곡 선택도 내부에서 마친다. 제작 전 패키지는 사용자 승인 대기 단계가 아니다.
3. 실제 승인 범위 안에서 전체TTS/실측타임라인/믹스/독립씬/고정자막/최종쌍을 제작한다. 기본 생성기의3개씬·무음WAV·준비카드는 scaffold이며 승인된 스타일/실제영상이 아니다.
4. `production/review-ledger.json`에 한 번의 현재 검수와 재사용 근거를 연결한다. PCM/믹스ASR·모든큐/컷/움직임·두decode/PTS/음량/동일AAC·4파일을 확인한다. 변경 없는 검사/미디어를 반복 생성하지 않는다.
5. 검수한 captioned 파일을 한 번 비공개 업로드하고 가능한 설정을 저장·재열람한 뒤 선택 Git 전달을 마친다. 완성된 비공개 링크를 사용자에게 제시해 수정 검수를 받고 멈춘다. 다음 편·공개·예약·기존 업로드 교체/삭제는 별도 명시 범위를 따른다.

TTS 명령은 승인·현재 GPU 인계·실행기 적용 범위를 확인한 후에만 사용한다:
`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-project-narration.ps1 -Project steam-next-fest-ai-flood`

납품: `node scripts/collect-video-output.cjs steam-next-fest-ai-flood`. clean/captioned/KO/EN은 `output/steam-next-fest-ai-flood/`, YouTube에는 captioned만 사용한다. 제작계획의 pending을 템플릿 생성이나 도구 실행 성공만으로 approved로 바꾸지 않는다.

- 화면: `docs/VIDEO_VISUAL_STYLE.md`; 고정자막: `docs/CAPTION_STYLE.md`
- 음성/믹스: `docs/NARRATION_AUDIO_STANDARD.md`; 게시: `docs/YOUTUBE_PUBLISHING.md`
- 코드: `motion-canvas/src/projects/steam-next-fest-ai-flood`, `manim/projects/steam-next-fest-ai-flood`
- 프로젝트 manifest의 예외/측정값이 실제 제작 입력이다. 준비파일의 예시길이를 실측값으로 사용하지 않는다.
