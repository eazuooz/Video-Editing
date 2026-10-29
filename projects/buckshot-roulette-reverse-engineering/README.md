# REA와 AI로 만드는 게임 기반 프로토타입

소유한 설치본에서 확인한 규칙을 별도로 설명하고, 독립적으로 작성한 코드와 새 외형으로 작은 플레이 실험을 만드는 프로젝트입니다. `prototype/`은 원작 실행 파일·복원 스크립트·원작 모델을 불러오지 않습니다. 원작 관찰 자료와 분석 원문은 Git에서 제외한 `production/local/`, `captures/`에 구분해 둡니다.

## v4 수정 · 전체 제작 흐름부터 소개

사용자 요청에 따라 **기존 게임 분석 → 규칙·리소스 구조 파악 → 새 코드·새 외형 제작 → 엔진에서 실행**을 중심 주제로 잡았다. 원작과 자체 프로토타입을 먼저 비교하고 REA(Reverse Engineer Anything), AI 에이전트, MCP의 역할을 설명한 뒤 실제 제작 사례로 이어진다.

실제 사용한 경로는 **REA 6.8.0 CLI → 읽을 수 있는 GDScript 분석 → AI와 독립 구현·Blender Python 모델 → Godot 4.7.2**다. Ghidra와 Tripo MCP, Unity·Unreal은 가능한 도구 선택지로 소개하며 이번에 실행한 것으로 표시하지 않는다. 분석 결과 도표는 실제 도구 UI 녹화가 아니다. 시간 단축 수치는 측정하지 않았다.

새 도입·설명·마무리 다섯 문단만 같은 참조 목소리로 생성하고 본문 열네 문단의 PCM 및 기존 컷은 보존한다. 계획은 `planning/revision-v4-workflow.json`, 현재 완료 상태와 검수 근거는 `production/checkpoint.json`을 따른다. 이전 v3는 보존한다.

v4 출력은 **6분 51.966667초 · 24,718프레임 · 1920×1080/60fps**다. 자막/무자막 MP4와 한국어115·영어135구절 SRT가 `output/buckshot-roulette-reverse-engineering-v4`에 있다. 두 영상의 전 구간 디코딩과 동일 음성 검사를 통과했고, 음량은 −17.1LUFS/−1.8dBTP다. 32개 컷과115개 자막에서 추출한189프레임 전부 및 주요 FHD/375px 화면을 직접 확인했다. 원작/자체 구현의 좌우 비교, REA 도구 역할, 선택 가능한 도구와 이번 실제 경로가 구분된다. 최종 상태는 현재 마스터 해시의 `production/final-review-v4.json`을 따른다. 사용자의 전체 시청·청취는 대기이며, 발음 확인 후보는 검수 페이지의 청취 클립에 모아 둔다.

## 이전 v3 결과 · 2026-10-29

[로컬 영상 검수 페이지](D:/Github/VideoEditing/output/buckshot-roulette-reverse-engineering/index.html) · [전체 자막 영상](D:/Github/VideoEditing/output/buckshot-roulette-reverse-engineering/buckshot-roulette-reverse-engineering.captioned.mp4) · [시제품 실행 스크립트](D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/launch-prototype.ps1)

v3 완성 파일은 이전 검수본으로 `output/buckshot-roulette-reverse-engineering-v3`에 보존합니다. 전체 길이는 **5분 43.083333초 · 20,585프레임 · 1920×1080/60fps**이며, 기존 2초 브랜딩과 10초 회원 안내를 포함합니다. 당시 최종 음량은 −17.0 LUFS, 최대 피크는 −1.8 dBTP입니다. 95개 자막과 32개 컷을 포함한173프레임 및 주요 FHD/375px 화면을 확인했습니다. 당시 검수 범위는 `production/final-review-v3.json`에 보존했습니다.

