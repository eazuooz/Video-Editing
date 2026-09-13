# 선택 BGM — Blue Dream / Cheel

- 선택일: 2026-09-06.
- 사용자 선택: **‘1번 블루드림’**.
- 곡명: Blue Dream.
- 아티스트: Cheel.
- [작곡가 미리듣기](https://www.youtube.com/watch?v=dOfp_DUdwF4).
- 적용 대상: `ai-era-cs-fundamentals` 한 편. 다른 프로젝트나 목소리 샘플의 승인을 의미하지 않습니다.

## 확인한 내용

공개 영상 메타데이터에서 `Cheel - Blue Dream (Original) - Free copyright music`, 게시자 `Cheel`, YouTube Audio Library 다운로드 안내를 확인했습니다. 이 설명만으로 개별 라이선스 유형·필수 크레딧을 단정하지 않습니다.

[YouTube 공식 안내](https://support.google.com/youtube/answer/3376882)에 따라 실제 오디오 보관함의 곡 행에서 라이선스 유형과 저작자 표시 필요 여부를 확인한 후 보관함 MP3를 받습니다. 보관함 제공곡과 다른 채널의 재업로드 파일을 같은 것으로 보증하지 않습니다.

초기에는 브라우저 연결이 없었고, 이후 2026-09-12 Computer Use 재시도에서는 브라우저의 현재 URL을 확인하지 못해 도구가 중단됐습니다. 오디오 보관함 파일은 확보하지 못했습니다. 음악을 임의로 대체하지 않으며, v6에서는 대본/TTS/원음 작업과 음악 확보를 분리해 진행합니다.

## 이어서 필요한 자료

1. [YouTube 오디오 보관함](https://www.youtube.com/audiolibrary)에서 `Blue Dream` / `Cheel` 검색.
2. 해당 곡의 MP3 다운로드 파일.
3. 곡 행의 라이선스 표시 화면 또는 표시 문구. CC 라이선스라면 복사 가능한 크레딧 전문도 함께 보관.

브라우저가 연결되면 직접 확인할 수 있고, 사용자가 파일과 라이선스 표시를 제공해도 계속할 수 있습니다. 확인 전에는 `license`, `attribution`을 미확정으로 유지합니다. 현재 `file`은 아래 공식 채널 출처의 청취 검토용 파일이며 오디오 보관함 다운로드 파일이 아닙니다.

## 2026-09-12 청취 검토 믹스

- 작곡가 Cheel의 위 공식 업로드에서 검토용 음원을 확보했습니다. 재업로드 채널을 사용하지 않았습니다.
- 파일: `shared/assets/music/artist-review/Blue-Dream-Cheel.mp3`.
- v6 WAV/M4A에는 Blue Dream이 전체 길이 연속으로 포함되어 있습니다.
- `licenseStatus: pending-audio-library-track-verification`, `previewUseOnly: true`: **게시 보류**.
- 파일 입수 경로와 제한: [공식 채널 근거](blue-dream-creator-evidence.md).

## 확정된 적용 방식

- Blue Dream 한 곡을 영상 처음부터 끝까지 연속 재생.
- 실제 예시 영상 원음은 제거하지 않고 함께 재생.
- v6 승인 목표: 내레이션 -16 LUFS (기존 후단 +1.8dB 유지) / 원음 -31 LUFS / BGM -28 LUFS.
- 원음이 있는 구간에만 BGM 추가 -3dB, 가벼운 내레이션 덕킹.
- 반복 연결은 1초 크로스페이드. 씬이 바뀔 때 음악을 다시 시작하지 않음.
- 현재 v3 개발 자료화면 12개 모두 원음이 있습니다. 과거 스톡 버전의 무음 씬 목록은 더 이상 적용하지 않습니다.
- v5 전체 TTS와 원음 MP4 검토본은 생성됐지만 Blue Dream은 미포함입니다.
- v6 대본은 2026-09-12 승인됐습니다. 자료화면에서도 우리 내레이션을 이어 가고 원음 목표를 -31 LUFS로 낮춥니다. BGM은 -28 LUFS 기준으로 계속 재생하며 내레이션 덕킹을 적용합니다. 전체 청취 승인은 별도입니다.
- v6 승인 대본 TTS와 검토용 음악을 섞어 편집기 WAV에 연결했습니다. MP4에는 동일 믹스의 AAC를 쓰고 VS Code 호환 영상에는 MP3를 씁니다. 게시용 권리 확인은 별도로 남아 있습니다.

출처 초안: `Music: Blue Dream — Cheel (YouTube Audio Library)`.
필수 크레딧 여부·문구 확인 전에는 이 초안을 라이선스 충족의 증거로 쓰지 않습니다.
