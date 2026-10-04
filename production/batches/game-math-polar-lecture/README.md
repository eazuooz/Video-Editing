# 극좌표계 전체 강의 · 두 편

2026-10-04 사용자 요청: 샘플을 보존하고 해당 챕터의 전체 강의를 두 편으로 제작한다. 이번 강의는 실제 기존 게임 영상 40%, 원본 설명 60%, 배경음악 없음. 고양이 로고 2초와 원본 회원 감사 10초만 비율 계산에서 제외한다. 각 편의 독립 도입은 본문 설명에 포함한다.

1편은 점 찍기, 단위, 앨리어스·정준화, 양방향 변환, 회전·조준과 2D 벡터를 다룬다. 2편은 원통·구면좌표, 수학/게임 축 약속, 역변환·극점과 3D 카메라를 다룬다. Notion 7.1–7.5의 핵심 주장과 경계를 보존하고 대표 연습 문제를 단계별로 설명한다. 모든 책 연습 문제를 원문 그대로 읽는 작업은 아니다.

Manim Community 0.20.1/Cairo를 사용한다. 각 설명은 독립 Manim 및 Motion Canvas 장면이다. 3D는 ThreeDScene 실제 공간 도형을 사용한다. 스크립트의 문단 시작을 Whisper 단어 타이밍에 맞춰 수식·강조를 바꾼다.

## 재제작 순서

승인된 개인 음성과 원본 회원/로고 자산, 기록된 실제 게임 소스를 먼저 복원한다. 영상·오디오·모델·압축 미디어를 Git에 넣지 않는다. 전체 사람 청취, 게임 IP 공개 권리 검토와 잘린 회원 표시명 확인은 별도의 대기 상태로 보존한다. 새 음성은 바이트 동일 재생성이 아니므로 두 SRT와 편집 길이를 함께 다시 검증한다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/render-voice.py --project game-math-polar-2d --batch-size 4
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/review_project_narration.py --project game-math-polar-2d --device cuda
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/align.py game-math-polar-2d
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/build.py game-math-polar-2d plan
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/build.py game-math-polar-2d render
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/build.py game-math-polar-2d assemble
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/build.py game-math-polar-2d burn
qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/game-math-polar-lecture/build.py game-math-polar-2d qa
```

2편은 slug를 `game-math-polar-3d`로 바꾼다. CPU/GPU는 동일 승인 모델과 참조 음성을 쓴다. `--scenes 06 --force-scenes 06 --device cpu`처럼 특정 장면만 재시도하면 이전 테이크를 보존하며 전체 믹스는 만들지 않는다. 끝부분 휴리스틱과 현재 WAV 해시의 ASR 검사를 다시 통과해야 한다.

`incremental-render.py <slug>`는 검사를 통과한 독립 장면만 먼저 렌더링한다. 마지막 10초는 중간 렌더의 정지 화면 여유분이며 최종 타임라인이 필요한 부분만 사용한다. 실제 게임에는 반복·속도 변경·정지 화면을 사용하지 않는다. 소스/대본/음성 해시가 바뀌면 해당 렌더를 다시 검증한다.

모든 현재 자막과 장면 픽셀을 직접 검토한 뒤 `pixel-review.json`, 내레이션 의미·숫자 차이를 확인한 `narration-review.json`을 기록한다. 실제 검토 없이 이 기록을 통과 상태로 생성하지 않는다. `finalize.cjs <slug> --visual-reviewed` 후 결과물 수집, 재빌드/미디어 검사, 영상별 소스 커밋·푸시, 비공개 Studio 업로드를 진행한다. `publishing.cjs`는 수집된 파일 해시와 실측 챕터로 업로드 준비만 한다.

맞춤 썸네일 한도는 실제 증거와 재시도 시각을 별도 기록하고 나머지 설정과 다음 영상 작업을 계속한다. 공개/예약은 사용자 직접 작업이며 비공개 댓글은 게시 후 대기 상태다.
