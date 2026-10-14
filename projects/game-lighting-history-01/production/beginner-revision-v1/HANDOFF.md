# 렌더링 역사 1편 — 초심자 보강본 이어가기

2026-10-14 재부팅 뒤 사용자가 다른 컴퓨터의 채팅에서 이어가도록 소스와 진행 기록의 커밋·푸시를 요청했다. 이 문서는 **초심자 보강 수정본 한 편**의 인수인계다. 다른 영상, 연구 작업, 자동 채팅을 시작하지 않는다.

## 새 채팅에 전달할 요청

> `origin/main`의 최신 소스를 받아 `projects/game-lighting-history-01/production/beginner-revision-v1/HANDOFF.md`와 해당 편 checkpoint를 읽고 초심자 보강본을 이어서 제작해 줘. 기존 3D 깊이감과 설명 순서는 유지한다. 전송 미디어의 경로·해시를 먼저 확인하고, 완료된 TTS·장면·믹스·ASR 01~03은 반복하지 마. 남은 믹스 ASR → 직접 대조 → 최종 clean/captioned 쌍 → 최종 자막/컷/동작 검수 → 4파일 수집 → 새 단일 비공개 업로드와 가능한 설정 → 선택 Git 전달까지 이 영상만 완료해 줘. 기존 `uT5FTLJx5_c`, `ZUrPmDV-bSQ`는 보존하고 공개·예약·삭제·다음 편은 하지 마.

## 현재 사실과 다음 시작점

- 원본 비공개: https://youtu.be/uT5FTLJx5_c . 이 링크는 **수정 전 Three.js 납품본**이다. 초심자 보강본은 아직 업로드하지 않았다.
- 현재 `project.json`의 납품 경로/게시 ID는 원본 납품 이력이다. `activeRevision` → `production/checkpoint.json#beginnerRevision` → 아래 `local/beginner-revision-v1/plan.json`을 따른다.
- 52개 교체 문단 + 6개 추가 안내 음성 제작·전체 텍스트 대조 완료. 92개 기존 문단의 승인 음성은 재사용한다. 새 설명 자산 30개(브라우저 27/Manim 3), 추가 실제 시연 21구간을 제작했다. `09b-p3` 새 자산은 사용하지 않고 실제 재질 내보내기 화면을 보존한다.
- 최종 입력 145768프레임, 1080p60, **2429.466667초**. 실제 87029 / 설명 58019프레임, 본편 145048, 60:40 오차 0.2프레임. 도입 2초와 회원 10초는 보존했다. 길이 목표에 맞춘 패딩이나 축약은 하지 않는다.
- KO 415 / EN 440큐, 150문단 그룹. 텍스트·문단 경계 검토 완료, **현재 최종 인코딩 픽셀은 아직 미검수**다.
- 현재 믹스 `final-mix-current.wav` SHA256 `63384b9ef1b89fef269b3d5bdc453645bda47e23ee68bdc391f90799386fc728`, 48kHz 116614400샘플, −16.56 LUFS / −2.35 dBTP. 정확한 AAC와 관련 해시는 `mix-execution.json`에 있다.
- 여섯 국소 음량 급락을 처리 음성에만 매끄러운 +4dB 보정으로 수리했다. 현재 발화 접합 플래그 0, 처리 때문에 생긴 실제 급락 0. 원래 PCM과 의도된 쉼은 보존했다. 사람 전체 청취·발음·표시된 원래 발화의 문맥 청취는 pending이다.
- 믹스 ASR은 재부팅 전 **01/02/03 세 장만 저장**됐다. 과거 PID74576 / 세션19729는 종료됐다. 이 번호로 기다리거나 종료하지 않는다. `mixed-asr/execution.json`의 현재 상태는 `interrupted-by-reboot`; 정상 종료 코드가 관찰된 것은 아니다.
- 남은 장: **04, 04f, 04t, 07, 08, 09, 09a, 09b, 10, 24**. 01~03 직접 비교 기록은 `mixed-asr-direct-progress.json`. 02의 색 칸/3칸, 법선/법성, 거울에 비칠 문장과 03의 둠/두 인식 차이를 숨기지 않았다. 필요한 완결 문맥만 현재 믹스로 추가 확인하며 기존 unmixed 승인으로 대체하지 않는다.
- `pair/concat-verification.json`은 세 종류 입력의 111프레임을 독립 추출 MD5와 대조한 성공 기록이다. 최종 visual/clean/captioned는 **아직 생성하지 않았다**. `encoded-review-request.json`의 1007프레임도 계획일 뿐 추출·검수 완료가 아니다.