| 확인 대상 | 실제 결과 | 근거 |
|---|---|---|
| 독립 제작 모델 | 테이블·분절 로봇·총·탄환 2종·도구 5종, 총 10개 GLB | `prototype/assets/provenance.json`, Blender 생성 코드와 독립 편집용 `.blend` |
| 규칙 검사 | 374개 통과 | `prototype/tests/test_rules.gd`, `production/local/test-evidence/` |
| 메인 씬 통합 검사 | 32개 통과 | `production/local/test-evidence/main-integration-audit.json` |
| 짧은 실제 시연 촬영 | 1920×1080/60fps, 1,990프레임, 33.166667초 | `captures/prototype-demo-fhd.avi`, `production/local/test-evidence/prototype-demo-fhd-capture.json` |
| 다섯 실험의 실제 촬영 | 1920×1080/60fps, 7,271프레임, 121.183333초; 실행 중 검증 26개 통과 | `production/local/documentary-capture/all-v1.avi`, `all-v1-events.json`, `all-v1-qa.json` |
| 대표 합성 화면 | 원작 대상 선택·자체 구현의 차례 전환·탄환 큐를 실제 자막과 함께 FHD/375px로 확인 | `production/local/documentary-capture/representative-caption-preflight/receipt.json` |

모델 생성, 실제 Godot 실행 영상, 규칙 검사는 각각 다른 근거입니다. 새 모델이 있다는 사실만으로 실제 실행이나 원작과의 완전한 일치를 주장하지 않으며, 위 검사는 독립 구현의 해당 조건을 확인한 범위입니다. 최종 영상 전 구간 검수와 사용자 확인 상태는 `production/checkpoint.json` 및 최종 검수 기록을 따릅니다.

## 실행

현재 컴퓨터의 Godot 4.7.2에서 에셋 가져오기와 실제 GPU 실행·촬영을 확인했습니다. 실행 스크립트는 PowerShell 7(`pwsh`)을 사용합니다. 아래 명령은 어느 작업 폴더에서 실행해도 프로젝트 경로를 스크립트 위치에서 찾습니다.

```powershell
& 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/launch-prototype.ps1'
```

Godot 설치 위치가 다르면 `-GodotExecutable 'C:/path/to/Godot.exe'`를 지정합니다. 다른 컴퓨터에 소스를 옮겼다면 먼저 Godot에서 `prototype/project.godot`을 열어 GLB 에셋을 가져옵니다. 실행 스크립트는 프로그램을 설치하거나 전역 설정·원작 설치본을 변경하지 않습니다. 로그는 프로젝트의 `production/local/prototype-runtime/`에 기록하며, Godot의 일반 런타임·가져오기 캐시는 별도로 생성될 수 있습니다.

| 조작 | 동작 |
|---|---|
| `1` / `2` | 자신 / 딜러를 대상으로 사격 |
| `Q` | 돋보기: 다음 탄환 확인 |
| `W` | 배출 캔: 다음 탄환을 피해 없이 소비 |
| `E` | 톱: 다음 사격의 실탄 피해를 2로 변경 |
| `T` | 수갑: 딜러의 다음 차례 한 번을 건너뛰기 |
| `Y` | 회복 팩: 생명력 1 회복, 최대치 제한 |
| `R` | 진행 중인 동작이 끝난 뒤 새 게임 |
| `F2` | 규칙 근거 화면 열기 / 닫기 |

동일한 버튼을 마우스로 눌러도 됩니다. 애니메이션 중에는 새 동작과 재시작을 받지 않습니다. 고정 시연은 실행 명령에 `-Demo`를 붙입니다. 고정 시연 동안 직접 조작은 차단되고 마지막 근거 화면 뒤에 자동 종료됩니다.

## 구현 범위

