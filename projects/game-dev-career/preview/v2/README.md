# 게임 개발로 먹고살기 — 프리뷰 v2

사용자 요청: “기존영상으로 게임개발로 먹고살기 느낌으로 해줘”.
기존 2.5D 상자 프리뷰를 바탕으로 도입·결론과 직무별 화면 제목을 수정한다.
포트폴리오 제작 팁이 아니라, 좋아하는 게임을 **맡아서 만드는 일**과 필요한 기본기를 설명한다.

## 결과물

- [전체 박스형 자막 적용 MP4](captioned/game-dev-career-preview-v2-captioned.mp4): 사용자 승인 스타일을 전 장면에 적용. 원본과 길이·오디오 동일.
- [수정 프리뷰 MP4](game-dev-career-preview-v2.mp4): 89.817초, 1920×1080, 60fps, 무자막 영상과 전체 믹스.
- [한국어 SRT](game-dev-career-preview-v2.ko.srt) · [영어 SRT](game-dev-career-preview-v2.en.srt): 동일 타임코드 20개 큐.
- [15초 자막 디자인 샘플](captions/game-dev-career-caption-sample-v2.mp4) · [디자인 수치·편집 방법](captions/README.md).
- [검증 기록](qa-notes.md). 본편과 최종 청취 승인은 대기.

## 편집 방향

- 도입: “게임을 좋아하는데, 이걸로 먹고살 수 있을까요?” 아직 직무를 정하지 못한 시청자에게 질문한다.
- 기획: 같은 게임을 만들 수 있도록 조건·결과·예외를 문서로 전달하는 일.
- 프로그래밍: 규칙을 구현하고 문제를 추적하는 일. C++·자료구조·알고리즘·디버깅 기본기를 유지한다.
- 2D 아트: 플레이어가 알아볼 수 있는 그림. 관찰·도형화·비례·원근·명암·색.
- 3D 아트: 게임 안에서 제대로 쓰이는 입체. 형태·공간·면 구조·표면·회전축.
- 결론: 팀에서든 혼자서든 문제를 풀고 결과물을 완성한다. 취업과 독립 개발 모두 작은 제작·수정 경험으로 연결한다.

새로운 문장의 도입·결론만 TTS를 생성하고, 변경 없는 2~5번 음성은 v1에서 복사해 사용한다. 같은 사용자 화자 참조와 균형형 합성 설정을 유지한다. 이전 MP4·오디오·자막은 덮어쓰지 않는다.

본편이 아닌 구성·톤 확인용 프리뷰다. 실제 게임·개발 B-roll은 이번 수정에도 포함하지 않는다. 참고 영상은 사용자가 제공한 대본의 주제 참고이며, 화면·음성·표현을 복제하지 않는다. 돈을 잘 번다거나 취업을 보장하는 내용은 넣지 않는다.

## 빌드

저장소 루트:

```powershell
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py tts --version 2
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py assemble --version 2
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/preview/build_audio.py mix --version 2
```

GPU가 사용할 수 없는 경우 TTS와 받아쓰기는 자동으로 CPU를 사용한다. `--device cpu`로 명시할 수도 있다. 2026-09-19 작업 중 NVIDIA 장치가 일시적으로 사용할 수 없게 되어 도입의 발음 수정은 CPU로 진행했다. 드라이버 변경이나 시스템 재시작은 수행하지 않았다.

`motion-canvas` 폴더:

```powershell
npm start -- --host 127.0.0.1 --port 9191
node scripts/render-career-preview.cjs 9191 --version=2
```

재생: http://localhost:9191/career-preview.html?v=2

편집기: http://localhost:9191/src/projects/game-dev-career/preview-v2/project

자막 포함 버전은 [별도 안내](captioned/README.md)를 따른다. 2026-09-19 “응 이렇게 만들어줘 ㄱㄱ” 승인에 따라 이 프로젝트에 적용했고, 채널 공통 기본값은 변경하지 않았다.

## 음악

선택한 Discovery를 전체 타임라인에 연속 사용한다. 기존과 같은 음량·덕킹 기준이다.

'Discovery' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au

https://www.scottbuckley.com.au/library/discovery/
https://creativecommons.org/licenses/by/4.0/

원곡 일부 발췌·음량 조정·덕킹·페이드 적용. 본편 대본과 최종 청취 승인은 별도 대기.
