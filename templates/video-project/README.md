# {{TITLE_KO}}

- 프로젝트 ID: `{{SLUG}}`
- 생성일: {{CREATED_AT}}
- 상태: 기획 중

## 작업 순서

1. `planning/outline.md`에서 영상의 질문과 결론을 확정합니다.
2. `script/narration.ko.json`에 장면별 내레이션을 작성합니다.
3. `sources/SOURCES.md`에 사용할 자료의 출처와 라이선스를 기록합니다.
4. TTS를 생성하고 SRT 타이밍을 확인합니다.
5. Motion Canvas와 Manim에서 필요한 장면을 제작합니다.
6. B-roll을 넣고 음성·화면 동기화를 검사합니다.
7. 무자막 본편과 필요한 고정 자막 버전을 렌더합니다.
8. `publishing/`의 제목, 설명, 챕터를 완성합니다.

전체 절차는 저장소의 `docs/VIDEO_WORKFLOW.md`를 참고하세요.

## 관련 코드

- Motion Canvas: `motion-canvas/src/projects/{{SLUG}}`
- Manim: `manim/projects/{{SLUG}}`
- 생성 결과: `shared/output`
