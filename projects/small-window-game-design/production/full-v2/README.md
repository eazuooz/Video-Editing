# 화면 비율 · FOV 본편 v2

사용자 요청: 자동차 원음을 샘플의 절반으로 줄이고 화면 프레임(비율)과 시야각 중심으로 본편 제작.

1. `scripts/build-project-narration.ps1 -Project small-window-game-design -SkipEnglish -SkipAsr`
2. `qwen3-tts/review_project_narration.py --project small-window-game-design`
3. `projects/small-window-game-design/production/align-captions.py` (Qwen venv Python)
4. `node projects/small-window-game-design/production/build-full.cjs prepare`
5. `node projects/small-window-game-design/production/build-full.cjs mix`
6. `node motion-canvas/scripts/render-small-window-full.cjs` (Vite :9210)
7. `node projects/small-window-game-design/production/build-full.cjs assemble`
8. `node motion-canvas/scripts/caption-small-window.cjs`
9. QA 후 `node scripts/collect-video-output.cjs small-window-game-design`

실제 게임은 원본 속도·비율의 연속 구간으로 약 68%. 설명은 6개 독립 Motion Canvas 씬의 자체 2.5D 도식이다. 최종 렌더는 같은 타이밍의 게임 컷과 도식 릴을 FFmpeg로 연결한다. 편집기에는 같은 컷·씬 길이와 전체 믹스를 연결한다.

내레이션 -16 LUFS, 원음 정규화 -23 LUFS 후 덕킹과 0.5배 감쇠, Discovery -28 LUFS에 원음 중 추가 -3dB. 최종 합산 normalize=0. 0.5배 감쇠 뒤 원음을 다시 정규화하지 않는다.

자막은 승인된 흰 박스/검정 글자/얇은 테두리/초록 하드 그림자. 하단 중앙 y=970, 48px. 게임 모서리 HUD를 피하도록 이 프로젝트는 글줄 폭을 더 좁힌다. SRT와 편집 가능한 ASS를 보존한다. 숫자 비율, Field of View, FOV는 표시 자막에서 영문·숫자로 쓴다.

원본 회원 이미지·사진·배지가 없어 10초 엔딩은 아직 포함하지 않는다. 이름만 있는 구형 엔딩으로 대체하지 않는다. 최종 사람 청취·원음 권리 검토 전 게시 승인 상태로 바꾸지 않는다.
