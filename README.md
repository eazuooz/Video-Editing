# Video Editing — Motion Canvas + Manim

다른 컴퓨터에서 이어서 작업하려면 [복원·실행·진행 상태 안내](docs/CONTINUE_ON_ANOTHER_COMPUTER.md)를 먼저 확인하세요.
대용량 영상 복원: `node scripts/restore-media.cjs` (저장소 루트, Node.js 필요).

Motion Canvas(TypeScript)와 Manim(Python), 두 코드 기반 영상 편집/애니메이션 엔진을 한 저장소에서 함께 쓰기 위한 프로젝트입니다. 각자 독립적으로 렌더링한 뒤 `shared/output`에 모인 결과물을 ffmpeg로 이어 붙여 최종 영상을 만듭니다.

## 폴더 구조

```
.
├── projects/            # 영상별 기획·대본·출처·게시 정보
│   └── <project-slug>/
├── templates/           # 새 영상 프로젝트와 엔진 시작 템플릿
├── docs/                # 반복 제작 워크플로와 운영 문서
├── motion-canvas/       # Motion Canvas 프로젝트 (UI 애니메이션, 텍스트, 트랜지션 등에 적합)
│   └── src/projects/    # 새 영상별 Motion Canvas 프로젝트
├── manim/               # Manim 프로젝트 (수학/도형/그래프 애니메이션에 적합)
│   └── projects/        # 새 영상별 Manim 프로젝트
├── examples/            # 완성해서 남겨두는 예제(소스+에셋+렌더링된 영상까지 자기완결적, git에 커밋됨)
│   └── <example-name>/
├── shared/
│   ├── assets/          # 두 엔진이 공유하는 폰트, 이미지, 오디오
│   └── output/          # 렌더·TTS 결과와 최종 전달 파일
└── scripts/             # 렌더링/합치기 헬퍼 스크립트
```

새 영상은 `scripts/new-video-project.ps1`로 시작합니다. 사람이 직접 관리하는 자료는
`projects/<project-slug>/`에, 실행 코드는 각 엔진의 `projects/<project-slug>/`에 생성됩니다.
완성된 독립 데모는 `examples/`에 보관합니다.

## 새 영상 시작하기

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/new-video-project.ps1 `
  -Slug "camera-shake" `
  -TitleKo "카메라 흔들림은 어떻게 손맛을 만들까?" `
  -TitleEn "How Does Camera Shake Create Impact?"
```

그다음 `projects/camera-shake/planning/outline.md`와
`projects/camera-shake/script/narration.ko.json`부터 작성합니다. 전체 순서는
[반복 가능한 영상 제작 워크플로](docs/VIDEO_WORKFLOW.md)에 정리되어 있습니다.
TTS·자막·게임 원음·BGM의 고정 기준과 승인 순서는
[내레이션·자막·오디오 제작 기준](docs/NARRATION_AUDIO_STANDARD.md)을 따릅니다.
2026-09-06 승인한 믹스 설정과 편집기·MP4 전체 오디오 일치 규칙을 기본값으로
사용하며, 새 프로젝트 템플릿에 음량 설정과 `audio/mix-report.md`가 함께 포함됩니다.

대본과 TTS 샘플을 승인한 뒤에는 다음 한 명령으로 1.7B 장면 단위 음성, 한글·영문
SRT, 씬 타이밍과 전체 받아쓰기 검토 파일을 만듭니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/build-project-narration.ps1 -Project <project-slug>
```

BGM은 후보의 라이선스와 출처를 먼저 확인하고 사용자가 선택한 뒤에만 최종 영상에
적용합니다.

## 사전 준비

- Node.js 20+ (`node -v`로 확인, 현재 환경 v24 설치됨)
- Python 3.10+ (현재 환경 3.12/3.14 설치됨)
- [ffmpeg](https://ffmpeg.org/download.html) — Manim 렌더링과 클립 합치기에 필수

## Motion Canvas 사용법

```powershell
cd motion-canvas
npm install
npm start
```

`npm start`로 브라우저 편집기가 열립니다(기본 http://localhost:9000). 씬을 만들고 편집기의 **Render** 탭에서 내보내면 결과물이 `shared/output/motion-canvas`에 저장됩니다. 새 프로젝트 생성 스크립트가 `motion-canvas/projects.json` 등록까지 처리합니다.

## Manim 사용법

```powershell
cd manim
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File ../scripts/render-manim.ps1 -Project <project-slug> -Quality qh
```

프로젝트별 결과는 `shared/output/manim/<project-slug>`에 저장됩니다. 기존 예제 씬 전체를 렌더하려면 `-Project` 없이 스크립트를 실행합니다.

## 두 렌더링 결과 합치기

각 엔진에서 클립을 렌더링한 뒤, `scripts/combine.ps1`로 순서대로 이어 붙입니다:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/combine.ps1 -Clips `
  "shared/output/manim/videos/example_scene/1080p60/Example.mp4", `
  "shared/output/motion-canvas/project.mp4" `
  -Out "shared/output/final.mp4"
```

내부적으로 `ffmpeg -f concat`을 사용하므로, 이어 붙이려는 클립들의 해상도/코덱을 맞춰두는 것을 권장합니다(다르면 먼저 `ffmpeg`로 리인코딩).

## 헬퍼 스크립트

- `scripts/render-motion-canvas.ps1` — Motion Canvas 편집기 실행
- `scripts/render-manim.ps1` — 특정 프로젝트 또는 기존 Manim 씬 렌더링
- `scripts/combine.ps1` — 렌더링된 클립들을 하나의 영상으로 합치기
- `scripts/new-video-project.ps1` — 프로젝트·Motion Canvas·Manim 폴더 동시 생성
- `scripts/build-project-narration.ps1` — 1.7B 장면 TTS·SRT·타이밍·전체 받아쓰기 생성
- `scripts/check-video-project.ps1` — 매니페스트, 대본, 자막, 최종 파일 검사
