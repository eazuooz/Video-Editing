# REA / Godot 분석 도구 점검

점검일: 2026-10-29 (Asia/Seoul). 대상 도구: 설치된 `rea-agents` 6.8.0. 이 문서는 **도구 소스·도움말 점검**이며 Buckshot Roulette 파일의 실제 분석 결과가 아니다. 게임 실행·추출·원본 변경은 이 점검에서 하지 않았다.

## 확인 결과

REA의 Godot 지원은 PCK의 정적 목록·바이트 위치·무결성·추출이다. 단독 PCK 및 EXE 끝의 정식 PCK 트레일러를 지원한다. 암호화되지 않은 PCK 형식 2/3/4를 지원하며 Godot나 Ghidra 실행이 필요하지 않다. 설치된 문서에는 **GDScript 역컴파일, Godot 리소스 디코딩, 복호화, 게임 실행을 제공하지 않는다**고 명시되어 있다. 따라서 이 도구의 목록만으로 탄환 순서, 아이템 규칙, 딜러 의사결정을 알아냈다고 주장하면 안 된다.

## 첫 실행 순서

저장 디렉터리를 먼저 만든 뒤 기존에 없는 evidence 파일명을 사용한다. `production/local/`은 Git 제외 대상이다. 아래 명령은 점검 중 실행하지 않은 권장 명령이다.

```powershell
$rea = 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/rea.ps1'
$install = 'D:/SteamLibrary/steamapps/common/Buckshot Roulette/Buckshot Roulette_windows'
$local = 'D:/Github/VideoEditing/projects/buckshot-roulette-reverse-engineering/production/local'

# 1. 설치 폴더와 제한된 헤더를 조사한다. 실제 런타임 실행은 하지 않는다.
& $rea inspect-desktop-application $install --detail summary --evidence_output "$local/desktop-evidence.json" --format json

# 2. 내장 PCK와 파일 목록/해시를 조사한다. 네이티브 디컴파일러를 열지 않는다.
& $rea inspect-artifact "$install/Buckshot Roulette.exe" --detail summary --evidence_output "$local/pck-evidence.json" --integrity-policy fail --format json

# 3. 필요한 경우에만 추출한다. CLI에는 출력 폴더나 파일 선택 인자가 없다.
# 새 시스템 임시폴더 rea-extracted-<UUID>가 자동 생성된다.
# & $rea extract-artifact "$install/Buckshot Roulette.exe" --integrity-policy fail --format json
```

`inspect-desktop-application`의 path는 파일이 아니라 설치 **디렉터리**다. 기본 관찰 한도는 20,000개 항목과 헤더 프로브 8,388,608바이트다. 한도 소진은 부분 범위로 남는다. `--detail summary`에는 `--evidence_output`이 필수이며 이미 있는 파일을 덮어쓰지 않는다. `--format json`은 공통 출력 옵션이다. `inspect-godot-pack`이라는 별도 명령은 없다.

## 결과에서 볼 항목

- 요약 반환: `summary`, `evidence_bundle.path`, `evidence_bundle.bytes`. 전체 Evidence는 저장 번들에서 확인한다.
- artifact inventory: `manifest`, `nodes`, `occurrences`, `edges`, `coverage`, `integrity_contradictions`, `limitations`.
- `manifest`: 원본 `root_sha256`, `root_format`, 노드·출현·연결 수.
- `occurrences`: `logical_path`, `artifact_id`, `source_path`, `source_location.offset/length`, `encrypted`, `hash_status`, `declared_integrity`, `format_metadata`.
- `nodes`: 관찰한 `sha256`, `size`, 실제 바이트 형식. 같은 `artifact_id`로 occurrence와 연결한다.
- PCK `format_metadata`: `format_version`, `engine_major/minor/patch`, `pack_start/end`, `embedded`, `pack_flags`, `file_base`, `directory_start`, `declared_file_count`, `directory_status`.
- 엔트리 `format_metadata`: 원래 `source_path`, `declared_offset`, `index`, `flags`, `md5_status`.

