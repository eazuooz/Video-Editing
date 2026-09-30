# 게임을 베끼지 않고 배우는 법 — 로컬 검토 제작

사용자 승인: 미제작 재생목록 영상의 독립 대본·기존 목소리·Nimbus·원본 인트로와 회원 엔딩을 사용해 제작한다. 업로드는 영상 확인 때까지 보류한다. 영상 완료 후 코드·대본·자막·재빌드 기록을 커밋·푸시한다. MP4/WAV/BGM/미디어 압축은 Git에 넣지 않는다.

## 현재 제작 기준

- 6개 독립 대본 씬, 실제 게임/플레이테스트 60%와 흰 2.5D 설명40%. 인트로2초·회원 엔딩10초는 비중에서 제외.
- 매번 새 게임 선정 검토. 이번은 Super Meat Boy / Hollow Knight / Portal. 예전 Mario·Celeste 후보는 사용 이력 때문에 제외했다.
- 원본 고양이 로고와 회원 프로필·이름·배지12개 행을 그대로 보존. 정확한 엔딩 제목은 `멤버쉽가입 감사드립니다.`.
- Qwen3-TTS 1.7B 승인 기준 목소리, 6개 씬 연속 합성, 장면 간0.72초. v2의 마지막 씬 첫 시도는 반복 음성으로 거절하고 재합성했다. 최종 사용자 청취는 완료로 추정하지 않는다.
- boxed-white-forest-v1 한글 자막과 clean master, 단어 시각으로 정렬한 한·영 SRT. 자체 입력 HUD는 자막 위에 배치한다.

## 재제작 순서

저장한 원본 자산·개인 음성 기준·로컬 모델을 확보한 후 저장소 루트에서 실행한다. 다른 장기 GPU 작업을 중지하거나 같은 합성/렌더를 중복 실행하지 않는다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-project-narration.ps1 -Project deconstruct-analyze-rebuild
python qwen3-tts/review_project_narration.py --project deconstruct-analyze-rebuild --device cpu
node projects/deconstruct-analyze-rebuild/production/build-video.cjs prepare
python projects/deconstruct-analyze-rebuild/production/align-captions.py
node projects/deconstruct-analyze-rebuild/production/build-video.cjs mix
# Vite를 motion-canvas/에서 포트9210으로 실행한 상태에서
node projects/deconstruct-analyze-rebuild/production/render-reel.cjs
node projects/deconstruct-analyze-rebuild/production/build-video.cjs assemble
node projects/deconstruct-analyze-rebuild/production/caption-video.cjs
python projects/deconstruct-analyze-rebuild/production/verify-video.py
# 모든 최종 자막/장면 contact sheet를 실제 확인한 뒤 qa.json visualReview를 기록
node projects/deconstruct-analyze-rebuild/production/finalize.cjs
node scripts/collect-video-output.cjs deconstruct-analyze-rebuild
node scripts/build-rebuild-manifests.cjs deconstruct-analyze-rebuild
npm run media:check
npm run rebuild:check
```

음성을 다시 합성하면 길이가 바뀔 수 있다. prepare·단어 정렬·믹스·렌더·두 SRT 검수를 함께 다시 실행한다. 보관한 미디어가 없으면 외부 출처와 이용 조건을 다시 확인해 확보한다.

자체 테스트 캡처 스크립트는 현재 v3 폴더에 새 파일을 만들며 기존 파일을 덮어쓰지 않는다. final-v1은 `landing/retry/observe`의 보관된 v2 캡처와 `variants` v3 캡처를 사용한다. 모든 v2/v3 입력·충돌 로그와 소스 코드를 보존했다. 새 전체 캡처를 사용하는 재제작은 build-video.cjs의 own 경로와 로그 버전을 함께 변경하고 검수한다.

## 검토와 전달

`final-v1/qa.json`, `caption-layout-qa.json`, `caption-alignment.json`, 최종 contact sheets가 기계 검사와 화면 검수 증거다. 수집기는 최종4개 파일만 `output/deconstruct-analyze-rebuild/`에 복사하고 `output/index.html`을 갱신한다. 사용자 청취, 원래 Audio Library 파일, Team Meat 게시 정책, 외부 백업 검토는 해당 경고를 유지한다. 수집이나 Git 푸시가 YouTube 게시 승인을 뜻하지 않는다.