- 2명, 생명력 3, 장전마다 실탄 2발·공포탄 2발인 작은 기본 규칙 실험입니다. 탄환 순서는 장전 때 섞으며, 일반 플레이는 매번 다른 시드를 사용합니다.
- 플레이어는 다섯 종류 아이템을 게임 시작 때 하나씩 받습니다. 이 시제품의 딜러는 **사격 대상만 선택하고 아이템은 사용하지 않습니다**. 원작의 아이템 배분·모든 AI 정책·캠페인·특수 라운드·멀티플레이를 재현한 완성품은 아닙니다.
- 일반 사격에서 자신에게 공포탄을 쏘면 차례가 유지됩니다. 수갑에 의한 상대 차례 건너뛰기는 별도 상태입니다. 모든 탄환을 소비하면 플레이어 차례로 새 탄환 묶음을 시작합니다.
- 일반 모드 딜러는 확인하지 않은 첫 탄환을 몰래 읽지 않고 무작위로 대상을 선택합니다. 알려진 탄환이나 마지막 한 발은 확인 가능한 정보로 판단합니다. 규칙 모듈의 확률 모드는 별도 시험용이며 현재 UI의 일반 모드와 구분됩니다.
- 온라인 연결, 저장, Steam 업적·순위표 기능은 없습니다. 화면은 새 실험 장면이며 원작 플레이 녹화로 분류하지 않습니다.

## 1080p60 시연 녹화

**다른 화면을 녹화 중일 때 실행하지 않습니다.** 이 명령은 GPU 렌더링 창을 띄웁니다. 준비된 명령만 확인하려면 `-DryRun`을 사용합니다.

```powershell
& 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/capture-prototype.ps1' -DryRun
& 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/capture-prototype.ps1'
```

기본 출력은 `captures/prototype-demo.avi`이며, 프로젝트의 창 크기 재정의까지 1920×1080으로 맞추고 60fps 고정 영화 시간을 사용합니다. GUI 실행 파일의 종료를 실제로 기다린 다음 ffprobe로 결과 해상도·프레임률을 검사합니다. ffprobe 위치가 다른 컴퓨터에서는 `-FfprobeExecutable`을 지정합니다. `--headless`나 빠른 시간 배율을 사용하지 않습니다. 현재 시연은 돋보기 → 자기 대상 공포탄 → 톱 → 상대 대상 실탄 → 딜러 사격 → 마지막 탄환 배출 → 근거 화면 순서이고 약 33초 뒤 스스로 종료합니다. 실제 촬영한 `captures/prototype-demo-fhd.avi`에서 FHD60·1,990프레임·33.166667초를 확인했습니다. `--quit-after 5400`은 완료되지 않는 경우를 위한 90초 상한이며, 정상 종료 길이를 늘리지 않습니다. 실행마다 실제 이벤트 시각과 파일 해시를 `production/local/test-evidence/`에 기록합니다.

기존 결과가 있으면 덮어쓰지 않습니다. `-OutputName 'prototype-demo-v2.avi'`로 새 이름을 주거나, 같은 결과를 교체하려는 경우에만 `-Overwrite`를 지정합니다. AVI는 중간 결과입니다. 스크립트가 실제 해상도·프레임률 검사에 통과한 뒤에도 음향·화면을 확인한 다음 최종 영상으로 편집합니다. 준비·단위 테스트·정상 프로세스 종료를 영상 품질 승인으로 간주하지 않습니다.

## 재현 가능한 검사

Godot 에셋 가져오기를 마친 후 아래 두 검사를 실행합니다. 결과 로그·JSON은 Git에서 제외한 `production/local/test-evidence/`에 둡니다.

```powershell
$godotExecutable = 'C:/Program Files (x86)/Steam/steamapps/common/Godot Engine/godot.windows.opt.tools.64.exe'
$prototypePath = 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/prototype'
& $godotExecutable --headless --path $prototypePath --script res://tests/test_rules.gd
& $godotExecutable --headless --path $prototypePath --script res://tests/test_integration.gd
```

규칙 검사는 탄환·피해·턴·아이템·정보 접근을 확인했고 374개를 통과했습니다. 통합 검사는 실제 메인 씬을 불러와 입력 차단, 아이템 소비, 애니메이션 완료, 턴 설명, 승패, 재시작 등 32개를 통과했습니다. 통합 검사는 빠른 시간 배율을 사용하는 headless 검사이므로 화면이나 음질을 검수한 결과는 아닙니다. 별도의 정상 속도 GPU 촬영은 위 표의 실제 영상과 이벤트 기록으로 확인합니다. 세부 근거는 `planning/mechanics-findings.json`과 `production/local/test-evidence/main-integration-audit.json`에 있습니다.
