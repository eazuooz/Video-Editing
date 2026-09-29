# 승인된 두 번째 고양이 인트로 적용

- 2026-09-26 사용자 승인: 두 번째 인트로를 붙여 다시 제작.
- 1920×1080 / 60fps, 인트로 2초 + 기존 본편 220.466667초 = 222.466667초.
- 인트로는 `intro-cats-v2`, 사용자 고양이 로고 원본을 그대로 사용.
- 본편 13,228개 영상 패킷을 재인코딩 없이 보존. 한국어/영어 63개 큐와 ASS는 모두 +2초.
- Discovery를 새 전체 타임라인에 연속 믹스. 내레이션과 게임 원음만 2초 지연.
- 게임 원음 정규화·덕킹 후 0.5배 유지. TTS 재생성 없음.
- FFmpeg의 지연 필터 이후 타임스탬프를 샘플 번호로 재설정하여 초반 무음 누락 방지.
- 기존 본편과 이전 납품본은 보존. 멤버십 원본 이미지 미확보 및 게시 검토 대기 상태 유지.

재현 명령 (저장소 루트):

```powershell
node projects/small-window-game-design/production/add-approved-intro.cjs build
node projects/small-window-game-design/production/add-approved-intro.cjs verify
node projects/small-window-game-design/production/add-approved-intro.cjs activate
node motion-canvas/scripts/test-small-window-editor.cjs
node scripts/collect-video-output.cjs small-window-game-design
```

`body-manifest.json`은 원래 본편 입력을 고정하여 재실행 시 인트로가 중복되지 않게 한다.
`timeline.json`은 새 전체 타임라인, `full-v2/plan.json`은 인트로를 제외한 본편 타임라인이다.
