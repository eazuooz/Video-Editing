# 내레이션·애니메이션 검토 프리뷰 v1

전체 88페이지 본편이 아니라 **1·14·48쪽 대본 일부를 이어 붙인 약 57초 샘플**이다. 원본 디자인·목소리·선택적 애니메이션을 함께 확인하기 위한 제작 중간물이다.

- 1쪽: 원본 표지와 내레이션. 장식 애니메이션을 넣지 않는다.
- 14쪽: 원본 행렬·도식을 보존하고 Q/K/V를 설명할 때 해당 영역만 강조한다. 강조 시점은 받아쓰기의 단어 시각으로 맞춘다.
- 48쪽: 원본의 빈 도식 영역에 편집 가능한 도형·텍스트·화살표를 추가했다. 장면 특징과 카메라 레이를 별도 입력으로 연결한다.
- 1920×1080, 60fps. 기존 균형형 목소리. 사용자 선택에 따라 BGM은 없다.
- 자막은 흰 박스/검정 글자/초록 그림자, 중심 y=400. 긴 수식 설명의 가독성을 위해 이 프리뷰는 44px, 줄간격 58px로 조정했다. 두 줄 이하와 페이지 하단 분리를 확인한다.
- 화면 지시를 TTS에 읽히지 않으며, Q/K/V 등은 음성에서는 한국어 음가, 화면 자막에서는 기호로 표기한다.

## 열기

저장소의 `motion-canvas` 폴더에서:

```powershell
npm run start -- --host 127.0.0.1 --port 9210 --strictPort
```

프리뷰: <http://127.0.0.1:9210/renderformer-preview.html>

편집기: <http://127.0.0.1:9210/src/projects/renderformer-explained/preview/project>

프리뷰 화면에서 `소리 켜고 재생 / 정지`를 누른다. 로컬 PCM WAV가 연결되어 있으며 브라우저 자동재생 제한을 사용자의 클릭으로 해제한다.

## 산출물

- `renderformer-preview-v1-mastered.mp4`: 확인할 최신 검토 영상. 음성·한국어 박스 자막·애니메이션 포함. 최종 AAC 실측 -16.04 LUFS / -2.35 dBTP.
- `renderformer-preview-v1.mp4`: 최종 음량 정리 전 중간 렌더. 최신판은 위 mastered 파일이다.
- `renderformer-preview-v1.ko.srt`, `renderformer-preview-v1.en.srt`: 같은 타임코드의 발췌 자막. 본편 자막이 아니다.
- `asr-review.json`: 원 대본과 Whisper 받아쓰기 비교. ASR 검사는 사람의 청취 승인을 대신하지 않는다.
- `qa/report.json`: 3개 독립 씬, cue별 자막 여백, 편집기 오디오 재생 검사.
- `render-report.json`: 렌더 후 영상 길이·프레임·오디오·전체 디코딩 검사.

원본 TTS는 `audio/page01.wav`, `page14.wav`, `page48.wav`에 보존한다. 노멀라이즈한 파일과 0.35초 선행/0.8초 이상 후행 여백을 조립한 편집기 음성은 `motion-canvas/src/projects/renderformer-explained/preview/assets/preview-narration.wav`다. AAC는 같은 마스터에서 생성한다.

## 재현

```powershell
qwen3-tts/.venv/Scripts/python.exe projects/renderformer-explained/production/prepare_preview.py
python projects/renderformer-explained/production/build_motion_plan.py
```

그다음 `motion-canvas`에서:

```powershell
npm exec tsc -- --project tsconfig.renderformer.json
node scripts/render-renderformer-preview.cjs 9210 --qa-only
node scripts/render-renderformer-preview.cjs 9210 --mastered
```

렌더 명령은 이미 전달한 MP4를 덮어쓰지 않는다. 변경판은 새 버전으로 만든다. 전체 TTS와 본편 렌더는 이번 목소리 샘플 확인 후 진행한다. BGM 없음은 이미 승인되었다.
