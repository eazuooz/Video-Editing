# 다른 컴퓨터에서 작업 이어가기

2026-09-17 인계. Node.js 20 이상과 Git을 설치합니다. 영상 재편집/출력에는 FFmpeg도 필요합니다.
Git LFS는 사용하지 않습니다. 100MiB가 넘는 완성 MP4는 최대 80MiB gzip 조각으로 저장했으며,
복원 시 원본 크기·SHA-256을 검사합니다. 화질·음질은 바뀌지 않습니다.

## 처음 가져올 때

```powershell
git clone https://github.com/eazuooz/Video-Editing.git
cd Video-Editing
node scripts/restore-media.cjs
cd motion-canvas
npm ci
npm start -- --host 127.0.0.1 --port 9100
```

이미 복제한 폴더라면 로컬 작업을 먼저 보존하고 `git pull --ff-only` 후 복원 명령을 실행합니다.
복원 대상 파일이 이미 같은 내용이면 건너뜁니다. 다른 내용이면 덮어쓰지 않고 중단합니다.

- 현재 보상 디자인 영상: http://127.0.0.1:9100/visible-rewards-review.html
- Motion Canvas 편집기: http://127.0.0.1:9100/src/projects/visible-rewards/project
- 다른 프로젝트 목록: http://127.0.0.1:9100/
- 완성/검토 MP4: `shared/output/motion-canvas/`
- 한국어·영어 SRT: 각 `projects/<slug>/project.json`의 `paths.captionsKo`, `paths.captionsEn`
- 빌드 검사: `npm run build --prefix motion-canvas` (저장소 루트에서 실행)

전체 빌드는 등록된 모든 프로젝트의 자산을 사용합니다. 아래의 비공개 고전 삽화까지 별도 전달받은 뒤 실행하세요.
그림을 아직 옮기지 않아도 `visible-rewards` 편집·재생은 위 주소에서 가능하며,
소스 타입 검사는 `npx --prefix motion-canvas tsc --noEmit --project motion-canvas/tsconfig.json`으로 할 수 있습니다.

보상 영상만 복원하려면:

```powershell
node scripts/restore-media.cjs --project visible-rewards
```

## Git에 포함한 것 / 별도로 옮겨야 하는 것

포함: 프로젝트 대본·기획·출처·승인 상태, Motion Canvas/Manim 소스, 편집에 쓰는 게임 컷,
렌더된 TTS·자막·전체 믹스, 승인 음악, 완성 MP4의 무손실 압축본, Unity/Unreal 원본 프로젝트.

제외: Unity Library, Unreal DerivedDataCache/Intermediate/Saved, node_modules, Python 가상환경,
TTS 모델, 원본 게임 영상 다운로드 캐시, 재생성 가능한 렌더 조각, 비밀 키와 개인 음성 복제 원본.
기존 제외 정책을 유지했으며 로컬 원본을 삭제하지 않았습니다.

- 이미 만든 영상의 재생·Motion Canvas 편집에는 TTS 모델이나 개인 기준 음성이 필요 없습니다.
- 새 TTS를 만들려면 `shared/voice-reference/`를 **개인적으로 전달**하고, 해당 컴퓨터에
  Qwen3 모델·Python 환경을 별도 설치해야 합니다. 공개 Git에 기준 목소리나 토큰을 넣지 마세요.
- `choice-driven-classics`의 사용자 원본 JPG/PNG는 공개 재배포 승인이 없어 제외되어 있습니다.
  해당 프로젝트를 재렌더하려면 `motion-canvas/src/projects/choice-driven-classics/assets/`의
  제외된 이미지를 개인적으로 전달해야 합니다. 기존 BGM 검토 MP4는 별도 보존됩니다.
- 원본 게임 영상의 구간을 바꾸려면 프로젝트별 fetch 스크립트로 다시 확보합니다.
  현재 편집에 쓰는 잘린 클립과 최종 믹스는 포함되어 있으므로 보기 위해 재다운로드할 필요는 없습니다.
- `unity/`는 Unity Hub에서 프로젝트 추가: `6000.6.0f1`.
- `unreal/VideoEditing.uproject`는 Unreal Engine `5.6`으로 엽니다. 캐시는 엔진이 다시 만듭니다.

## 현재 수정 상태 — visible-rewards

2026-09-17 최종 **v3 / 6분 15.767초 / 1080p60**. 이번 전달에는 v2의 자료 교체·2.5D 개선과 v3의 전체화면·하단 설명 제거를 함께 포함합니다.
`git pull --ff-only` 후 보상 프로젝트 복원 명령을 실행하면 최신 최종 MP4와 기존 v1을 복원합니다. v2 MP4만 이 PC에 보존하며 별도로 배포하지 않습니다.

1. 설명 8장을 움직이는 2.5D 디오라마로 변경 완료.
2. 스타듀밸리 얼굴캠 없는 재사용 허용 영상으로 교체. 실제 2,000G 가방 구매/24칸 확장 확인.
3. 몬헌 와일즈 제작 메뉴·소재 보유량 + 사냥 예시 추가. 04:40.867부터 19.5초.
4. `shared/output/motion-canvas/visible-rewards-final.mp4` 생성. 전체화면, 하단 설명 없음. 22,546프레임, 전체 디코딩 및 마스터 AAC 일치 검사 통과.
5. 편집기는 `final-mix-v2.wav` 사용. A 내레이션·Wanderlust·작은 게임 원음 포함. 한영 SRT 각 94개 타이밍 유지.
6. 최종 영상과 같은 폴더에 `visible-rewards-final.ko.srt`, `visible-rewards-final.en.srt` 제공. 영상에 자막을 구워 넣지 않음.
7. `final-video-v3/manifest.json`의 2개 80MiB 이하 압축 조각에서 141,252,470바이트 원본을 무손실 복원. 새 PC에서 `node scripts/verify-visible-rewards-delivery.cjs`로 영상·자막 해시와 싱크 검사.
8. 노션 게임 디자인 기초의 [04. 게임 보상](https://app.notion.com/p/3de0b1ffa61e81f48cc4d3f4dce3b4d1), 원고 `docs/wiki/game-design-basics/04-rewards.md`, 캡처 5장도 보존. 유튜브 게시 주소가 확인되면 글 최상단의 대기 문구를 해당 영상 임베드로 교체.

승인된 **A 균형형 목소리 / Wanderlust — Scott Buckley**는 유지합니다.
별도 몬헌 새 장 대본은 미승인이라 새 TTS를 만들지 않았습니다. 기존 07장 대사에 자료화면을 넣었습니다.
새 내레이션이 필요하면 대본 수정 승인을 먼저 받고, 타이밍을 바꾸면 한영 SRT·편집기·최종 믹스를 함께 갱신합니다.
v1은 기존 압축본을 보존합니다. 최신 v3는 `shared/media-archives/visible-rewards/final-video-v3/`이며 복원 시 원본과 모든 조각의 SHA-256을 검사합니다.
기술 검사 완료와 전체 사람 청취 승인은 별개이며 `publishReady=false`입니다.
시작 전 `AGENTS.md`와 세 제작 기준 MD, 프로젝트 매니페스트를 읽습니다.
