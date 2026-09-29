# 다른 컴퓨터에서 작업 이어가기

2026-09-29 변경: Git에는 소스·대본·자막·제작 JSON만 보관하고, 영상·음성·BGM·압축 미디어는 별도로 전달합니다. 과거 이력을 정리했으므로 기존 clone을 merge/pull로 연결하지 말고 개인 변경을 보관한 뒤 새 폴더에 clone하세요.

```powershell
git clone https://github.com/eazuooz/Video-Editing.git Video-Editing-clean
cd Video-Editing-clean
npm ci --prefix motion-canvas
```

1. `projects/rebuild-index.json`에서 프로젝트를 고릅니다.
2. `projects/<slug>/rebuild.json`의 원본 경로, 선택한 타임라인/컷, 대본, 스타일, 음량, 제작 스크립트를 확인합니다.
3. 개인 백업에서 원본 영상·음성·승인 음악과 필요한 비공개 이미지·기준 음성을 동일 경로로 옮깁니다. 파일이 없으면 출처/권리 문서를 확인하여 다시 확보하거나 생성합니다.
4. Python/FFmpeg 및 프로젝트가 사용하는 TTS/Manim 환경을 설치하고 해당 제작 스크립트의 사용법대로 렌더합니다. 최종 미디어가 없으면 편집기에서도 음성/영상이 자동 복구되지 않습니다.
5. KO/EN SRT와 영상 타이밍을 검수하고 `node scripts/collect-video-output.cjs <slug>`로 결과를 모읍니다. 사용자는 `output/index.html`에서 확인합니다.

```powershell
# 필요한 자산을 옮긴 뒤 편집기 실행
npm start -- --host 127.0.0.1 --port 9100
# 최종 전달 후 메타데이터/추적 정책 검사
npm run rebuild:manifests
npm run rebuild:check
npm run media:check
```

Motion Canvas: http://127.0.0.1:9100/ . 전체 빌드는 등록된 모든 프로젝트의 자산을 요구할 수 있습니다. 소스만 clone한 상태의 전체 빌드 성공을 보장하지 않습니다.

기존 `shared/media-archives/**/manifest.json`은 남아 있지만 압축 조각은 Git에서 제거되었습니다. 조각을 개인 백업에서 옮긴 경우에만 `node scripts/restore-media.cjs --project <slug>`로 해시 검증 복원할 수 있습니다. 이전의 “clone만 하면 완성 영상을 복원” 안내는 폐기합니다.

Unity는 `unity/` 폴더, Unreal은 `unreal/VideoEditing.uproject`를 엽니다. 엔진 버전은 각 설정 파일을 확인하며 캐시는 새 컴퓨터에서 생성합니다.

추가 조건과 이력 정리 한계는 [미디어 보관/재제작](MEDIA_STORAGE.md), 제작 검수는 [워크플로](VIDEO_WORKFLOW.md)를 따릅니다. Git에 없는 원본은 JSON만으로 되살릴 수 없으므로 개인 백업이 중요합니다.