선언된 MD5와 실제 관찰한 SHA-256을 구분한다. 목록/페이지가 완전하다는 것과 소스 내용이 알려졌다는 것은 다르다. 암호화된 디렉터리·sparse bundle은 엔트리 범위가 unknown이며, 암호화된 멤버는 내용 해시가 알려지지 않을 수 있다. 빈 결과를 부재의 증거로 삼지 않는다.

## 제한과 다음 도구 선택

- 디렉터리 메타데이터는 64 MiB 예산을 가진다. 읽기/추출 확장 예산은 최소 256 MiB 또는 PCK 바이트 구간의 500배 중 큰 값이다. 엔트리 경로 별로 합산한다.
- 알 수 없는 pack/file flag, 잘못된 오프셋·경로·파일 크기는 실패하거나 unsupported로 남는다. 무결성 오류를 기본으로 무시하지 않는다.
- EXE 내장팩 탐지는 끝의 12바이트 트레일러와 그 위치가 가리키는 `GDPC` 헤더를 확인한다. 임의의 페이로드 전체 검색이나 게임 실행이 아니다.
- 목록에서 `.gd`가 실제 평문으로 확인되면 그 파일의 규칙을 로컬에서 읽고 플레이 결과로 대조할 수 있다. `.gdc`라면 REA 자체로 읽을 수 없으므로 실제 바이트코드 버전과 별도 역컴파일 도구의 지원을 확인해야 한다.
- 별도 후보인 [공식 GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp)는 내장 EXE/PCK에서 프로젝트·스크립트 복구, GDScript 역컴파일, 리소스 변환을 문서화한다. `--headless --recover=<EXE> --scripts-only --output=<ignored-local-dir>`가 스크립트 중심 후보이며, 원본에 실행하거나 덮어쓰는 명령이 아니다. **아직 설치·실행·이 게임 호환 검증은 하지 않았다.** 전체 아트 재사용보다 규칙 확인에 필요한 최소 스크립트를 로컬에서 확인하는 흐름을 권장한다.
- Ghidra는 실제 필요한 네이티브 코드 질문이 생겼을 때만 선택한다. Godot EXE의 엔진 네이티브 코드를 먼저 디컴파일하는 것만으로 게임별 GDScript 규칙을 얻는다고 보장하지 않는다.

## 검증 기록과 근거

실제 실행한 것은 아래 세 도움말뿐이다. 모두 exit code 0이었다.

```text
rea inspect-artifact --help
rea inspect-desktop-application --help
rea extract-artifact --help
```

설치 패키지 루트: `C:/Users/1/.codex/tools/rea-buckshot-20261028/node_modules/rea-agents`

| 근거 | 확인 내용 |
|---|---|
| `package.json` | 6.8.0, 공식 저장소 `morluto/rea` |
| `skills/reverse-engineer-anything/references/native-and-artifacts.md`, Godot PCK 항목 | 지원 범위와 GDScript 역컴파일 미지원 |
| `dist/cli/artifactCommands.js` | inspect/extract 명령 인자 |
| `dist/cli/analysisEvidenceDelivery.js` | summary/evidence 번들 동작 |
| `dist/artifacts/GodotPckLocation.js` | 단독/정식 EOF 내장팩 위치 확인 |
| `dist/artifacts/GodotPckArtifactReader.js` | 형식 2/3/4, 버전/파일 메타데이터, 암호화·플래그·크기 제한 |
| `dist/artifacts/inventory/reader.js` | 게임 장면/리소스/바이트코드/런타임 신호 미디코딩 |
| `dist/domain/artifactGraph.js` | inventory/node/occurrence 결과 스키마 |
| `dist/domain/artifactExpansionBudget.js` | 확장 예산 |
| `dist/application/artifacts/ArtifactExtractionDestination.js` | 새 임시 추출 폴더 |
| [GDRETools 공식 README](https://github.com/GDRETools/gdsdecomp) | 별도 복구·역컴파일 도구 후보와 CLI 인자 |

게임 파일 분석 결과·역컴파일 성공·플레이 규칙 확정·영상 녹화 완료를 이 문서의 상태로 승격하지 않는다.
