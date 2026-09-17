# 오디오 검토 상태

2026-09-13: **Childhood BGM 단독 검토본**. 전체 내레이션은 목소리 승인 후 연결한다. 현재 파일을 완성된 내레이션 믹스라고 부르지 않는다.

- 원음: 공식 Scott Buckley MP3, 사용 구간1.35–61.35초. 곡 시작의 약1.382초 무음을 줄여 도입부터 배경이 들어오도록 했다.
- 60초 연속 트랙. 씬 경계에서 끊거나 재시작하지 않는다.
- 목표 -28 LUFS. 실제 AAC 전구간 측정 **-27.5 LUFS / true peak -13.7 dBTP**, LRA2.8 LU.
- 시작0.8초, 마지막1.5초의 부드러운 페이드: 느린 종이/펜화 연출에 맞춘 프로젝트별 예외.
- 편집기: `assets/bgm-review-v2.wav`, PCM16 48kHz 스테레오.
- 영상용: `assets/bgm-review-v2.m4a`, AAC192kbps 48kHz 스테레오, 정확히60초.
- 음성 승인 후: 내레이션 -16 LUFS 기준, BGM 가벼운 사이드체인 덕킹. 덕킹·최종 합성은 아직 수행하지 않았다.
- 새로운 풀 믹스는 별도 파일에 생성하며 기존 TTS 원본을 덮지 않는다. 결과 MP4와 편집기 모두 같은 믹스로 교체한다.

전체 내레이션 승인/재생 검수 전 `publishReady=false` 유지.

Childhood BGM 포함 검토 MP4 생성 및 전체 디코딩 통과: `shared/output/motion-canvas/choice-driven-classics-BGM-ONLY-REVIEW-20260913T092359Z.mp4`. 편집기 WAV 실제 재생 시간 증가도 확인했다. 본편 TTS가 없는 상태임을 파일명/페이지/매니페스트에 명시했다.
