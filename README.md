# Video Editing — Motion Canvas + Manim

Motion Canvas(TypeScript)와 Manim(Python), 두 코드 기반 영상 편집/애니메이션 엔진을 한 저장소에서 함께 쓰기 위한 프로젝트입니다. 각자 독립적으로 렌더링한 뒤 `shared/output`에 모인 결과물을 ffmpeg로 이어 붙여 최종 영상을 만듭니다.

## 폴더 구조

```
.
├── motion-canvas/       # Motion Canvas 프로젝트 (UI 애니메이션, 텍스트, 트랜지션 등에 적합)
│   └── src/scenes/
├── manim/               # Manim 프로젝트 (수학/도형/그래프 애니메이션에 적합)
│   └── scenes/
├── shared/
│   ├── assets/          # 두 엔진이 공유하는 폰트, 이미지, 오디오
│   └── output/          # 렌더링 결과물 (git에는 커밋되지 않음)
└── scripts/             # 렌더링/합치기 헬퍼 스크립트
```

## 사전 준비

- Node.js 20+ (`node -v`로 확인, 현재 환경 v24 설치됨)
- Python 3.10+ (현재 환경 3.12/3.14 설치됨)
- [ffmpeg](https://ffmpeg.org/download.html) — Manim 렌더링과 클립 합치기에 필수. 이 PC에는 아직 설치되어 있지 않으니 PATH에 추가해주세요.

## Motion Canvas 사용법

```powershell
cd motion-canvas
npm install
npm start
```

`npm start`로 브라우저 편집기가 열립니다(기본 http://localhost:9000). 씬을 만들고 편집기의 **Render** 탭에서 내보내면 결과물이 `shared/output/motion-canvas`에 저장됩니다. 새 씬은 `motion-canvas/src/scenes/`에 추가하고 `src/project.ts`에 등록하세요.

## Manim 사용법

```powershell
cd manim
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
manim render -qh scenes/example_scene.py
```

`manim.cfg`에서 `media_dir`을 `../shared/output/manim`으로 지정해두어서, 렌더링 결과가 자동으로 `shared/output/manim`에 쌓입니다. 새 씬은 `manim/scenes/`에 파일을 추가하면 됩니다.

## 두 렌더링 결과 합치기

각 엔진에서 클립을 렌더링한 뒤, `scripts/combine.ps1`로 순서대로 이어 붙입니다:

```powershell
pwsh scripts/combine.ps1 -Clips `
  "shared/output/manim/videos/example_scene/1080p60/Example.mp4", `
  "shared/output/motion-canvas/project.mp4" `
  -Out "shared/output/final.mp4"
```

내부적으로 `ffmpeg -f concat`을 사용하므로, 이어 붙이려는 클립들의 해상도/코덱을 맞춰두는 것을 권장합니다(다르면 먼저 `ffmpeg`로 리인코딩).

## 헬퍼 스크립트

- `scripts/render-motion-canvas.ps1` — Motion Canvas 편집기 실행
- `scripts/render-manim.ps1` — `manim/scenes` 안의 모든 씬을 렌더링
- `scripts/combine.ps1` — 렌더링된 클립들을 하나의 영상으로 합치기
