# 완료 후 로컬 용량 정리

2026-09-17 사용자 요청: 불필요한 파일 삭제 및 최종 영상 위주 보관.

## 정리 결과

- 삭제 267개, **5,088,204,713바이트 (약 5.09GB / 4.74GiB)**.
- 다운로드 원본·후보·정규화 중간 컷 100개, 3,651,758,538바이트.
- 중복 전체 믹스/음악·게임 단독 WAV/M4A 10개, 597,075,514바이트.
- 재생성 가능한 화면 QA 캡처 98개, 164,824,227바이트.
- TTS 중간 청크 9개, 19,860,878바이트.
- 조립용 GAME/GRAPHICS 렌더 48개, 382,665,914바이트.
- 이전 영상 `visible-rewards.mp4`, `visible-rewards-v2.mp4` 2개, 272,019,642바이트.

상세: [삭제 목록·보존 해시](cleanup-20260917-232332.json).

## 보존

- `shared/output/motion-canvas/visible-rewards-final.mp4` 및 같은 폴더의 `.ko.srt`, `.en.srt`.
- 썸네일, 한국어/영어 제목과 설명 전문, 위키 문서·캡처, 기획·대본·출처 기록.
- 승인 TTS 원본, 현재 편집기 전체 믹스, 편집된 게임 클립, 제작 코드, 재생성 스크립트.
- 모든 Git 추적 파일과 Git 대용량 복원 압축본. 다른 프로젝트·모델·개인 기준 목소리는 건드리지 않음.
- 원본 라이선스 메타데이터 `.info.json`과 오디오/렌더 검증 JSON은 기존 로컬 경로에 보존.

삭제 전후 최종 전달 검사 및 영상·자막·현재 WAV·썸네일·한영 제목/설명 SHA-256 불변 확인.
원본 다운로드 없이 현재 Motion Canvas 편집/재생 가능. 원본 구간을 다시 자르려면 fetch 단계부터 실행.

## 복구와 주의

휴지통으로 이동한 것이 아니라 실제 디스크 공간 확보를 위해 파일을 영구 삭제했다.
캐시는 출처 기록/스크립트로 다시 다운로드하거나 렌더해야 하며, 원본의 온라인 제공 여부까지 보장할 수는 없다.
v1 완성 MP4는 기존 Git 압축본에서 복원할 수 있다. **v2 완성 MP4의 별도 무손실 백업은 없으며**, 최신 v3를 보존했다.
최신 v3 압축본은 `shared/media-archives/visible-rewards/final-video-v3/`에 있다.

추가 작업 후 같은 임시 파일이 다시 생긴 경우에만 아래 스크립트로 점검한다.

```powershell
# 목록/용량 점검만: 기본 동작은 삭제하지 않음
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean-visible-rewards-cache.ps1
# 실제 정리: 무시된 캐시/구버전 출력만. Git 추적 파일·링크 경로는 거절
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/clean-visible-rewards-cache.ps1 -Apply
```

이번 요청에서는 커밋·푸시나 Git 이력 축소를 실행하지 않았다.
