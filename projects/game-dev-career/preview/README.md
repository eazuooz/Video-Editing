# 직무와 기본기 — 내레이션 프리뷰 v1

사용자 요청: “일단 프리뷰 먼저만들어줘”. 앞서 조사한 내용을 짧은 영상으로 확인하는 범위다. 전체 본편의 대본·보이스·최종 청취 승인은 별도 유지한다.

6개 독립 씬: 도입 → 기획 → 프로그래밍 → 2D 아트 → 3D 아트 → 마무리.
직접 제작한 보물상자 2.5D 애니메이션, 기존 균형형 화자 참조, 승인된 Discovery를 사용한다.
이번 샘플은 설명 화면의 구성·발화·BGM을 검토하기 위한 것이므로 외부 자료화면 슬롯을 넣지 않는다. 유튜브 자료화면까지 들어간 본편으로 소개하지 않는다.

## 완성된 프리뷰

- [MP4 재생](game-dev-career-preview-v1.mp4): 75.733초, 1920×1080, 60fps, 약 5.7MB. 내레이션과 BGM 포함, 자막은 별도.
- [한국어 SRT](game-dev-career-preview-v1.ko.srt) · [영어 SRT](game-dev-career-preview-v1.en.srt): 17개 큐, 동일 타임코드.
- [검증 기록](qa-notes.md): 레이아웃·편집기 오디오·전체 디코딩 확인. 사람의 최종 청취 승인은 대기 중.

## 기준 파일

- `script.v1.json`: 프리뷰에 한정한 한국어 발화와 영어 번역.
- `build_audio.py`: 로컬 Qwen3-TTS 합성, Whisper 확인, 양언어 SRT·실측 타이밍, BGM 믹스.
- `motion-canvas/src/projects/game-dev-career/preview/`: 편집 가능한 텍스트, 절차적 입체, 독립 씬, 음성 길이 기반 타임라인.
- `motion-canvas/scripts/render-career-preview.cjs`: 모든 씬 화면과 편집기 소리 확인 후 렌더.

## 재현

저장소 루트에서 다음 단계를 순서대로 실행한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py tts
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py assemble
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py mix
```

`motion-canvas` 폴더에서:

```powershell
npm start -- --host 127.0.0.1 --port 9191
node scripts/render-career-preview.cjs 9191
```

프리뷰 재생: http://localhost:9191/career-preview.html
편집기: http://localhost:9191/src/projects/game-dev-career/preview/project

렌더 스크립트는 이미 있는 완성 MP4를 덮어쓰지 않는다. 재출력 시 기존 결과를 별도 리비전 폴더에 보관하거나 출력 리비전을 변경한다.

재생 화면에서 버튼을 누르면 음소거를 해제하고 재생한다. 최종 본편 프로젝트는 아직 시작 템플릿이다. 반드시 위 프리뷰 주소를 사용한다.

## 음악 출처

'Discovery' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au

https://www.scottbuckley.com.au/library/discovery/
https://creativecommons.org/licenses/by/4.0/

원곡 일부 발췌, 음량 조정, 내레이션 덕킹 및 시작·끝 페이드 적용. 음악은 씬 사이에서도 연속 재생한다.
