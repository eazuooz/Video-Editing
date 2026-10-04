# 극좌표계 · 3분 강의 샘플

사용자 요청(2026-10-04): 첫 챕터 극좌표계 약3분 샘플, **실제 사례40% / 설명60%**. 본편168초에서 실제 기존 게임67.2초, 직접 제작한 수학 설명100.8초. 원본 고양이 로고2초와 원본 회원 엔딩10초를 포함하여 총180초(1080p60)로 계획/측정했다. 최종 파일 검증은 production/qa.json을 따른다.

Manim Community0.20.1(Cairo)를 선택했다. [GL·Community 비교](planning/manim-comparison.md), [구성안](planning/outline.md). 3D 원통좌표 장면까지 실제 ThreeDScene으로 만들었다. Part1의 익숙한 질문→구체 숫자→움직임→공식 흐름을 계승한다. 전체 극좌표 단원을3분으로 요약한 완강본은 아니며 점의 표현/직교변환이 중심이다.

최종 납품: `output/game-math-polar-sample/`의 captioned.mp4, clean.mp4, ko.srt, en.srt. `output/index.html`이 전체 목록. 편집 가능한 자막 텍스트는 script/final.ko.ass. 독립 Motion Canvas 씬은 Manim/실제 게임 컷을 재생하는 래퍼이며 최종 영상은 FFmpeg로 합성한다. Motion Canvas에서 렌더했다고 혼동하지 않는다.

재제작(기존 음성과 개인 원본 자료 보존 필요):

```powershell
# qwen3-tts/.venv에 production/requirements.txt의 Manim 버전 설치
# 음성을 새로 만들면 아래 순서로 현재 파일을 다시 검수
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/render_narration.py --project game-math-polar-sample --batch-size 1
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/review_project_narration.py --project game-math-polar-sample --device cuda
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/align.py
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py plan
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py render
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py assemble
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py burn
qwen3-tts/.venv/Scripts/python.exe projects/game-math-polar-sample/production/build.py qa
# 모든 자막과 장면 구도를 직접 검수한 뒤 수집
node projects/game-math-polar-sample/production/finalize.cjs --visual-reviewed
node scripts/collect-video-output.cjs game-math-polar-sample
node scripts/build-rebuild-manifests.cjs game-math-polar-sample
```

원본 MP4·Qwen WAV·BGM·원본 로고/회원 이미지·모델/venv는 Git에 넣지 않는다. 새 TTS는 바이트/길이가 달라질 수 있으므로 plan부터 컷·한영 자막·최종 믹스·비율을 함께 갱신한다. prepare.cjs는 최초 생성 설정용이며 검수 완료본에 다시 실행하지 않는다.

2026-10-04 실제 결과: clean/captioned 모두180초·10800프레임·1080p60, 전체 디코딩 통과, AAC 패킷MD5 동일. 한영43큐의 발화 타이밍이 같고 모든 한국어 자막 중간 시점 및13개 전체 구도를 직접 보았다. 최종 믹스는 -16.04 LUFS/-1.55 dBTP. 렌더·픽셀 검수 완료와 사람의 청취 승인은 별개다.

미완료 상태: 사람의 전체 청취, 기존 Nimbus 복구본의 Audio Library 원본 취득 확인, 게임IP 공개 전 검토, 기존 회원 목록의 잘린 이름 확인. 업로더의 녹화 재사용 허용은 확인했으며 source audio/OST는 최종 믹스에서 제외한다. 이번 요청은 로컬 샘플이고 공개/예약/YouTube 업로드를 하지 않는다. 검수 샘플 완료와 게시 승인 상태를 구분한다.
