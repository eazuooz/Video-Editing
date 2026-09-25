# 트랜스포머부터 RenderFormer까지

사용자의 `RenderFormer_v0.4_한글본문.pdf`를 88페이지 모두 원래 순서로 설명하는 장편 영상 프로젝트다. **2026-09-25 승인 프리뷰를 바탕으로 44:08.75 전체 본편을 제작했다.** 로컬 Qwen3 1.7B의 전체 한국어 음성과 KO/EN 자막 533큐를 사용한다. 원본 PDF는 보존하고 영상용 오버레이에서 설명·도표를 보완했다. 사용자 선택대로 BGM은 없다. 멤버십 원본 이미지와 사람의 전체 청취 승인은 별도로 필요하다.

**[전체 본편 재생](http://127.0.0.1:9210/renderformer-full.html)**에서 페이지 이동과 자막판/무자막판 선택이 가능하다. 최초 승인 자료는 [57초 프리뷰](preview/renderformer-preview-v1-mastered.mp4)로 보존한다. [페이지별 애니메이션 계획](planning/animation-plan.md).

## 먼저 볼 파일

- [88페이지 전체 대본](script/review.ko.md): 각 페이지의 화면 지시와 실제 내레이션을 분리했다.
- [내용 보완·교체표](planning/corrections.ko.md): 원문 오류, 영상용 대체 문구, 확인 근거를 정리했다.
- [페이지별 제작표](planning/page-plan.md): 페이지/씬 대응과 예상 분량을 빠르게 확인한다.
- [제작 계획](planning/production-plan.md): 챕터 구성, 화면·음성·자막 처리와 다음 단계.
- [논문·공식 코드 출처](sources/SOURCES.md): 원 논문과 공개 코드 설명을 구분했다.
- [프로젝트 설정](project.json): 이번 요청에 맞춘 기본 규칙의 예외와 승인 상태.

현재 대본은 88씬, 내레이션 518문장이다. TTS 이후 확정한 본편은 **44분 8.75초**, 60fps 기준 158,925프레임이다. 긴 문장을 나눈 한국어/영어 자막은 각각 533큐다. 최초 분량 추정 53~68분은 더 이상 실제 영상 길이로 사용하지 않는다.

## 원본 보존

원본 위치: `D:/OneDrive/문서/RenderFormer_v0.4_한글본문.pdf`

- 원본은 수정하거나 저장소에 복사하지 않았다.
- 원본의 흰색·남색 발표 디자인, 그림, 페이지 순서를 유지한다. 다른 프로젝트의 디자인으로 재구성하지 않는다.
- 잘못된 수식·설명은 별도 영상용 사본에서 교체한다. 바른 음성을 틀린 슬라이드 위에 그냥 얹지 않는다.
- 같은 제목의 연속 페이지도 전부 사용한다. 48쪽 빈 도식과 88쪽 미완성 한계 설명은 기존 페이지 안에서 보완한다.
- 외부 영상 슬롯을 추가하는 일반 템플릿과 달리 이번 영상은 PDF 전체 설명에 집중한다.

## 대본 갱신

편집 원본은 `script/review.ko.md`다. 내레이션 JSON을 직접 수정하면 다음 컴파일 때 덮어써진다.

저장소 루트에서:

```powershell
python projects/renderformer-explained/production/build_script.py
```

이 명령은 원문 PDF의 SHA-256과 1~88쪽 순서를 검사하고, 내레이션 JSON·페이지별 제작표·분량 추정 보고서를 생성한다. TTS를 실행하거나 영상을 렌더하는 명령이 아니다. 원문 PDF가 다른 컴퓨터에 있다면 동일한 원문 파일을 준비하고 `project.json`의 `sourceDocument.path`를 변경해야 한다.

## 현재 제작과 확인 방법

- [전체 88페이지 화면 검수](http://127.0.0.1:9210/renderformer-layout.html): 페이지 선택 가능. **무음 시각 검수 전용**이며 본편 완료물로 사용하지 않는다.
- `production/slide-overlays.json`: 원본 960×540 좌표의 편집 가능한 대체 문구·마스크. Motion Canvas가 원본 페이지 위에서 렌더한다.
- `motion-canvas/src/projects/renderformer-explained/full/layout/`: 원본 페이지당 독립 씬 88개.
- `production/layout-qa/`: 전체 페이지 캡처와 줄넘침·씬 수·프레임 수 검사 결과.
- `production/full-narration.log`: 현재 전체 TTS 작업 로그.
- `shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1/production-progress.json`: 생성 진행률. `completedPages`는 저장된 페이지 수이며 최종 ASR·청취 합격 수가 아니다.
- `production/finish-body.log`: 전체 TTS 후 받아쓰기·마스터링·검토 렌더의 로그.

```powershell
# 진행 상태
Get-Content -Encoding UTF8 shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1/production-progress.json

# 중단 후 재개 (먼저 production.lock의 PID가 살아 있는지 확인, 중복 실행 금지)
qwen3-tts/.venv/Scripts/python.exe -X utf8 -u projects/renderformer-explained/production/render_full_narration.py

# 전체 생성 후: ASR, 한국어 SRT, 실측 타이밍, 무BGM 음성 마스터
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/renderformer-explained/production/prepare_full.py

# 개발 서버 9210이 실행 중일 때 무자막/한국어 자막 검토본 렌더
node motion-canvas/scripts/render-renderformer-body.cjs
```

2026-09-25 후반 작업: 22쪽 발화 재생성본과 실측 자막을 적용했다면 위 원본 조립을 무심코 다시 실행하지 않는다. 재개에는 `production/finalize_body.py`를 사용한다. `body-review/page22-repair.json`이 완료 조건이며, v1 음성과 이전 타이밍은 `before-page22-repair` 파일로 보존한다.

## 전체 본편 재생

- 브라우저: http://127.0.0.1:9210/renderformer-full.html
- Motion Canvas 자막판: http://127.0.0.1:9210/src/projects/renderformer-explained/full/narrated/project
- 무자막 MP4: `production/body-review/renderformer-clean-review.mp4`
- 한국어 박스 자막 MP4: `production/body-review/renderformer-captioned-review.mp4`
- 한영 자막: `production/body-review/renderformer.ko.srt`, `production/body-review/renderformer.en.srt`
- 영어 번역 원본: `script/captions.en.tsv`. `production/build_english_subtitles.py`가 실제 KO 타이밍과 533개 키를 검사한다.
- 기술 용어 표시 기준: [논문 용어 자막 표기](script/CAPTION_TERMINOLOGY.md). `SwiGLU`, `GELU`, `ReLU`, `FFN` 등은 영문으로 표시하고, TTS 발화·타임코드는 유지한다. 수정 원본은 `script/caption-terms.ko.json`이다.
- 출력 상태: `production/body-review/render-progress.json`. `body-review-rendered` 및 `media-validation.json`으로 전체 디코딩 완료 여부를 확인한다. 생성 중에는 MP4가 아직 완성되지 않았을 수 있다.

자막판은 Motion Canvas의 `LectureCaption`과 **동일한 Canvas 그리기 코드**로 만든 투명 자막을 무자막 마스터에 합성한다. 편집기에는 88개 독립 씬과 편집 가능한 자막이 그대로 남는다. 1~2쪽 기존 Motion Canvas 자막 렌더와 비교한 SSIM은 0.999457이었다. 음성은 AAC 패킷 복사해 두 버전에서 동일하게 유지한다.

```powershell
# 루트에서, 22쪽 보완 적용 완료 후 자막판·전체 미디어 검사까지 재개
python projects/renderformer-explained/production/finalize_body.py
```

전체 생성 뒤 자동 이어가는 작업은 `production/finish_body_review.py`다. 실패하면 로그와 중간 WAV를 남긴다. 기존 음성은 입력 지문이 같을 때만 재사용한다. 자동 산출물은 `production/body-review/` 아래의 **검토본**이며 다음 확인 전에는 게시본으로 올리지 않는다.

## 최종 완료 전에 남는 검수

1. 전체 음성의 숫자·고유명사·문장 끝을 실제로 청취한다. 88페이지 ASR 및 별도 구간 재인식은 완료했고, 검토 내역은 `production/body-review/ASR_REVIEW_NOTES.md`에 남겼다.
2. 한영 SRT 533큐는 번역 완료. 음성 재생성 시 두 언어 타이밍을 함께 갱신한다.
3. 원본 사진·이름·배지가 함께 있는 회원 목록 이미지 파일을 확보해 마지막 10초를 붙인다. 현재 원본 파일 미확보로 이름만 있는 구버전 엔딩은 사용하지 않는다.
4. 본편 + 10초 엔딩의 최종 길이, 한영 자막, 편집기 음성, 자막 안전 여백을 함께 검수한다.
5. 최종 전체 청취 승인 후에만 `publishReady`를 변경한다.

원본 회원 이미지가 없는 동안은 **엔딩 미포함 본편 검토본**이다. 전체 본편과 최종 게시 승인 상태를 구분한다. 기존 사진·배지가 없는 이름만의 엔딩을 붙이지 않는다.
