# RenderFormer — 음성 전용 믹스

- 승인: 기존 균형형 Qwen3-TTS 1.7B 사용자 목소리. BGM은 사용자 요청으로 **없음**.
- 88페이지 본편: 158,925프레임 / 60fps = **2,648.75초 (44:08.75)**.
- 페이지 앞 0.35초, 뒤 약 0.8초의 읽기 여유. 전체 페이지 길이는 프레임 경계에 맞춤.
- 입력 원본: `shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1/chunks/`.
- 22쪽은 첫 문장 누락 의심으로 전체 페이지를 다시 합성. v1을 보존하고 `qwen3-1.7b-balanced-v2-repair/`에 별도 기록.
- 페이지 음량 정규화 및 최종 2-pass 마스터링: -16 LUFS / -2 dBTP 목표.
- v1 AAC 실측: **-16.05 LUFS / -1.53 dBTP**. AAC 인코딩 후 true peak가 PCM보다 소폭 높아짐. 이 수치는 v2의 최종 측정값이 아님.
- 22쪽 교체 후 v2 AAC 실측: **-16.05 LUFS / -1.52 dBTP**, LRA 3.7. 22쪽 원본 take는 24.16초이고 속도 0.973539배로 페이지 길이에 맞춤. 다른 페이지 시작은 불변.
- 본편 음성: `production/body-review/narration-mastered.wav` 및 `.m4a`.
- 편집기: `motion-canvas/src/projects/renderformer-explained/full/narrated/narration.wav`에 동일 PCM 마스터 연결.
- 자막판은 무자막판의 AAC 스트림을 그대로 복사한다. `media-validation.json`에서 두 파일의 오디오 해시를 비교한다.
- 원음·게임 소리·음악 추가 없음. 이번 프로젝트는 사용자 PDF 설명 강의로 외부 영상 슬롯을 사용하지 않는다.
- 마지막 10초는 회원 원본 이미지 확보 후 별도 추가 예정. 음악·추가 내레이션을 임의로 넣지 않는다.
- 전체 사람 청취 승인은 아직 받지 않았으므로 `publishReady: false`를 유지한다.
