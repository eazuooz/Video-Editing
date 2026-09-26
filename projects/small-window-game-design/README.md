# 같은 게임도 화면이 달라지면? | 화면 비율과 시야각의 게임 디자인

**6씬 전체 본편**: 1920×1080/60fps, 220.467초. 게임 149.917초(68%), 자체 2.5D 설명 70.55초(32%). 내레이션·Discovery·절반으로 낮춘 게임 원음 포함. 원본 회원 이미지가 없어 멤버십 엔딩은 미포함이며 최종 청취/원음 권리 검토 전 게시 승인 상태가 아니다.

- 최신 결과물 모음: [output 재생 페이지](../../output/small-window-game-design/index.html)
- 재현 가능한 제작 단계: [본편 빌드 안내](production/full-v2/README.md)
- 정확한 구간: [plan.json](production/full-v2/plan.json)
- 오디오/프레임 QA: [qa.json](production/full-v2/qa.json)

- [대본 검토](script/review.ko.md) / 편집 원본: `script/narration.ko.json`
- [구성](planning/outline.md) / [자료화면 계획](planning/footage-plan.md)
- [사실관계 보완](planning/fact-check.md) / [출처·사용 상태](sources/SOURCES.md)
- [BGM 선택](audio/bgm-candidates.md)
- [첫 장면 30.75초 영상](preview/narrated-v1/small-window-voice-preview-v1.mp4): 새 Forza 게임 68.02%, 설명 31.98%, TTS/낮춘 원음/Discovery. 목소리 승인용, 자막 미포함.
- 음성 검토 Motion Canvas: `http://127.0.0.1:9210/src/projects/small-window-game-design/voice-preview/project`
- Motion Canvas: `http://127.0.0.1:9210/src/projects/small-window-game-design/project`
- [콘셉트 미리보기](preview/index.html) / [MP4 직접 열기](preview/v2/small-window-concept-v2.mp4) (36초 무음, 1920×1080/60fps)

본편 대본 v2는 화면의 틀·비율·FOV·대상 점유율·UI 가림에 집중한다. 자동차는 사례이며 VR 장은 제외했다.
원작 YouTube는 논지 참고만 한다. 실제 삽입은 별도의 Forza/DOOM 게임 자료이며 예시 위에서도 우리 대사가 이어진다.
BGM Discovery — Scott Buckley는 사용자 선택 승인 후 처음부터 끝까지 연속 믹스했다.
자동차 원음: 정규화·덕킹 이후 0.5배(약 -6.02dB), 추가 재정규화 없음. 나레이션/BGM 레벨은 기존 기준 유지.
확인할 항목: 최종 사람 청취, 원음 음악 권리, 회원 사진·이름·배지 원본.

```powershell
node projects/small-window-game-design/production/prepare-review.cjs
# 개발 서버 실행 후 무음 디자인 검토본
node motion-canvas/scripts/render-small-window-concept.cjs v3
```

기존 균형형 Qwen3 1.7B 전체 음성을 장면별로 생성하고 ASR로 검토했다. 한영 SRT는 같은 63개 타임코드다.
표시용 16:9·21:9·FOV와 발음용 대본을 분리한다. 박스 자막은 모서리 HUD를 피하도록 좁히고 아래 여백을 유지한다.
최종 결과물 네 개가 준비되면 `node scripts/collect-video-output.cjs small-window-game-design`으로
`output/small-window-game-design/`에 모은다. 무음 콘셉트를 최종 모음에 넣지 않는다.
