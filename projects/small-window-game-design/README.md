# 그래픽은 멋진데, 왜 플레이하기 불편할까?

새 영상 제작 프로젝트. 현재 **대본 v1과 6씬 2.5D 무음 콘셉트** 단계이며 전체 음성/실제 게임 클립/음악을 넣은 완성본은 아니다.

- [대본 검토](script/review.ko.md) / 편집 원본: `script/narration.ko.json`
- [구성](planning/outline.md) / [자료화면 계획](planning/footage-plan.md)
- [사실관계 보완](planning/fact-check.md) / [출처·사용 상태](sources/SOURCES.md)
- [BGM 선택](audio/bgm-candidates.md)
- Motion Canvas: `http://127.0.0.1:9210/src/projects/small-window-game-design/project`
- [콘셉트 미리보기](preview/index.html) / [MP4 직접 열기](preview/v2/small-window-concept-v2.mp4) (36초 무음, 1920×1080/60fps)

최종 목표는 본편 약 4~5분과 10초 회원 감사 엔딩, 1920×1080/60fps다. 분량은 TTS 후 확정한다.
원본 영상은 논지 참고로만 사용한다. 레이싱/FPS/VR 화면은 내용·인아웃·권리 확인 후 삽입하며, 예시 위에서도 우리 대사를 이어 간다.
BGM은 Discovery — Scott Buckley로 승인되었다(아직 믹싱 전).
현재 미승인: 대본, 첫 장면 목소리 샘플, 최종 청취. 회원 사진·이름·배지 원본도 필요하다.

```powershell
node projects/small-window-game-design/production/prepare-review.cjs
# 개발 서버 실행 후 무음 디자인 검토본
node motion-canvas/scripts/render-small-window-concept.cjs v3
```

기존 균형형 Qwen3 1.7B로 첫 장면 샘플을 승인받은 뒤 전체 음성·한영 SRT·실측 타이밍을 만든다.
표시용 FOV/VR과 발음용 대본을 분리한다. 박스 자막은 실제 UI를 가리지 않는 위치에 둔다.
최종 결과물 네 개가 준비되면 `node scripts/collect-video-output.cjs small-window-game-design`으로
`output/small-window-game-design/`에 모은다. 무음 콘셉트를 최종 모음에 넣지 않는다.
