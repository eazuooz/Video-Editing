# 미디어 보관·선택 Git 전달

현재 운영은 [통합 제작 규칙](VIDEO_WORKFLOW.md)을 따른다. 미디어를 보존하면서 승인된 제작 설계·대본·자막·코드·근거만 전달한다.

- 영상·내레이션·게임소리·BGM·압축/분할/LFS 미디어와 다운로드 원본info/연구 전체자막은 Git에 추가하지 않는다. 로컬 원본은 삭제하지 않는다.
- 새 JPG/PNG/WebP/GIF/BMP/TIFF는 기본 local-only. 추출프레임/연락판/렌더시퀀스/자막오버레이/반복QA 이미지는 생성경로·PTS·검수결과·SHA만 기록한다.
- 원본 로고/회원/씬 필수자산, 전달 썸네일, 최소 게시/권리증거만 직접 필요성을 검토해 `shared/git-essential-images.json`의 exactpath/purpose/reason/reviewedAt/SHA256과 파일별 ignore 예외를 추가한다. 폴더 예외·force-add 금지. 기존 모든 이미지가 필수라는 뜻은 아니다.
- 해당 편 완료 후 명시 경로만 선택해 일반 commit/push한다. 공유checkout에서는 실제HEAD에서 임시index를 만들고 최종 staged blob·경로와 외부index bytes/entries를 대조한다. 다른 작업의 staged/working파일을 변경·혼합하지 않는다. force-push/이력 재작성/변경 폐기 금지.
- `node scripts/media-policy.cjs`와 `node scripts/build-rebuild-manifests.cjs <slug> --check` 등 변경 범위의 필수 검사를 실행한다. 전체 index lock/다른 미완료 프로젝트 실패를 무시해 전체통과라 하지 않는다. 명령·범위·한계를 기록하고 자신의 manifest만 수정한다.
- 실제 commit/push/remote SHA를 확인해 증거를 남긴다. 미래 자신의 SHA를 예상해 문서에 쓰지 않는다. 같은 완료 전달을 매 턴 다시커밋/푸시하거나 증거의 증거를 무한히 커밋하지 않는다.

## 재현과 외부 보관

`projects/<slug>/rebuild.json`은 현재 설정·대본·편집·원본위치/컷·타이밍·믹스·자막해시·렌더 소스의 재현 목록이다. `projects/rebuild-index.json`은 공유 전체 목록이며 동시 작업 중 함부로 재작성하지 않는다. record 수는 최종 컷 수가 아닐 수 있고 supporting 항목은 역사 자료다. 현재 매니페스트가 고른 입력부터 읽는다.

`node scripts/collect-video-output.cjs <slug>`로 clean/captioned/KO/EN과 output index를 수집한다. 출력폴더는 Git 제외, 준비된 중간파일을 납품본에 섞지 않는다. 원본을 이동/삭제하지 않고 납품해시와 실제 미완료 항목을 유지한다.

다른 컴퓨터에서는 외부에 보관된 미디어·목소리 레퍼런스·회원 원본을 실제 경로와 해시로 복원한 뒤 현재 제작 실행기를 사용한다. JSON만으로 소실된 미디어를 복원할 수 없고 TTS 재합성도 동일바이트/길이를 보장하지 않는다. 백업이 미확인이라면 pending이다. 과거 `shared/media-archives/**/manifest.json`과 restore 도구는 실제 외부 조각이 있을 때만 사용한다.

2026-09-29의 미디어 이력 제거는 완료/과거 작업 기록이며 새 자동 이력 재작성 명령이 아니다. 과거 원문은 [보관본](history/video-policy-before-20261013-consolidation/docs/MEDIA_STORAGE.md)에 있다.