## Git과 별도 미디어 전송

Git에는 편집 가능한 코드·KOEN 대사·현재 계획/자막·ASR 결과·검수 근거를 넣었다. MP4/WAV/M4A, 모델, QA 이미지와 전송 압축파일은 넣지 않는다. **다른 컴퓨터에서 pull만 해서는 완성된 미디어를 사용할 수 없다.**

`handoff-media.json`은 실제 존재를 확인한 **274파일, 6,067,314,273바이트**의 상대경로·SHA256 목록이다. 최종 입력 영상, 승인 PCM, 현재 믹스/진단 음성, 자막 폰트, 기존 썸네일을 포함한다. 원본 자료 전체나 반복 QA 이미지는 묶지 않았다. 전송 파일은 원래 컴퓨터의 다음 위치에 준비한다:

`output/handoff-game-lighting-history-01-beginner-v1/media.tar`

사용자의 추가 요청으로 [Google Drive 전용 폴더](https://drive.google.com/drive/folders/17WbjD1-NRp5gbKrp-38Klc9NYpEcfOMU)에 원본 `media.tar`를 브라우저로 업로드 중이다. **아직 업로드 완료를 확인하지 않았다.** `media-package-receipt.json#googleDrive`가 현재 상태이며 다른 컴퓨터 복원도 미확인이다. 연결 도구의 512MiB 제한과 분할 전송의 5분 시간 초과가 있어 원본 브라우저 전송을 유지한다. 폴더의 `unused-incomplete-attempt-media.tar.part013`은 실패한 분할 시도의 작은 잔여 조각이며 복원용이 아니다. 업로드 중인 원래 컴퓨터를 깨워 두고 Codex의 Drive 탭을 닫거나 새로고침하지 않는다. 자동 채팅/연구/제작 재시작은 하지 않았다.

Drive의 `media.tar`가 **6,067,906,560바이트로 완료**된 뒤 내려받는다. 같은 폴더에 업로드한 `README.md`, `transfer-manifest.json`, `restore-media.py`의 안내대로 원본 SHA256과 274파일을 검증할 수 있다. 또는 아래처럼 새 checkout의 루트에 상대경로를 유지하여 복원한다. 빈 미디어를 만들어 검사만 통과시키거나, 파일이 없다는 이유로 이미 완료된 TTS/렌더를 자동 재생성하지 않는다.

```powershell
# 새 컴퓨터의 저장소 루트. Python 3.12+ tarfile의 data 필터 사용.
python -c "import tarfile; tarfile.open(r'전송받은-media.tar').extractall('.', filter='data')"
python projects/game-lighting-history-01/production/beginner-revision-v1/transfer-media.py --verify
```

## 환경과 실행 순서

기존 실행기들은 저장소 루트를 자기 파일 위치에서 계산한다. `D:/Github/Video-Editing`에 설치할 필요는 없지만 저장소 내부 상대경로는 유지한다. Windows 폰트 `Arial`/`Malgun Gothic`, 현재 자막 폰트, Python의 `numpy/soundfile/psutil/av/torch/torchaudio/transformers/imageio-ffmpeg/Pillow`를 실제 확인한다. ASR 모델은 `qwen3-tts/models/whisper-large-v3-turbo`에 복원하거나 `ASR_MODEL_PATH`에 이미 확보한 동일 모델 디렉터리를 지정한다. 모델·가상환경은 전송 묶음에 포함되지 않는다. GPU 연구를 정지하거나 자동 복원하지 않는다. 이번 인수인계 작업은 연구를 정지시키지 않았다.

1. 현재 운영 규칙과 이 편의 권한을 읽는다. 공유 control의 selectedVideo가 다른 작업의 계층형 영상을 가리킨다고 그 작업을 덮어쓰지 않는다. 이 편의 명시적 수정·비공개 전달 권한은 checkpoint에 있다. 실제 CPU/GPU/명령줄을 확인한다.
2. 미디어 검증 후 아래 읽기 전용 검사로 완료 3장과 남은 10장을 확인한다. `--resume`은 같은 계획/믹스 해시, 이미 저장된 결과, 과거 PID 생성시각/명령줄을 검사하고 **없는 장만 처리**한다. 한 번만 실행한다. 현재 컴퓨터에서는 실행하지 않고 인수인계했다.

```powershell
python -X utf8 projects/game-lighting-history-01/production/beginner-revision-v1/review-mix.py --check-resume
python -X utf8 projects/game-lighting-history-01/production/beginner-revision-v1/review-mix.py --resume
```

3. 13장 전체 기대글/실제글을 직접 대조하고 모호한 부분만 독립 완결 문맥으로 해소한다. `mixed-asr-direct-review.json`에 실제 현재 mixSha256과 `allCurrentMixedTextsDirectlyCompared`, `contentCoverageApproved`를 근거가 있을 때만 기록한다. 사람 청취를 ASR로 대신했다고 기록하지 않는다.
4. `review-ledger.json#beginnerRevision.liveMotionPreviewProgress`의 실제 범위에서 계속한다. 브라우저 미리보기는 `preview-server.cjs`를 실제 생존 확인 후 필요시 다시 시작하고 UI는 CUA로 조작한다. 02-p4의 마지막/09-p9/09a-p5 등 남은 동작과 3 Manim의 동작 확인이 남아 있다. 정지판만으로 움직임 전체를 승인하지 않는다. `review-assets.html` 파일 URL은 보안 차단 이력이 있으므로 다른 경로로 우회하지 않는다.
5. `assemble-pair.py`를 한 번 실행한다. 입력·믹스 직접 검토 gate를 유지한다. `--visual-only`는 준비된 선택 기능이나 현재 실행/출력은 없다. FFmpeg는 `VIDEO_FFMPEG` 또는 기존 7.1/imageio 런타임을 사용하며, 다른 버전 사용 시 기존 정확 PTS/폰트 관련 성공을 무조건 재사용하지 않는다. 198개 노드의 완료 입력에서 합성하고 current AAC를 두 파일에 동일하게 넣는다. 새 두 전체 decode/145768 PTS·90000 timebase·음량·동일 AAC를 확인한다.
6. `extract-current-qa.py`로 현재 출력의 1007개 고유 프레임을 한 번 추출하고 415개 자막/모든 컷/추가 동작/접합을 직접 확인한다. 현재 `allFinalPixels`는 false다. 실패 시 해당 범위만 수리한다.
7. 검수 후에만 project의 현재 납품 경로와 captionAlignmentReview를 새 입력으로 등록하고 `node scripts/collect-video-output.cjs game-lighting-history-01`로 네 파일 수집. 기존 collector가 이전 output을 delivery-history로 보존한다. 아직 새 등록 스크립트는 완성되지 않았으므로 이전 register-delivery.py를 그대로 실행하지 않는다.
8. `publishing/upload-package-beginner-v1.json`과 `description-beginner.ko.txt/.en.txt`는 **prepared-only**다. 새 captioned 파일을 단일 비공개 업로드한 실제 ID로 설정을 저장/재열람한다. 기존 두 ID 삭제/예약/공개 변경 금지. 수동 KOEN/영문 정보/썸네일/정확 링크/0초 카드/마지막10초 엔딩/실제 검사 상태를 확인하고 선택 Git 전달 후 이 편에서 멈춘다.

## 보존해야 할 실패 이력과 미완료 항목

- `final-mix-local-corrected.*`는 192kHz에서 48kHz용 샘플 trim을 적용한 **607초 잘못된 출력**이다. 사용 금지. 이를 고친 것은 `finish-local-mix.py`와 `local-mix-tail-resume.json`; 현재 `final-mix-current.*`만 사용한다. 원래 peak-safe/초기 믹스도 현재 파일로 오인하지 않는다.
- 완료 TTS, 30개 설명, 21개 프레이밍, 3개 ASR 결과, 현재 믹스의 반복 실행 금지. prepared 파일을 완료로 승격하지 않는다.
- 사람 청취/발음, 공개 권리 최종 확인, 원래 Nimbus 파일, 기존 잘린 회원 핸들, 외부 백업/미디어 전송, 비공개 고정 댓글은 미완료 상태를 유지한다.
- Git 작업 시 현재 외부 index에 대량의 과거 staged 변경이 관찰됐다. 이 작업과 무관하며 초기화·폐기·일괄 add/commit 하지 않는다. 원격의 다른 컴퓨터 후속 커밋을 보존하고 isolated index와 명시 경로만 쓴다.
