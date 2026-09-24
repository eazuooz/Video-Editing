# 게임 개발로 먹고살기 — 전체 자막 적용 프리뷰

2026-09-19 사용자 승인: “응 이렇게 만들어줘 ㄱㄱ”. 15초 샘플에서 확인한 자막 스타일을 6개 장면 전체에 적용한다.

- [자막 포함 MP4](game-dev-career-preview-v2-captioned.mp4)
- [무자막 원본](../game-dev-career-preview-v2.mp4)
- [한국어 SRT](../game-dev-career-preview-v2.ko.srt) · [영어 SRT](../game-dev-career-preview-v2.en.srt)
- [브라우저 재생](http://localhost:9191/career-preview.html?v=2&captions=full)
- [Motion Canvas 편집기](http://localhost:9191/src/projects/game-dev-career/preview-v2-captioned/project)

## 보존한 항목

5389프레임 / 60fps = 89.817초, 1920×1080. 내레이션·Discovery 믹스와 장면 순서, 양언어 SRT 타임코드는 변경하지 않는다. 새 TTS나 재믹스를 수행하지 않고 기존 AAC를 패킷 복사한다. 외부 B-roll 없는 6개 장면 프리뷰이며 장편 본편 완성본으로 표시하지 않는다.

무자막 원본, 첫 v1, 15초 자막 샘플을 모두 보존했다. 자막은 영상에 포함되며 이 버전에서는 끌 수 없다. 유튜브에서 자막을 선택하게 하려면 무자막 원본과 별도 SRT를 사용한다.

## 자막 디자인

흰 사각 박스 / 3px 검정 테두리 / 오른쪽 아래 14px 짙은 초록 하드 그림자. Noto Sans KR 500, 48px, 최대 두 줄. 세부 토큰은 [자막 샘플 디자인 문서](../captions/README.md)에 있다.

총 20개 문구를 캡처해 확인했다. 17개 한 줄, 3개 두 줄. 최대 박스 폭 1514px, 높이 146px. 화면 안전 범위 검사 통과, 핵심 상자와 왼쪽 제목·설명 가림 없음. 전체 자막은 실측 발화 타임코드에 연결된다.

이 스타일은 처음에 현재 프로젝트용으로 승인되었다. 2026-09-19 후속 요청 “그리고 이 자막스타일 기억해줘~”에 따라 `docs/CAPTION_STYLE.md`에 새 영상의 채널 기본값으로 기록했다. 기존 완성 영상은 자동 변경하지 않는다.

## 재현

`motion-canvas` 폴더에서:

```powershell
npm start -- --host 127.0.0.1 --port 9191
node scripts/render-career-preview.cjs 9191 --version=2 --captioned
```

이미 있는 완성 파일은 자동 덮어쓰지 않는다. 다시 렌더해야 하면 새 리비전을 사용하거나 이전 결과를 명시적으로 보관한다. 장면 텍스트와 타이밍은 `preview-v2/timing.generated.json`, 자막 구현은 `preview/caption-box.ts`를 공유한다.

## 검증 기록

- TypeScript/Vite 빌드 통과.
- `qa-v2/report.json`: 6개 씬 경계, 20개 자막의 폭·높이·줄 수, 편집기 오디오 실제 재생.
- `qa-v2/contact.png`: 전체 자막 확인 화면.
- `render-report.json`: 최종 MP4 해상도·프레임·길이·오디오·전체 디코딩.
- 자막판과 무자막 원본의 AAC 패킷 SHA-256 일치: `3e9e0c292761e7d167a50524fce317b34b6d92ecc7b8951765e0e2e3d02dce4d`.

사용자의 스타일 승인은 기록했으며 새 출력 파일에 대한 최종 청취·발행 승인은 별도다. Discovery 출처는 [상위 README](../README.md)를 따른다.
