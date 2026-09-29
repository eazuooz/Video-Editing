# 미디어는 외부 보관, 제작 설계는 Git

2026-09-29 사용자 승인: 모든 영상·음성·BGM과 압축/분할 미디어를 최신 파일뿐 아니라 공개 main의 과거 이력에서도 제거합니다. 실제 로컬 파일은 삭제하지 않습니다. 이미지, 폰트, 코드, 프로젝트 설정, 대본, 자막, 출처/라이선스, 편집 기록은 기존 정책대로 보존합니다.

## 프로젝트별 재제작 파일

- 전체 목록: `projects/rebuild-index.json`
- 프로젝트마다 `projects/<slug>/rebuild.json`
- 제거 목록과 이전 Git blob 식별자: `docs/media-removal-inventory.json` (바이너리 백업 아님)

각 JSON에는 원래 프로젝트 설정, 대본의 씬 수, 실제 편집 레코드, 원본 위치·컷 구간·출처, 타이밍 자료, 음량/BGM 승인, 자막 위치/큐 수/해시, 편집 가능한 렌더 소스, 제작 스크립트 경로가 들어갑니다. 레코드 수는 서로 다른 자료의 행 수이며, 타임라인과 컷 목록이 중복되므로 최종 영상의 컷 수와 혼동하지 않습니다. `purpose`가 supporting인 자료는 과거 버전일 수 있습니다. 선택한 현재 자료와 `projectSettings.paths`부터 읽으세요.

자료마다 시간 기준이 다릅니다. `startFrame`은 프레임, `in`/`rawStart`/`fileStart`는 원본 또는 부분 다운로드의 위치일 수 있습니다. 원래 값을 그대로 보존하고 제작 스크립트에서 해석합니다. 기록이 없는 값은 추측하지 않으며 `rebuild.gaps`에 한계를 표시합니다.

```powershell
# 새 프로젝트 생성/납품 수집 시 자동 갱신. 편집 후 수동 갱신도 가능.
node scripts/build-rebuild-manifests.cjs
node scripts/build-rebuild-manifests.cjs visible-rewards
npm run rebuild:check
npm run media:check
```

## 다른 컴퓨터에서

1. 이력 정리 이후 저장소를 새 폴더에 clone합니다. 옛 checkout에서 강제 pull/merge하지 마세요. 개인 작업을 먼저 별도 보관합니다.
2. 프로젝트 `rebuild.json`과 제작 기준을 읽고 Node/Python/FFmpeg 및 해당 엔진 환경을 설치합니다.
3. 개인 외장 저장소/클라우드에서 원본 미디어를 JSON의 동일 경로로 가져옵니다. 별도 백업 위치는 아직 지정되어 있지 않습니다. 없으면 출처·권리를 확인하여 원본을 다시 확보합니다. 링크가 없거나 삭제된 자료는 수동 확보가 필요합니다.
4. 개인 목소리 샘플·TTS 모델·회원 원본 이미지를 별도 준비합니다. 없는 회원 이미지/뱃지를 새로 만들어 대체하지 않습니다.
5. 해당 프로젝트의 제작 스크립트/README를 확인하고 클립 준비 → TTS → 믹스 → 렌더 → 자막 검사 순서로 실행합니다. 여러 버전의 스크립트를 전부 실행하지 마세요.
6. 최종 검사 후 `node scripts/collect-video-output.cjs <slug>`로 로컬 `output/`에 모읍니다.

JSON만으로 소실된 영상/음성 자체를 되살릴 수는 없습니다. 특히 TTS 재생성은 동일 바이트/길이를 보장하지 않습니다. 재합성하면 전체 씬 타이밍·KO/EN SRT·믹스를 함께 검수/갱신합니다. 이전 영상과 정확히 같아야 한다면 원본 음성과 영상을 외부에 보관하세요. 사용 권리나 게시 승인도 JSON 생성으로 새로 부여되지 않습니다.

`shared/media-archives/**/manifest.json`은 기존 외부 백업 조각의 해시/경로를 확인하는 기록입니다. 압축 조각은 더 이상 Git에 없습니다. 별도로 조각을 가져온 경우에만 `node scripts/restore-media.cjs --project <slug>`로 복원할 수 있습니다.

## 커밋 전

`npm run rebuild:manifests` → `npm run rebuild:check` → `npm run media:check`를 실행합니다. `.gitignore`는 기존 추적 파일이나 `git add -f`를 차단하지 못하므로 검사도 필요합니다. 확장자만 바꾸거나 Git LFS, ZIP/분할 압축으로 우회 업로드하지 않습니다.

## 이력 정리의 범위

GitHub main에서 도달 가능한 커밋에서 미디어 경로를 제거합니다. 커밋 ID가 변경됩니다. 로컬 복구용 bundle/백업 참조는 공개하지 않습니다. GitHub의 옛 커밋 URL, 캐시, fork, 다른 사람의 clone까지 즉시 삭제되는 것은 아니며, 서버 용량 회수 시점도 GitHub에 달려 있습니다. 민감 자료의 완전 삭제가 필요하면 별도로 GitHub 지원 절차를 확인해야 합니다.
