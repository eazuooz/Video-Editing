# 오디오 상태

현재: **전체 TTS + 작은 원음 + 연속 Discovery 믹스와 MP4 완성. 기술 검수 통과. 게시 권리·전체 사람 청취 승인 대기.**

## 전체 믹스 (2026-09-18)

- 결과: `review/astra-simple-showcase-v2-narrated-review.mp4` / 262.5초 / 1920×1080, 60fps / 71,958,574바이트
- 내레이션: Qwen3 1.7B 장면 단위, 승인된 본인 기준 음성. 기차 승인 샘플 SHA-256 일치, 속도·피치 변경 없음
- 각 장면의 정규화 내레이션 실측 -16.05~-16.13 LUFS. 원본 `.wav`와 영상 배치용 `.timeline.wav`는 보존
- 원음은 원본 파일의 사용 구간에서 새로 추출, 경쟁 발화/음악을 고려해 -31 LUFS 적용. 이미 섞인 MP4의 오디오를 재사용하지 않음
- 06번은 오디오 트랙 없음, 07·08번은 사실상 무음. 해당 구간은 원음을 만들어 넣지 않고 Discovery만 연속 유지
- Discovery 실측 -27.99 LUFS. 원음과 겹치면 0.45초 램프로 추가 -3dB. 235.3초 곡의 끝과 시작을 1초 크로스페이드해 전체 262.5초에 맞춤
- 승인 샘플과 같은 버스 덕킹: threshold 0.08, ratio 2.2, attack 15ms, release 280ms. amix normalize=0
- 최종 AAC 192kbps / 48kHz stereo: **-17.41 LUFS, true peak -1.55 dBTP, LRA 14.70 LU**
- 10씬 × 발화/후반부의 20개 레이어 표본에서 BGM 확인. 발화 구간 음성 확인
- 전체 디코딩 성공. AAC 편집기 파일과 MP4 오디오 패킷 SHA-256 일치. PCM 편집기 트랙은 같은 AAC를 디코딩한 파일
- 한글·영어 SRT 각40개, 번호/시각 동일, 겹침 없음, 마지막 자막 261.080초
- 10개 WAV 전부 ASR 검토. 05 ‘탈것’ 재생성 후 정상 인식, 10 종결부 재생성 후 감쇠 검사 통과. 최종 차이는 여덟/8, 네/4 숫자 표기만
- 근거: `review/audio-v2/mix-report.json`, `review/technical-check-v2.json`, `review/qa-v2-narrated/report.json`
- 사람의 전체 음성/영상 검수는 남아 있음. 자동 분석을 실제 청취 승인으로 표시하지 않음

## 기차 장면 샘플 (2026-09-18)

- 파일: `review/astra-v2-voice-sample.mp4` (프로젝트 폴더 기준)
- H.264, 1920×1080, 60fps, 31초 / AAC 192kbps, 48kHz 스테레오
- 사용자 기준 음성 Qwen3 1.7B TTS 12.880042초, 속도·피치 변경 없음
- Whisper 받아쓰기 대조에서 내용 누락·반복 없음. 이것은 사람의 청취 승인을 대체하지 않음
- 선택곡: Discovery — Scott Buckley. 2026-09-18 사용자 승인, CC BY 4.0 크레딧 기록
- 내레이션 -16 LUFS 정규화 후 남는 구간 무음 패딩. 원음은 검토 버스(0.15 gain)에 추가 0.5 gain
- BGM -28 LUFS + 원음 겹침 -3dB. 사이드체인 threshold 0.08, ratio 2.2, attack 15ms, release 280ms
- amix normalize=0, 리미터 0.82. AAC 측정: 전체 -22.12 LUFS / true peak -4.50 dBTP / LRA 12 LU. 전체 측정에는 대사 종료 후 약18초의 배경음 구간이 포함됨
- 사용자가 이 샘플의 목소리·속도를 승인한 후 위 전체 믹스를 제작함

## 구버전 화면본과 구분

- 원본 영상의 오디오 유무를 ffprobe로 확인하고, 있는 트랙은 검토본에서 0.15 linear gain으로 낮춰 연결한다. 이것은 LUFS 정규화된 최종 믹스가 아니다.
- `astra-picture-review-v2.mp4`는 보존한 화면 검토본으로, 설명 화면이 무음이다. 새 전체 음성 파일과 혼동하지 않는다.
- 원본 음악·발화의 재사용 권리는 미확인. 게시본에 자동 포함하지 않는다.
- 승인된 Discovery를 처음부터 끝까지 연속 배치. 원음과 함께 나올 때 추가 -3dB. 곡 반복은 1초 크로스페이드.
- 최종 목표: 사용자 내레이션 -16 LUFS, 효과음 중심 원음 -23 LUFS; 외국어 해설이 경쟁하면 -31 LUFS 검토, BGM -28 LUFS. 사이드체인/피크 검사는 공통 기준 적용.
- 편집기는 `final-mix.wav`, 최종 MP4는 동일 믹스 AAC 연결 완료. `editorReviewAudio` 경로는 구버전 원음 전용 기록이다.
