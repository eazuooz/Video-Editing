# 첫 장면 검토본 — 전체 영상 아님

- `small-window-voice-preview-v1.mp4`: 1920×1080, 60fps, 30.75초.
- 실제 게임 20.9167초 / 설명 9.8333초 = 68.02%. 정지·반복·슬로다운 없이 원본 속도.
- 30.24초 Qwen3 1.7B 사용자 음성 기반 TTS. Whisper 받아쓰기에서 6문장 누락 없이 일치 확인. 목소리/속도/감정의 사람 청취 승인은 대기.
- Discovery 연속 BGM, 원음 -23 / BGM -28 / TTS -16 LUFS 정규화 시작점, 사이드체인 덕킹 적용.
- 생성 믹스 측정: -18.36 LUFS, -3.23 dBTP (PCM 측정; 최종 AAC는 별도 검사).
- MP4 AAC 측정: -18.40 LUFS, -3.32 dBTP. 전체 디코딩·1,845프레임·TypeScript 검사 통과. 실제 게임/도식 렌더 스틸 확인, 렌더 오류 0건.
- 현재 자막/회원 엔딩 없음. 전체 본편은 음성 샘플 확인 후 제작한다.
- 프로젝트 전체와 별도로 보존한 승인용 버전이며 `output/` 최종 모음에는 넣지 않는다.

## 자료 출처

Forza Horizon 5 © Microsoft Corporation. This commentary preview was created under Microsoft's Game Content Usage Rules using assets from Forza Horizon 5 and is not endorsed by or affiliated with Microsoft.
https://www.xbox.com/en-US/developers/rules

Gameplay — No Copyright Gameplay: https://www.youtube.com/watch?v=ZnCxVxfv3MM
사용 구간: 원본 00:30.000–00:50.917. 업로더는 해설·편집을 더한 재사용을 허용하며 무편집 무료자료 재배포 채널 사용은 금지한다.
주행/다른 차량/코너가 보이는 추적 시점이다. 운전석 비교나 FOV 실측의 증거로 사용하지 않는다.
게임 브랜드·라디오·제3자 음악 등은 업로더 허용과 별도이며, 원음의 게시용 검토가 끝나지 않았다. 게시 준비 완료가 아니다.

'Discovery' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au
https://www.scottbuckley.com.au/library/discovery/
https://creativecommons.org/licenses/by/4.0/
음악 발췌·음량 조정·페이드·덕킹 적용. 본편 설명란에도 출처를 유지한다.
