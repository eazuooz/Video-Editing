# v6 전체 렌더 검토 — 2026-09-13

**청취 검토본 생성 완료. 게시용 완료는 아닙니다.** 12개 독립 씬, 1920×1080, 60fps, 63394프레임, 1056.566667초입니다.

- [전체 VS Code 호환 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z-vscode.mp4): H.264 + MP3.
- [전체 표준 MP4](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.mp4): H.264 + AAC.
- [한국어 SRT](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.ko.srt) · [영어 SRT](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.en.srt).
- [검수 JSON](../../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z-qa.json).

## 확인한 것

- 자료화면에서도 우리 내레이션이 0초부터 시작합니다. 원음은 낮추고 연속 Blue Dream을 함께 넣었습니다.
- 12개 자료화면 + 12개 설명 구간의 오디오 LUFS가 유한하고 무음이 아님을 검사했습니다. 배경 레이어도 별도 확인했습니다. 전체 믹스 -16.25 LUFS / -1.92 dBTP.
- 편집기 WAV의 실제 재생 시간 증가, 음소거 해제, 전체 타임라인 길이 일치를 24개 지점에서 확인했습니다.
- 24개 표본 화면을 2개 모음 이미지로 확인했습니다. 실제 코드/편집기/테트리스/플레이 테스트 → 흰색 연구 발표형 자체 설명 구성이 유지됐습니다. 화면 표본 검사는 전 프레임의 주관적인 시청 검수를 대신하지 않습니다.
- 표준 MP4의 AAC 패킷 SHA-256이 전체 믹스 M4A와 일치합니다. 표준본과 호환본 전체 디코딩 검사도 통과했습니다.
- 양 언어 253개 번호·타임코드가 같습니다. 승인 대본의 모든 내용, 두 줄 이하 자막, 겹침 없음, 영상 종료 이내를 검사했습니다.
- 영어는 11번의 장황한 번역 한 문단을 같은 의미로 간결하게 다듬고, 기존 타임코드의 표시 길이에 따라 단어를 재배분했습니다. 최대 읽기 분량은 43.7 → 27.9자/초로 줄었습니다. 모든 자막이 일정한 읽기 속도라는 뜻은 아닙니다.
- 이 영어 문구 개선은 영상 렌더 후 적용됐습니다. MP4와 한영 타임코드는 그대로이며, 렌더 당시 입력 해시는 기존 `.json`에 보존했습니다. 최신 SRT 해시와 이전 사본은 `-qa.json.captionTextRefinement`에 기록했습니다.

## 남은 확인

1. 전체 음성의 자연스러움·목소리/BGM 균형에 대한 사용자 청취 승인. [발음 확인 메모](v6-asr-notes.md).
2. Blue Dream의 실제 오디오 보관함 파일·사용 조건 확인. 현재는 공식 작곡가 채널 음원을 사용한 비공개 청취 검토본입니다. `previewUseOnly: true`, `publishReady: false`. [근거](blue-dream-creator-evidence.md).
3. 게시 조건 확보 및 청취 승인 후 최종 게시용 상태를 별도로 확정합니다. 현재 publish 검사는 미확인 음악 조건과 검토 믹스 상태 때문에 의도대로 실패합니다.

기존 v5 완성 검토 파일, FPS·점프 물리 프로젝트는 변경하지 않았습니다. 커밋·푸시·YouTube 업로드는 이 작업에 포함하지 않았습니다.
