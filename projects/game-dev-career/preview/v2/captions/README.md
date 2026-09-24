# 참고 이미지 기반 자막 샘플

사용자 요청: 작업은 계속 진행하면서 첨부 이미지와 같은 느낌의 자막을 영상에서 미리 확인한다.

- [샘플 MP4](game-dev-career-caption-sample-v2.mp4): 첫 장면 15.317초, 1920×1080, 60fps. 한국어 내레이션·Discovery 포함.
- [대표 프레임](qa-v2/caption-97.png)
- [브라우저 재생](http://localhost:9191/career-preview.html?v=2&captions=sample)
- Motion Canvas 편집기: http://localhost:9191/src/projects/game-dev-career/caption-sample/project

## 적용한 디자인

첨부 이미지의 자막만 참고했다. 원본 그래프·통계·종이 질감·화면 전체 디자인은 가져오지 않았다. 기존 2.5D 영상은 유지한다.

- 불투명 흰색 사각형, 모서리 라운드 없음.
- 검정에 가까운 `#161b18` 테두리, 3px.
- 오른쪽 아래 14px의 짙은 초록 `#073c32` 하드 그림자, 블러 없음.
- 텍스트 `#080b09`, Noto Sans KR 500, 48px, 줄 간격 62px.
- 참고 이미지의 정확한 서체를 확인한 것은 아니며 설치된 유사한 산세리프 서체를 사용했다.
- 화면 중앙 정렬, y=430(1920×1080 중심 좌표), 글자 폭에 따라 박스 자동 크기 조정.
- 글줄 최대 폭 1570px, 긴 문장은 단어 단위 줄바꿈. 상자 본체와 왼쪽 핵심 설명은 가리지 않는다.
- 각 발화 타임코드에 맞춰 표시. 샘플의 네 문구를 모두 캡처해 확인했다.

샘플은 자막이 영상에 들어간 비교본이다. 2026-09-19 “응 이렇게 만들어줘 ㄱㄱ” 승인 후 [전체 프리뷰에 같은 자막을 적용](../captioned/README.md)했다. 무자막 원본과 KO/EN SRT는 별도로 보존한다. 처음에는 프로젝트 단위 승인이었으며, 후속 요청 “그리고 이 자막스타일 기억해줘~”에 따라 `docs/CAPTION_STYLE.md`에 새 영상의 채널 공통 기본값으로 기록했다. 과거 완성 영상은 변경하지 않는다.

## 편집과 재현

기준 발화·자막 문구: `projects/game-dev-career/preview/script.v2.json`

편집 가능한 자막 구현: `motion-canvas/src/projects/game-dev-career/preview/caption-box.ts`

`caption-sample/scene01.tsx`에서 기존 장면에 박스 자막을 켠다. 실제 음성 길이와 자막 타이밍은 v2 타임라인을 참조한다. 샘플 음성은 v2 전체 믹스의 첫 장면을 잘라 끝 0.45초 페이드아웃한 것으로, TTS를 다시 생성하지 않았다.

```powershell
# 저장소 루트에서 v2 전체 믹스 생성 후
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py caption-audio --version 2
# motion-canvas 폴더에서
node scripts/render-career-preview.cjs 9191 --version=2 --caption-sample
```

음악 출처와 라이선스는 [상위 README](../README.md)의 Discovery 표기를 사용한다.
